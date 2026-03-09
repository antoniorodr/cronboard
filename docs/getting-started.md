# Getting Started

## Launching Cronboard

After [installing](installation.md), start the application with:

```bash
cronboard
```

---

## Interface Overview

When Cronboard opens you will see:

- **Header** — shows the app name and current version.
- **Tab bar** — switch between **Local** (your local cron jobs) and **Servers** (remote SSH servers).
- **Main table** — lists all cron jobs with the following columns:

| Column | Description |
|---|---|
| ID | The comment/identifier attached to the job |
| Expression | The raw cron expression (e.g. `0 * * * *`) |
| Command | The shell command that runs |
| Last Run | When the job last ran |
| Next Run | When the job will run next |
| Status | `Active`, `Paused`, or `Inactive` |

- **Footer** — displays all available keyboard bindings for the current context.

---

## Your First Cron Job

1. Press **`c`** to open the **Create** form.
2. Enter a valid cron expression in the **Expression** field.  
   As you type, a human-readable description appears below the field in real time (e.g. *"Every hour"*).
3. Enter the **Command** to execute. Use **`Tab`** to autocomplete file paths.
4. Give the job a unique **ID** (stored as a crontab comment).
5. Press **Save**.

The table refreshes automatically and your new job appears immediately.

---

## Switching Between Local and Remote

Use the **`Tab`** key to switch focus between panels, or click the **Local** / **Servers** tabs at the top.

- **Local** — manages your current user's crontab.
- **Servers** — lists saved SSH servers. See [Remote Servers](features/remote-servers.md) for setup.

---

## Quitting

Press **`q`** or **`Ctrl+Q`** to exit Cronboard.
