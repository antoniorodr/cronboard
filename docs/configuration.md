# Configuration

Cronboard stores its configuration in the user's home directory under `~/.config/cronboard/`.

---

## Config Files

| File                               | Purpose                       |
| ---------------------------------- | ----------------------------- |
| `~/.config/cronboard/config.toml`  | General settings (e.g. theme) |
| `~/.config/cronboard/servers.toml` | Saved SSH servers             |

These files are created automatically the first time you run Cronboard. You do not need to edit them manually.

---

## Theme

Cronboard is built on [Textual](https://textual.textualize.io), which ships with several built-in themes.

The active theme is saved automatically whenever you change it inside the application. The default theme is **`catppuccin-mocha`**.

To change the theme, use Textual's built-in theme picker (accessible via the command palette with `Ctrl+P` → `theme`).

### `config.toml` example

```toml
theme = "catppuccin-mocha"
```

---

## Saved Servers

The `servers.toml` file holds the list of SSH servers you have added. Each server entry looks like this:

```toml
[username@host:crontab_user]
name = "username@hostname"
host = "hostname"
port = 22
username = "username"
encrypted_password = "<bcrypt-encrypted>"
ssh_key = false
connected = false
crontab_user = "username"
```

Passwords are **never stored in plain text**, they are encrypted with `bcrypt` before being written to disk.
