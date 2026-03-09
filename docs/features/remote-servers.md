# Remote Servers (SSH)

Cronboard can connect to remote servers via SSH and manage their cron jobs exactly like local ones.

---

## Adding a Server

1. Switch to the **Servers** tab.
2. Press **`a`** to open the **Add Server** dialog.
3. Fill in the fields:

| Field | Description |
|---|---|
| Hostname | Server hostname or IP. Append `:port` for a non-standard port (e.g. `myserver.com:2222`). Defaults to port `22`. |
| Username | SSH login username |
| Password | Leave empty to use an SSH key instead |
| Crontab user | Optional. Manage cron jobs for a different user (requires `sudo` permissions). Leave empty to use the current user. |

4. Click **Add Server**.

Servers are saved persistently in `~/.config/cronboard/servers.toml`. Passwords are stored encrypted.

---

## SSH Key Authentication

If you leave the **Password** field empty, Cronboard will connect using your SSH key. It looks for the `known_hosts` file in the default location:

```
~/.ssh/known_hosts
```

Make sure the server's host key is already trusted (i.e. you have connected to it manually at least once).

---

## Connecting to a Server

1. In the **Servers** tab, navigate to the server in the tree view using **`j`** / **`k`**.
2. Press **`c`** to connect.

Once connected, the cron table for that server appears on the right and supports all the same operations as the local tab:

- **Create** (`c`), **Edit** (`e`), **Delete** (`D`), **Pause** (`p`), **Refresh** (`r`), **Search** (`/`)

---

## Managing Another User's Cron Jobs

If you entered a **Crontab user** when adding the server, Cronboard will run `crontab -u <user>` on the remote server. This requires your SSH user to have `sudo` (or equivalent) privileges on the remote machine.

---

## Disconnecting

Press **`d`** to disconnect from the current server. The tree view remains intact so you can reconnect later.

---

## Deleting a Server

1. Navigate to the server in the tree view.
2. Press **`D`** (uppercase) and confirm.

This removes the server from both the tree view and the saved configuration file.
