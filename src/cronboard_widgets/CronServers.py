from textual.app import ComposeResult
from textual.containers import Horizontal, Grid
from textual.widget import Widget
from textual.widgets import Label, Tree
from cronboard_widgets.CronTree import CronTree
from textual.binding import Binding
from cronboard_widgets.CronSSHModal import CronSSHModal
from cronboard_widgets.CronTable import CronTable
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation
import paramiko
from pathlib import Path
import tomllib
import tomlkit
from cronboard_encryption.CronEncrypt import decrypt_password, encrypt_password


class CronServers(Widget):
    BINDINGS = [
        Binding("a", "add_server", "Add Server"),
        Binding("D", "delete_server", "Delete Server"),
        Binding("c", "connect_server", "Connect"),
        Binding("d", "disconnect_server", "Disconnect Server"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.servers_path = Path.home() / ".config/cronboard/servers.toml"
        self.servers = self.load_servers()
        self.current_ssh_client = None
        self.current_cron_table = None

    def compose(self) -> ComposeResult:
        servers_tree = CronTree("Servers", id="servers-tree")
        servers_tree.root.expand()
        self.content_area = Label(
            "Use 'a' on the tree view to add a server", id="disconnected"
        )
        yield Grid(
            Horizontal(
                servers_tree,
                self.content_area,
            ),
            id="servers-grid",
        )

    def on_mount(self) -> None:
        servers_tree = self.query_one("#servers-tree", Tree)
        for server_id, server_info in self.servers.items():
            servers_tree.root.add_leaf(f"{server_info['name']}", server_id)
        servers_tree.refresh()

    def action_connect_server(self) -> None:
        servers_tree = self.query_one("#servers-tree", Tree)
        if servers_tree.cursor_node and servers_tree.cursor_node != servers_tree.root:
            server_id = servers_tree.cursor_node.data
            server_info = self.servers.get(server_id)
            if server_info:
                self.connect_to_server(server_info)

    def connect_to_server(self, server_info) -> None:
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)

            host = server_info["host"]
            port = server_info["port"]
            username = server_info["username"]
            password = server_info["password"]

            if server_info["ssh_key"]:
                ssh_client.connect(hostname=host, port=port, username=username)
            else:
                ssh_client.connect(
                    hostname=host, port=port, username=username, password=password
                )

            if self.current_ssh_client:
                try:
                    self.current_ssh_client.close()
                except:
                    pass

            self.current_ssh_client = ssh_client
            self.show_cron_table_for_server(ssh_client, server_info)

            server_info["connected"] = True
            self.save_servers()

            self.notify(f"Connected to {server_info['name']}")

        except paramiko.AuthenticationException:
            self.notify("Authentication failed. Please check your credentials.")
        except Exception as e:
            self.notify(f"Connection error: {e}")

    def show_cron_table_for_server(self, ssh_client, server_info) -> None:
        if self.current_cron_table:
            self.current_cron_table.ssh_client = ssh_client
            self.current_cron_table.remote = True
            self.current_cron_table.action_refresh()
            self.notify(f"Switched to {server_info['name']}")
            return

        self.current_cron_table = CronTable(
            remote=True, ssh_client=ssh_client, id="remote-cron-table"
        )

        container = self.query_one("#servers-grid", Grid)
        horizontal = container.query_one(Horizontal)

        if self.content_area and self.content_area != self.current_cron_table:
            self.content_area.remove()

        horizontal.mount(self.current_cron_table)
        self.content_area = self.current_cron_table

    def show_disconnected_message(self) -> None:
        if self.current_cron_table:
            self.current_cron_table.remove()
            self.current_cron_table = None

        disconnected_label = Label(
            "Use 'a' on the tree view to add a server", id="disconnected"
        )

        container = self.query_one("#servers-grid", Grid)
        horizontal = container.query_one(Horizontal)

        if self.content_area:
            self.content_area.remove()

        horizontal.mount(disconnected_label)
        self.content_area = disconnected_label

    def action_disconnect_server(self) -> None:
        if self.current_ssh_client:
            try:
                self.current_ssh_client.close()
            except:
                pass
            self.current_ssh_client = None

        self.show_disconnected_message()

        for server_info in self.servers.values():
            server_info["connected"] = False
            self.notify(f"Disconnected from server {server_info['name']}")

        self.save_servers()

    def load_servers(self) -> dict:
        print(f"🔍 Looking for servers file: {self.servers_path}")
        print(f"📁 File exists: {self.servers_path.exists()}")

        if self.servers_path.exists():
            try:
                with self.servers_path.open("rb") as f:
                    loaded_servers = tomllib.load(f)
                print(f"📊 Loaded {len(loaded_servers)} servers from file")

                # ✅ Fix: Correct key name
                for server_id, server_info in loaded_servers.items():
                    print(f"🔧 Processing server: {server_id}")
                    if "encrypted_password" in server_info:
                        encrypted_password = server_info.pop(
                            "encrypted_password"
                        )  # ✅ Fixed
                        if encrypted_password:
                            try:
                                server_info["password"] = decrypt_password(
                                    encrypted_password
                                )
                                print(
                                    f"🔓 Successfully decrypted password for {server_id}"
                                )
                            except Exception as e:
                                print(
                                    f"❌ Failed to decrypt password for {server_id}: {e}"
                                )
                                server_info["password"] = None
                        else:
                            server_info["password"] = None
                    elif "password" not in server_info:
                        server_info["password"] = None

                print(f"✅ Successfully loaded {len(loaded_servers)} servers")
                return loaded_servers
            except Exception as e:
                print(f"❌ Warning: Failed to load servers: {e}")
        else:
            print("📝 No servers file found, starting with empty list")
        return {}

    def save_servers(self) -> None:
        print(f"💾 Saving {len(self.servers)} servers to {self.servers_path}")
        try:
            self.servers_path.parent.mkdir(parents=True, exist_ok=True)
            toml_safe_servers = {}
            for server_id, server_info in self.servers.items():
                print(f"📝 Processing server for save: {server_id}")
                encrypted_password = ""
                if server_info.get("password"):  # ✅ Added .get() for safety
                    encrypted_password = encrypt_password(server_info["password"])
                    print(f"🔒 Encrypted password for {server_id}")

                toml_safe_servers[server_id] = {
                    "name": server_info["name"],
                    "host": server_info["host"],
                    "port": server_info["port"],
                    "username": server_info["username"],
                    "encrypted_password": encrypted_password,
                    "ssh_key": server_info["ssh_key"],
                    "connected": server_info["connected"],
                }

            with self.servers_path.open("w", encoding="utf-8") as f:
                tomlkit.dump(toml_safe_servers, f)
            print(f"✅ Successfully saved {len(toml_safe_servers)} servers")
        except Exception as e:
            print(f"❌ Error: Failed to save servers: {e}")

    def action_add_server(self) -> None:
        def on_server_added(result):
            if result:
                name = result.get("username") + "@" + result.get("hostname")
                host = result.get("hostname")
                port = result.get("port")
                username = result.get("username")
                password = result.get("password") if result.get("password") else None
                self.add_server_to_tree(name, host, port, username, password)

        cron_ssh_modal = CronSSHModal()
        self.app.push_screen(cron_ssh_modal, on_server_added)

    def add_server_to_tree(
        self, name: str, host: str, port: str, username: str, password: str | None
    ) -> None:
        servers_tree = self.query_one("#servers-tree", Tree)
        server_id = f"{username}@{host}"
        if server_id not in self.servers:
            self.servers[server_id] = {
                "name": name,
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "ssh_key": True if not password else False,
                "connected": False,
            }
            servers_tree.root.add_leaf(f"{name}", server_id)
            servers_tree.refresh()
            self.save_servers()

    def action_delete_server(self) -> None:
        servers_tree = self.query_one("#servers-tree", Tree)
        if not (
            servers_tree.cursor_node and servers_tree.cursor_node != servers_tree.root
        ):
            self.notify("No server selected to delete.")
            return

        server_id = servers_tree.cursor_node.data
        server_info = self.servers.get(server_id)

        if not server_info:
            self.notify("Selected server not found.")
            return

        def on_delete_confirmed(confirmed: bool) -> None:
            if confirmed:
                if self.current_ssh_client:
                    self.action_disconnect_server()

                del self.servers[server_id]
                servers_tree.cursor_node.remove()
                self.save_servers()
                self.notify(f"Deleted server {server_info['name']}")
            else:
                self.notify("Server deletion cancelled.")

        confirmation_modal = CronDeleteConfirmation(
            message=f"Are you sure you want to delete the server '{server_info['name']}' ?",
        )
        self.app.push_screen(confirmation_modal, on_delete_confirmed)
