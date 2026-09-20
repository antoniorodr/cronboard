import tomllib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cronboard.screens.cron_creator import CronCreator

import tomlkit

from cronboard.config import (
    CONFIG_FILE,
    CRONBOARD_CONFIG_FILE,
    CRONBOARD_NOTIFICATIONS_FILE,
)
from cronboard.services.cron_encrypt_service import CronEncryptService


class ConfigService:
    """Service for Config related operations."""

    @staticmethod
    def save_job_settings(
        cron_creator: "CronCreator", cron_name: str, notifications: bool, logging: bool
    ) -> None:
        """Saves the notification settings to the notifications file."""

        try:
            with CRONBOARD_NOTIFICATIONS_FILE.open("r") as f:
                config = tomlkit.loads(f.read())
        except FileNotFoundError:
            config = tomlkit.document()

        ConfigService._migrate_old_format(config)

        if cron_creator.server_name not in config or not isinstance(
            config[cron_creator.server_name], dict
        ):
            config[cron_creator.server_name] = tomlkit.table()
        config[cron_creator.server_name][cron_name] = tomlkit.table()
        config[cron_creator.server_name][cron_name]["notifications"] = notifications
        config[cron_creator.server_name][cron_name]["logging"] = logging

        with CRONBOARD_NOTIFICATIONS_FILE.open("w") as f:
            f.write(tomlkit.dumps(config))

    @staticmethod
    def _migrate_old_format(config) -> None:
        """Migrate old flat format (key = true) to new per-server format."""

        to_migrate = []
        for key, value in config.items():
            if isinstance(value, bool):
                to_migrate.append(key)
        for key in to_migrate:
            value = config.pop(key)
            if "local" not in config or not isinstance(config["local"], dict):
                config["local"] = tomlkit.table()
            config["local"][key] = tomlkit.table()
            config["local"][key]["notifications"] = value
            config["local"][key]["logging"] = False

    @staticmethod
    def _generate_telegram_config() -> str:
        """Generates a minimal config.toml with only Telegram settings."""

        try:
            with CRONBOARD_CONFIG_FILE.open("r") as f:
                config: dict = tomlkit.loads(f.read())
            minimal: dict = tomlkit.document()
            minimal["telegram_token"] = config.get("telegram_token", "")
            minimal["telegram_chat_id"] = config.get("telegram_chat_id", "")
            return tomlkit.dumps(minimal)
        except Exception as e:
            print(f"Error: {e}")
            return ""

    @staticmethod
    def _generate_notifications_config_for_server(server_name: str) -> str | None:
        """Generates a flattened notifications.toml for a specific server.

        Extracts only entries for the given server and removes the server
        prefix.
        """

        try:
            with CRONBOARD_NOTIFICATIONS_FILE.open("r") as f:
                config = tomlkit.loads(f.read())
            result = tomlkit.document()
            server_section = config.get(server_name)
            if isinstance(server_section, dict):
                for job_name, value in server_section.items():
                    if isinstance(value, dict):
                        result[job_name] = value
            return tomlkit.dumps(result)
        except Exception as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def load_servers_config() -> dict:
        """Loads the servers config from the config file.
        Returns:
            A dictionary with the servers config.
        """

        if CONFIG_FILE.exists():
            try:
                with CONFIG_FILE.open("rb") as f:
                    loaded_servers = tomllib.load(f)

                for server_id, server_info in loaded_servers.items():
                    if "encrypted_password" in server_info:
                        encrypted_password = server_info.pop("encrypted_password")
                        if encrypted_password:
                            try:
                                server_info["password"] = (
                                    CronEncryptService.decrypt_password(
                                        encrypted_password
                                    )
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

                    if "crontab_user" not in server_info:
                        server_info["crontab_user"] = None

                return loaded_servers
            except Exception as e:
                print(f"❌ Warning: Failed to load servers: {e}")
        else:
            print("📝 No servers file found, starting with empty list")
        return {}

    @staticmethod
    def save_servers_config(servers: dict) -> None | Exception:
        """Saves the servers config to the config file.

        Args:
            servers: The dictionary with the servers config.
        """

        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            toml_safe_servers = {}
            for server_id, server_info in servers.items():
                encrypted_password = ""
                if server_info.get("password"):
                    encrypted_password = CronEncryptService.encrypt_password(
                        server_info["password"]
                    )

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

            with CONFIG_FILE.open("w", encoding="utf-8") as f:
                tomlkit.dump(toml_safe_servers, f)
            return None
        except Exception as e:
            return e
