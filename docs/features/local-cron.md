# Local Cron Management

The **Local** tab shows all cron jobs for the currently logged-in user. Cronboard reads and writes your crontab directly.

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

---

## Creating a Cron Job

Press **`c`** to open the creation form.

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

As you type the expression, a **live description** is shown below the field (e.g. *"At 00:00 on day-of-month 1"*).

---

## Editing a Cron Job

1. Navigate to the job using **`j`** / **`k`** (or arrow keys).
2. Press **`e`** to open the edit form — pre-filled with the current values.
3. Modify the fields and press **Save**.

---

## Deleting a Cron Job

1. Navigate to the job.
2. Press **`D`** (uppercase).
3. Confirm the deletion in the confirmation dialog.

---

## Pausing and Resuming

Press **`p`** on a selected job to toggle its active state:

- **Active → Paused**: the job is commented out in the crontab and will not run.
- **Paused → Active**: the job is uncommented and resumes its schedule.

---

## Refreshing

Press **`r`** to reload the crontab from disk at any time.
