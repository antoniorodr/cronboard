# Local Cron Management

The **Local** tab shows all cron jobs for the currently logged-in user. Cronboard reads and writes your crontab directly, so what you see in the table matches what `crontab -l` shows. Any change you make (create, edit, delete, pause) is written to your user crontab immediately.

---

## Viewing Cron Jobs

All jobs are displayed in a table with the following columns:

| Column | Description |
|---|---|
| ID | Comment attached to the job (used as identifier) |
| Expression | Raw cron expression |
| Command | Shell command to execute |
| Last Run | Previous scheduled execution time |
| Next Run | Next scheduled execution time |
| Status | `Active` (green), `Paused` (red), or `Inactive` (yellow) |

The table is read from your crontab when you open the app or when you press **`r`** to refresh. If you edit the crontab in another terminal, refresh in Cronboard to see the updates.

---

## Creating a Cron Job

Press **`c`** to open the creation form. The form is the same for both new jobs and edits (when you press **`e`** on an existing job).

![Create cron job form with Expression, Command, and ID fields and live human-readable description](images/create-job.gif)

### Fields

| Field | Description |
|---|---|
| Expression | A valid cron expression or special alias (see below) |
| Command | The shell command to run. Supports path autocompletion with `Tab` |
| ID | A unique identifier stored as a crontab comment |

### Cron expression cheatsheet

| Symbol | Meaning |
|---|---|
| `*` | Any value |
| `,` | Value list separator (e.g. `1,3,5`) |
| `-` | Range of values (e.g. `1-5`) |
| `/` | Step values (e.g. `*/5`) |

Format: `Minute  Hour  Day  Month  Weekday`

### Special aliases

| Alias | Equivalent | Description |
|---|---|---|
| `@reboot` | — | Run once at startup |
| `@hourly` | `0 * * * *` | Every hour |
| `@daily` / `@midnight` | `0 0 * * *` | Every day at midnight |
| `@weekly` | `0 0 * * 0` | Every Sunday at midnight |
| `@monthly` | `0 0 1 * *` | First day of each month |
| `@yearly` / `@annually` | `0 0 1 1 *` | Once a year on January 1st |

As you type the expression, a **live description** is shown below the field (e.g. *"At 00:00 on day-of-month 1"*). Use it to confirm the schedule before saving.

---

## Editing a Cron Job

1. Navigate to the job using **`j`** / **`k`** (or arrow keys).
2. Press **`e`** to open the edit form — pre-filled with the current values.
3. Modify the fields and press **Save**.

The job is updated in your crontab and the table refreshes.

---

## Deleting a Cron Job

1. Navigate to the job.
2. Press **`D`** (uppercase).
3. Confirm the deletion in the confirmation dialog.

The job is removed from your crontab. This cannot be undone from within Cronboard, so use with care.

---

## Pausing and Resuming

Press **`p`** on a selected job to toggle its active state:

- **Active → Paused**: the job is commented out in the crontab and will not run.
- **Paused → Active**: the job is uncommented and resumes its schedule.

Pausing is useful when you want to keep the job definition but temporarily disable it (e.g. for debugging or maintenance) without losing the expression or command.

---

## Refreshing

Press **`r`** to reload the crontab from disk at any time. Use this if you changed the crontab outside Cronboard or if you want to see the latest state after an external edit.
