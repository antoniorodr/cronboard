# Search

Cronboard includes a built-in search feature that lets you quickly find cron jobs by keyword. It’s useful when you have many jobs and want to jump to one that matches a script name, ID, or expression.

---

## Starting a Search

Press **`/`** to open the search prompt. Type your query and confirm with **`Enter`**.

The search is **case-insensitive** and matches against:

- Job **ID** (comment)
- Cron **expression**
- **Command**

For example, typing `backup` will match any job whose ID, expression, or command contains “backup”. You don’t need to type the whole word; partial matches count.

![Search prompt open with a query; matching table rows highlighted and next/previous match navigation](../images/search.gif)

---

## Navigating Matches

After a search is performed, matching rows are highlighted in **bold yellow**. If there is more than one match, move between them with the keys below.

| Key | Action                         |
| --- | ------------------------------ |
| `n` | Jump to the **next** match     |
| `N` | Jump to the **previous** match |

A notification shows the total number of matches found (e.g. _"3 match(es) for 'backup'"_). If there are no matches, you’ll see a message saying so and the table stays unchanged.

---

## Clearing a Search

Press **`Escape`** to clear the current search and restore the table to its normal view. You can also start a new search by pressing **`/`** again and typing a different query.

---

## Notes

- Search works in both the **Local** tab and on **Remote Server** tables. The behavior is the same in both.
- The table must have at least one row for search to be available. If the table is empty, the search shortcut may not open the prompt.
