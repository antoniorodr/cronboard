from pathlib import Path

CONFIG_DIR = Path.home() / ".config/cronboard"
CONFIG_FILE = CONFIG_DIR / "servers.toml"
KEY_FILE = CONFIG_DIR / "secret.key"
LOG_DIR = CONFIG_DIR / "logs"

##TODO: Missing logging config paths. Remember that these are different for each platform.
