from pathlib import Path

CONFIG_FILE = Path.home() / ".config/cronboard/servers.toml"
CONFIG_DIR = Path.home() / ".config/cronboard"
KEY_FILE = CONFIG_DIR / "secret.key"

##TODO: Missing logging config paths. Remember that these are different for each platform.
