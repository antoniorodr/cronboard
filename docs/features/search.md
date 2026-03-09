# Search

Cronboard includes a built-in search feature that lets you quickly find cron jobs by keyword.

---

## Starting a Search

Press **`/`** to open the search prompt. Type your query and confirm with **`Enter`**.

The search is **case-insensitive** and matches against:

- Job **ID** (comment)
- Cron **expression**
- **Command**

---

## Navigating Matches

After a search is performed, matching rows are highlighted in **bold yellow**.

| Key | Action |
|---|---|
| `n` | Jump to the **next** match |
| `N` | Jump to the **previous** match |

A notification shows the total number of matches found (e.g. *"3 match(es) for 'backup'"*).

---

## Clearing a Search

Press **`Escape`** to clear the current search and restore the table to its normal view.

---

## Notes

- Search works in both the **Local** tab and on **Remote Server** tables.
- The table must have at least one row for search to be available.
