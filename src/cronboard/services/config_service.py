from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cronboard.screens.cron_creator import CronCreator

import tomlkit

from cronboard.config import CRONBOARD_CONFIG_FILE, CRONBOARD_NOTIFICATIONS_FILE


class ConfigService:
    """Services for Config related operations."""

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
