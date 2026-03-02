import base64
import hashlib
import socket
from pathlib import Path

import paramiko
import tomllib
import tomlkit
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal
from textual.widget import Widget
from textual.widgets import Label, Tree

from cronboard_encryption.CronEncrypt import decrypt_password, encrypt_password
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation
from cronboard_widgets.CronHostKeyChanged import CronHostKeyChanged
from cronboard_widgets.CronHostKeyConfirm import CronHostKeyConfirm
from cronboard_widgets.CronSSHModal import CronSSHModal
from cronboard_widgets.CronTable import CronTable
from cronboard_widgets.CronTree import CronTree

CRONBOARD_KNOWN_HOSTS = Path.home() / ".config/cronboard/known_hosts"


class CronServers(Widget):
    BINDINGS = [
        Binding("a", "add_server", "Add Server"),
        Binding("D", "delete_server", "Delete Server"),
        Binding("c", "connect_server", "Connect"),
        Binding("d", "disconnect_server", "Disconnect Server"),
    ]

    def __init__(self, config: dict | None = None) -> None:
        super().__init__()
        self.config = config or {}
        self.servers_path = Path.home() / ".config/cronboard/servers.toml"
        self.known_hosts_path = CRONBOARD_KNOWN_HOSTS
        self.servers = self.load_servers()
        self.current_ssh_client = None
        self.current_cron_table = None

    # ------------------------------------------------------------------ #
    # Host-key helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def format_fingerprint(key: paramiko.PKey) -> str:
        """Return a human-readable SHA-256 fingerprint for *key*."""
        digest = hashlib.sha256(key.asbytes()).digest()
        b64 = base64.b64encode(digest).decode("ascii").rstrip("=")
        return f"SHA256:{b64}"

    def _load_or_init_host_keys(self) -> paramiko.HostKeys:
        """Load Cronboard's known_hosts file, creating it first if absent."""
        self.known_hosts_path.parent.mkdir(parents=True, exist_ok=True)
        if self.known_hosts_path.exists():
            return paramiko.HostKeys(str(self.known_hosts_path))
        host_keys = paramiko.HostKeys()
        host_keys.save(str(self.known_hosts_path))
        return host_keys

    def _build_ssh_client(self) -> paramiko.SSHClient:
        """Return a configured SSHClient with the correct host-key policy."""
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        if self.known_hosts_path.exists():
            client.load_host_keys(str(self.known_hosts_path))

        permissive = (
            self.config.get("ssh", {}).get("host_key_policy", "strict") == "permissive"
        )
        if permissive:
            client.set_missing_host_key_policy(paramiko.WarningPolicy)
        else:
            client.set_missing_host_key_policy(paramiko.RejectPolicy)
        return client

    # ------------------------------------------------------------------ #
    # Compose / mount
    # ------------------------------------------------------------------ #

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
            servers_tree.root.add_leaf(
                f"{server_info['name']}: {server_info.get('crontab_user', '')}",
                server_id,
            )
        servers_tree.refresh()

    # ------------------------------------------------------------------ #
    # Connect / disconnect
    # ------------------------------------------------------------------ #

    def action_connect_server(self) -> None:
        servers_tree = self.query_one("#servers-tree", Tree)
        if servers_tree.cursor_node and servers_tree.cursor_node != servers_tree.root:
            server_id = servers_tree.cursor_node.data
            server_info = self.servers.get(server_id)
            if server_info:
                self.connect_to_server(server_info)

    def connect_to_server(self, server_info: dict) -> None:
        try:
            ssh_client = self._build_ssh_client()

            host = server_info["host"]
            port = int(server_info["port"])
            username = server_info["username"]
            password = server_info["password"]
            crontab_user = server_info.get("crontab_user")

            if server_info["ssh_key"]:
                ssh_client.connect(hostname=host, port=port, username=username)
            else:
                ssh_client.connect(
                    hostname=host, port=port, username=username, password=password
                )

            if self.current_ssh_client:
                try:
                    self.current_ssh_client.close()
                except Exception:
                    pass

            self.current_ssh_client = ssh_client
            self.show_cron_table_for_server(ssh_client, server_info, crontab_user)

            server_info["connected"] = True
            self.save_servers()
            self.notify(f"Connected to {server_info['name']}")

        except paramiko.BadHostKeyException as exc:
            self._handle_bad_host_key(server_info, exc)
        except paramiko.SSHException as exc:
            if "not found in known_hosts" in str(exc):
                self._handle_unknown_host(server_info)
            else:
                self.notify(f"Connection error: {exc}")
        except paramiko.AuthenticationException:
            self.notify("Authentication failed. Please check your credentials.")
        except Exception as exc:
            self.notify(f"Connection error: {exc}")

    # ------------------------------------------------------------------ #
    # Unknown host — trust-on-first-use flow
    # ------------------------------------------------------------------ #

    def _handle_unknown_host(self, server_info: dict) -> None:
        host = server_info["host"]
        port = int(server_info["port"])

        try:
            sock = socket.create_connection((host, port), timeout=10)
            transport = paramiko.Transport(sock)
            transport.start_client(timeout=10)
            key = transport.get_remote_server_key()
            transport.close()
            sock.close()
        except Exception as exc:
            self.notify(
                f"Could not retrieve host key from {host}:{port}: {exc}\n"
                "Verify the host is reachable and try again."
            )
            return

        fingerprint = self.format_fingerprint(key)
        key_type = key.get_name()

        def on_decision(trust: bool | None) -> None:
            if not trust:
                self.notify(
                    f"Connection to {host} cancelled — host key was not trusted.\n"
                    "Verify the fingerprint out-of-band before connecting."
                )
                return

            host_keys = self._load_or_init_host_keys()
            storage_name = f"[{host}]:{port}" if port != 22 else host
            host_keys.add(storage_name, key_type, key)
            host_keys.save(str(self.known_hosts_path))
            self.notify(f"Host key for {host} saved. Connecting…")
            self.connect_to_server(server_info)

        self.app.push_screen(
            CronHostKeyConfirm(host, port, key_type, fingerprint),
            on_decision,
        )

    # ------------------------------------------------------------------ #
    # Changed host key flow
    # ------------------------------------------------------------------ #

    def _handle_bad_host_key(
        self, server_info: dict, exc: paramiko.BadHostKeyException
    ) -> None:
        host = server_info["host"]
        port = int(server_info["port"])
        expected_fp = self.format_fingerprint(exc.expected_key)
        received_fp = self.format_fingerprint(exc.key)

        def on_decision(trust: bool | None) -> None:
            if not trust:
                self.notify(
                    f"Connection to {host} cancelled — changed key was not trusted.\n"
                    "Contact your server admin to verify the new fingerprint."
                )
                return

            host_keys = self._load_or_init_host_keys()
            storage_name = f"[{host}]:{port}" if port != 22 else host
            host_keys.add(storage_name, exc.key.get_name(), exc.key)
            host_keys.save(str(self.known_hosts_path))
            self.notify(f"Updated trusted key for {host}. Reconnecting…")
            self.connect_to_server(server_info)

        self.app.push_screen(
            CronHostKeyChanged(host, port, expected_fp, received_fp),
            on_decision,
        )

    # ------------------------------------------------------------------ #
    # Cron table helpers
    # ------------------------------------------------------------------ #

    def show_cron_table_for_server(
        self, ssh_client, server_info, crontab_user
    ) -> None:
        if self.current_cron_table:
            self.current_cron_table.ssh_client = ssh_client
            self.current_cron_table.remote = True
            self.current_cron_table.crontab_user = crontab_user
            self.current_cron_table.action_refresh()
            self.notify(f"Switched to {server_info['name']}")
            return

        self.current_cron_table = CronTable(
            remote=True,
            ssh_client=ssh_client,
            id="remote-cron-table",
            crontab_user=crontab_user,
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
            except Exception:
                pass
            self.current_ssh_client = None

        self.show_disconnected_message()

        for server_info in self.servers.values():
            server_info["connected"] = False
            self.notify(f"Disconnected from server {server_info['name']}")

        self.save_servers()

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #

    def load_servers(self) -> dict:
        if self.servers_path.exists():
            try:
                with self.servers_path.open("rb") as f:
                    loaded_servers = tomllib.load(f)

                for server_id, server_info in loaded_servers.items():
                    if "encrypted_password" in server_info:
                        encrypted_password = server_info.pop("encrypted_password")
                        if encrypted_password:
                            try:
                                server_info["password"] = decrypt_password(
                                    encrypted_password
                                )
                            except Exception as exc:
                                print(
                                    f"❌ Failed to decrypt password for {server_id}: {exc}"
                                )
                                server_info["password"] = None
                        else:
                            server_info["password"] = None
                    elif "password" not in server_info:
                        server_info["password"] = None

                    if "crontab_user" not in server_info:
                        server_info["crontab_user"] = None

                return loaded_servers
            except Exception as exc:
                print(f"❌ Warning: Failed to load servers: {exc}")
        else:
            print("📝 No servers file found, starting with empty list")
        return {}

    def save_servers(self) -> None:
        try:
            self.servers_path.parent.mkdir(parents=True, exist_ok=True)
            toml_safe_servers = {}
            for server_id, server_info in self.servers.items():
                encrypted_password = ""
                if server_info.get("password"):
                    encrypted_password = encrypt_password(server_info["password"])

                toml_safe_servers[server_id] = {
                    "name": server_info["name"],
                    "host": server_info["host"],
                    "port": server_info["port"],
                    "username": server_info["username"],
                    "encrypted_password": encrypted_password,
                    "ssh_key": server_info["ssh_key"],
                    "connected": server_info["connected"],
                    "crontab_user": server_info.get("crontab_user")
                    if server_info.get("crontab_user")
                    else server_info["username"],
                }

            with self.servers_path.open("w", encoding="utf-8") as f:
                tomlkit.dump(toml_safe_servers, f)
        except Exception as exc:
            self.notify(f"❌ Error: Failed to save servers: {exc}")

    # ------------------------------------------------------------------ #
    # Add / delete server actions
    # ------------------------------------------------------------------ #

    def action_add_server(self) -> None:
        def on_server_added(result) -> None:
            if result:
                name = result.get("username") + "@" + result.get("hostname")
                host = result.get("hostname")
                port = result.get("port")
                username = result.get("username")
                password = result.get("password") if result.get("password") else None
                crontab_user = result.get("crontab_user")
                self.add_server_to_tree(
                    name, host, port, username, password, crontab_user
                )

        cron_ssh_modal = CronSSHModal()
        self.app.push_screen(cron_ssh_modal, on_server_added)

    def add_server_to_tree(
        self,
        name: str,
        host: str,
        port: str,
        username: str,
        password: str | None,
        crontab_user: str | None = None,
    ) -> None:
        servers_tree = self.query_one("#servers-tree", Tree)
        server_id = f"{username}@{host}:{crontab_user}"
        if server_id not in self.servers:
            self.servers[server_id] = {
                "name": name,
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "ssh_key": True if not password else False,
                "connected": False,
                "crontab_user": crontab_user,
            }
            servers_tree.root.add_leaf(
                f"{name}: {crontab_user if crontab_user else username}", server_id
            )
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
