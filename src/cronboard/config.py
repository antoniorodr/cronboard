from pathlib import Path

CONFIG_REL_PATH: str = ".config/cronboard"
CONFIG_DIR: Path = Path.home() / CONFIG_REL_PATH
CRONBOARD_CONFIG_FILE: Path = CONFIG_DIR / "config.toml"
CRONBOARD_NOTIFICATIONS_FILE: Path = CONFIG_DIR / "notifications.toml"
WRAPPER_DIST: str = "cron-wrapper.sh"
LOG_REL_PATH: str = f"{CONFIG_REL_PATH}/logs"
CONFIG_FILE: Path = CONFIG_DIR / "servers.toml"
KEY_FILE: Path = CONFIG_DIR / "secret.key"
LOG_DIR: Path = CONFIG_DIR / "logs"
WRAPPER_SOURCE: Path = Path(__file__).parent / "logging" / "cron-wrapper.sh"
CRON_ALIASES: dict[str, None | str] = {
    "@reboot": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@midnight": "0 0 * * *",
}
