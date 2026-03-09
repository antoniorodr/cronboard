# Cronboard Project Explanation

## Project Overview

Cronboard is a terminal-based application built with Python and the Textual framework that allows users to manage and schedule cron jobs both locally and on remote servers. The application provides an intuitive user interface for creating, editing, pausing, resuming, and deleting cron jobs with validation and human-readable feedback.

### Main Goals

- Simplify cron job management through a user-friendly terminal interface
- Support both local and remote SSH-based cron administration
- Provide real-time validation and human-readable descriptions of cron expressions
- Secure passwords and sensitive information with encryption

## Architecture

The project is structured into three main modules:

### 1. **cronboard** - Main application

### 2. **cronboard_widgets** - UI components

### 3. **cronboard_encryption** - Encryption functionality

---

## Main Components and Algorithms

### 1. CronBoard (app.py)

**Purpose:** Main application that coordinates all components and handles user interaction.

#### Functions:

##### `compose()`

- **Input:** None
- **Output:** ComposeResult with UI components
- **Steps:**
    1. Retrieves version number from package
    2. Sets up configuration path (`~/.config/cronboard/config.toml`)
    3. Creates title label with version
    4. Creates footer for keyboard commands
    5. Creates tabs for "Local" and "Servers"
    6. Creates container for content
- **Goal:** Build the basic UI structure

##### `on_mount()`

- **Input:** None
- **Output:** None (side effects)
- **Steps:**
    1. Loads configuration from TOML file
    2. Sets theme based on saved preference (default: "catppuccin-mocha")
    3. Initializes local CronTable
    4. Mounts and displays local table
- **Goal:** Initialize application state at startup

##### `load_config()`

- **Input:** None
- **Output:** Dictionary with configuration data
- **Steps:**
    1. Checks if configuration file exists
    2. Opens and parses TOML file with `tomllib`
    3. Returns empty dictionary on error
- **Goal:** Load user preferences

##### `watch_theme(theme: str)`

- **Input:** `theme` - Theme name (string)
- **Output:** None (saves to file)
- **Steps:**
    1. Creates configuration directory if it doesn't exist
    2. Writes theme to configuration file with `tomlkit`
- **Goal:** Persist theme selection

##### `on_tabs_tab_activated(event)`

- **Input:** `event` - Tabs.TabActivated event
- **Output:** None (displays correct content)
- **Steps:**
    1. Gets label from activated tab
    2. Calls `show_tab_content()` with correct index
- **Goal:** Handle tab switching

##### `show_tab_content(index: int)`

- **Input:** `index` - Tab index (0=Local, 1=Servers)
- **Output:** None (shows/hides components)
- **Steps:**
    1. If index 0: Show local table, hide server view
    2. If index 1: Create server widget if needed, show it
- **Goal:** Manage visibility of tab content

##### `action_create_cronjob(cron, remote, ssh_client, crontab_user)`

- **Input:**
    - `cron` - CronTab object
    - `remote` - Boolean (if remote server)
    - `ssh_client` - Paramiko SSH client (optional)
    - `crontab_user` - Username for crontab (optional)
- **Output:** None (opens modal)
- **Steps:**
    1. Defines callback function `check_save()`
    2. Opens CronCreator modal with screen push
    3. On save: Updates relevant tables
- **Goal:** Start process for creating new cron job

##### `action_delete_cronjob(job, cron, remote, ssh_client, crontab_user)`

- **Input:**
    - `job` - CronJob object to delete
    - Other parameters for context
- **Output:** None (opens confirmation dialog)
- **Steps:**
    1. Defines callback function `check_delete()`
    2. Opens CronDeleteConfirmation modal
    3. On confirmation: Updates tables
- **Goal:** Delete cron job with user confirmation

##### `action_edit_cronjob(cron, identificator, expression, command, ...)`

- **Input:**
    - `cron` - CronTab object
    - `identificator` - Job ID
    - `expression` - Cron expression
    - `command` - Command to execute
    - Context parameters
- **Output:** None (opens edit modal)
- **Steps:**
    1. Defines callback function `check_save()`
    2. Opens CronCreator in edit mode with existing values
    3. On save: Updates tables
- **Goal:** Edit existing cron job

---

### 2. CronTable (CronTable.py)

**Purpose:** Display and manage cron jobs in a tabular view.

#### Functions:

##### `__init__(remote, ssh_client, crontab_user, **kwargs)`

- **Input:**
    - `remote` - Boolean (local or remote)
    - `ssh_client` - SSH client
    - `crontab_user` - Username
- **Output:** CronTable instance
- **Goal:** Initialize table with context

##### `on_mount()`

- **Input:** None
- **Output:** None (builds table)
- **Steps:**
    1. Initializes local CronTab with `CronTab(user=True)`
    2. Adds columns: Identificator, Expression, Command, Last Run, Next Run, Status
    3. If remote: Fetches crontab via SSH command `crontab -l` or `crontab -u <user> -l`
    4. Handles exit status 1 (no crontab) as empty string
    5. Parses SSH crontab content with `CronTab(tab=content)`
    6. Calls `load_crontabs()` to populate table
- **Goal:** Set up table with data

##### `parse_cron(cron)`

- **Input:** `cron` - CronTab object
- **Output:** None (adds rows to table)
- **Steps:**
    1. Iterates through each job in cron
    2. Extracts expression with `job.slices.render()`
    3. Gets command and identificator (comment)
    4. Checks if job is active with `job.is_enabled()`
    5. Calculates next run time with `job.schedule().get_next()`
    6. Calculates previous run time with `schedule.get_prev()`
    7. Formats dates as "dd.mm.yyyy at HH:MM"
    8. Handles ValueError for invalid expressions
    9. Adds row to table with all values
- **Goal:** Convert cron data to table rows

##### `load_crontabs()`

- **Input:** None
- **Output:** None (updates display)
- **Steps:**
    1. Clears existing table content
    2. If remote: Parses SSH cron
    3. Otherwise: Parses local cron
- **Goal:** Load/reload cron data

##### `action_refresh()`

- **Input:** None
- **Output:** None (updates data)
- **Steps:**
    1. If remote: Runs `crontab -l` via SSH
    2. Reads output and parses with CronTab
    3. If local: Reinitialize CronTab(user=True)
    4. Calls `load_crontabs()`
- **Goal:** Refresh table with fresh data

##### `action_pause_cronjob()`

- **Input:** None (uses cursor_row)
- **Output:** None (toggles pause status)
- **Steps:**
    1. Gets row at cursor position
    2. Extracts identificator, expression and command
    3. Finds matching job in crontab
    4. Toggles enabled status with `job.enable(False/True)`
    5. If remote: Writes to remote crontab with `write_remote_crontab()`
    6. If local: Writes with `cron.write()`
    7. Reloads table
- **Goal:** Pause or resume a cron job

##### `action_edit_cronjob()`

- **Input:** None (uses selected row)
- **Output:** None (opens edit modal)
- **Steps:**
    1. Gets row at cursor
    2. Extracts identificator, expression and command
    3. Finds job with `find_if_cronjob_exists()`
    4. Calls `action_edit_cronjob_keybind()` with values
- **Goal:** Start editing selected job

##### `action_delete_cronjob()`

- **Input:** None (uses selected row)
- **Output:** None (opens delete confirmation)
- **Steps:**
    1. Gets row at cursor
    2. Finds job with `find_if_cronjob_exists()`
    3. Calls `action_delete_cronjob_keybind()` with job
- **Goal:** Start deletion process for selected job

##### `find_if_cronjob_exists(identificator, cmd)`

- **Input:**
    - `identificator` - Job ID
    - `cmd` - Command
- **Output:** CronJob or None
- **Steps:**
    1. Iterates through all jobs in crontab
    2. Compares comment and command
    3. Returns match or None
- **Goal:** Find specific job in crontab

##### `write_remote_crontab()`

- **Input:** None (uses instance variables)
- **Output:** Boolean (success)
- **Steps:**
    1. Renders crontab content with `ssh_cron.render()`
    2. Constructs command: `crontab -u <user> -` or `crontab -`
    3. Executes SSH command with `exec_command()`
    4. Writes content to stdin
    5. Closes write channel with `shutdown_write()`
    6. Checks exit status and stderr
    7. Returns True on success, False on error
- **Goal:** Update crontab on remote server

---

### 3. CronCreator (CronCreator.py)

**Purpose:** Modal for creating or editing cron jobs with validation.

#### Constants:

##### `CRON_ALIASES`

Dictionary mapping special cron expressions to standard format:

- `@reboot` → None (special handling)
- `@hourly` → "0 \* \* \* \*"
- `@daily` → "0 0 \* \* \*"
- `@weekly` → "0 0 \* \* 0"
- `@monthly` → "0 0 1 \* \*"
- `@yearly` → "0 0 1 1 \*"
- `@annually` → "0 0 1 1 \*"
- `@midnight` → "0 0 \* \* \*"

#### Functions:

##### `__init__(cron, expression, command, identificator, remote, ssh_client, crontab_user)`

- **Input:**
    - `cron` - CronTab object
    - `expression` - Existing expression (for editing)
    - `command` - Existing command
    - `identificator` - Existing ID
    - Context parameters
- **Output:** CronCreator instance
- **Goal:** Initialize creator with context

##### `compose()`

- **Input:** None
- **Output:** ComposeResult with form elements
- **Steps:**
    1. Creates Grid container
    2. Adds information labels about special characters (\*, ,, -, /)
    3. Adds Input for cron expression with placeholder "\* \* \* \* \*"
    4. Adds Label for description (label_desc)
    5. Adds Input for command
    6. Adds Input for identificator
    7. Adds Save and Cancel buttons
- **Goal:** Build input form

##### `on_input_changed(event)`

- **Input:** `event` - Input.Changed event
- **Output:** None (updates description)
- **Steps:**
    1. Checks if input is "expression" field
    2. Gets description label
    3. Calls `expression_description()` with expression
    4. Removes existing error messages
- **Goal:** Provide real-time validation and feedback

##### `expression_description(expr, label_desc)`

- **Input:**
    - `expr` - Cron expression (string)
    - `label_desc` - Label widget
- **Output:** None (updates label)
- **Steps:**
    1. If empty: Clears label and removes classes
    2. If "@reboot": Shows "Runs at system startup"
    3. Converts alias with `CRON_ALIASES.get()`
    4. Creates ExpressionDescriptor with options:
        - locale_code = "en"
        - use_24hour_time_format = True
    5. Generates description with `get_description()`
    6. On success: Updates label with green color (success class)
    7. On Exception: Shows "Invalid cron expression" with red color (error class)
- **Goal:** Convert cron expression to human-readable text

##### `on_button_pressed(event)`

- **Input:** `event` - Button.Pressed event
- **Output:** None (saves or cancels)
- **Steps:**
    1. If Cancel: Dismiss with False
    2. If Save:
        1. Gets values from all input fields
        2. Validates that identificator is not empty
        3. Finds existing job with `find_if_cronjob_exists()`
        4. If job exists:
            - Updates command with `job.set_command()`
            - Updates expression with `job.setall()`
        5. If new job:
            - Creates with `cron.new(command, comment)`
            - Sets expression with `setall()`
        6. Calls `write_cron_changes()` to save
        7. Dismiss with True on success
        8. Shows error message on ValueError/KeyError
- **Goal:** Save cron job with validation

##### `write_cron_changes()`

- **Input:** None
- **Output:** None (writes changes)
- **Steps:**
    1. If remote and SSH client:
        1. Renders crontab with `cron.render()`
        2. Constructs command based on crontab_user
        3. Executes SSH command
        4. Writes content to stdin
        5. Closes write channel
        6. Checks exit status and errors
        7. Shows notification on error
    2. If local:
        - Writes with `cron.write()`
- **Goal:** Persist cron changes

##### `find_if_cronjob_exists(identificator, cmd)`

- **Input:**
    - `identificator` - Job ID
    - `cmd` - Command
- **Output:** CronJob or None
- **Steps:**
    1. Iterates through cron
    2. Compares comment and command
    3. Returns match or None
- **Goal:** Check if job already exists

---

### 4. CronServers (CronServers.py)

**Purpose:** Manage and connect to remote servers via SSH.

#### Functions:

##### `__init__()`

- **Input:** None
- **Output:** CronServers instance
- **Steps:**
    1. Sets servers_path to `~/.config/cronboard/servers.toml`
    2. Loads servers with `load_servers()`
    3. Initializes SSH client and table as None
- **Goal:** Set up server management

##### `compose()`

- **Input:** None
- **Output:** ComposeResult with tree and content area
- **Steps:**
    1. Creates CronTree with "Servers" root
    2. Expands root node
    3. Creates content_area Label with instructions
    4. Mounts in Grid layout
- **Goal:** Build server UI

##### `on_mount()`

- **Input:** None
- **Output:** None (populates tree)
- **Steps:**
    1. Gets servers tree
    2. Iterates through saved servers
    3. Adds leaf node for each server with format "name: crontab_user"
    4. Refreshes tree
- **Goal:** Display saved servers

##### `action_connect_server()`

- **Input:** None (uses selected node)
- **Output:** None (connects to server)
- **Steps:**
    1. Gets cursor_node from tree
    2. Checks that it's not root node
    3. Gets server_info based on server_id
    4. Calls `connect_to_server()` with server_info
- **Goal:** Start connection to selected server

##### `connect_to_server(server_info)`

- **Input:** `server_info` - Dictionary with server details
- **Output:** None (establishes connection)
- **Steps:**
    1. Creates Paramiko SSHClient
    2. Loads system host keys with `load_system_host_keys()`
    3. Sets missing host key policy to WarningPolicy
    4. Extracts host, port, username, password
    5. If ssh_key: Connects without password
    6. Otherwise: Connects with password
    7. Closes existing connection if active
    8. Saves new ssh_client
    9. Calls `show_cron_table_for_server()`
    10. Sets connected=True and saves
    11. Shows success notification
    12. Handles AuthenticationException and other errors
- **Goal:** Establish SSH connection to server

##### `show_cron_table_for_server(ssh_client, server_info, crontab_user)`

- **Input:**
    - `ssh_client` - Active SSH client
    - `server_info` - Server details
    - `crontab_user` - Username for crontab
- **Output:** None (displays table)
- **Steps:**
    1. If table exists:
        - Updates ssh_client, remote and crontab_user
        - Refreshes table
    2. If new table:
        - Creates CronTable with remote=True
        - Finds container and horizontal layout
        - Removes old content
        - Mounts new table
        - Updates content_area
- **Goal:** Display cron jobs from remote server

##### `show_disconnected_message()`

- **Input:** None
- **Output:** None (shows message)
- **Steps:**
    1. Removes existing table if active
    2. Creates disconnected Label
    3. Finds container
    4. Removes old content
    5. Mounts new label
    6. Updates content_area
- **Goal:** Display disconnected state

##### `action_disconnect_server()`

- **Input:** None
- **Output:** None (disconnects)
- **Steps:**
    1. Closes SSH client if active
    2. Resets current_ssh_client
    3. Calls `show_disconnected_message()`
    4. Sets connected=False for all servers
    5. Shows notification
    6. Saves changes
- **Goal:** Terminate SSH connection

##### `load_servers()`

- **Input:** None
- **Output:** Dictionary with servers
- **Steps:**
    1. Checks if servers.toml exists
    2. Opens and parses with tomllib
    3. For each server:
        1. Decrypts password with `decrypt_password()`
        2. Handles missing fields
        3. Sets password to None if empty
        4. Ensures crontab_user exists
    4. Returns empty dict on error
- **Goal:** Load saved servers with decrypted passwords

##### `save_servers()`

- **Input:** None
- **Output:** None (saves to file)
- **Steps:**
    1. Creates configuration directory
    2. For each server:
        1. Encrypts password with `encrypt_password()`
        2. Builds TOML-safe dictionary with:
            - name, host, port, username
            - encrypted_password
            - ssh_key, connected
            - crontab_user
    3. Writes to file with tomlkit.dump()
    4. Handles errors with notification
- **Goal:** Persist server configuration securely

##### `action_add_server()`

- **Input:** None
- **Output:** None (opens modal)
- **Steps:**
    1. Defines callback `on_server_added()`
    2. Opens CronSSHModal
    3. On result: Calls `add_server_to_tree()` with values
- **Goal:** Start process for adding server

##### `add_server_to_tree(name, host, port, username, password, crontab_user)`

- **Input:** Server details
- **Output:** None (adds to tree and storage)
- **Steps:**
    1. Generates server_id: `username@host:crontab_user`
    2. Checks if server_id exists
    3. Builds server_info dictionary
    4. Adds leaf to tree
    5. Refreshes tree
    6. Calls `save_servers()`
- **Goal:** Add new server to configuration

##### `action_delete_server()`

- **Input:** None (uses selected node)
- **Output:** None (deletes server)
- **Steps:**
    1. Gets cursor_node from tree
    2. Validates it's a server node
    3. Gets server_info
    4. Defines callback `on_delete_confirmed()`
    5. Opens CronDeleteConfirmation modal
    6. On confirmation:
        - Disconnects if connected
        - Deletes from dictionary
        - Removes node from tree
        - Saves changes
- **Goal:** Delete server with confirmation

---

### 5. CronDeleteConfirmation (CronDeleteConfirmation.py)

**Purpose:** Modal for confirming deletion of jobs or servers.

#### Functions:

##### `__init__(job, cron, remote, ssh_client, server, message, crontab_user)`

- **Input:** Context for deletion
- **Output:** Modal instance
- **Goal:** Initialize confirmation dialog

##### `compose()`

- **Input:** None
- **Output:** ComposeResult with message and buttons
- **Steps:**
    1. Determines message based on:
        - Custom message if provided
        - Server deletion if server provided
        - Job deletion if job provided
        - Generic message otherwise
    2. Creates Grid with Label and buttons (Delete/Cancel)
- **Goal:** Display confirmation dialog

##### `on_button_pressed(event)`

- **Input:** `event` - Button.Pressed event
- **Output:** None (deletes or cancels)
- **Steps:**
    1. If Cancel: Dismiss with False
    2. If Delete and job exists:
        1. Removes job from cron with `cron.remove(job)`
        2. If remote: Calls `write_remote_crontab()`
        3. Otherwise: Writes with `cron.write()`
    3. Dismiss with True
- **Goal:** Execute deletion on confirmation

##### `write_remote_crontab()`

- **Input:** None
- **Output:** Boolean (success)
- **Steps:**
    1. Renders crontab
    2. Constructs SSH command
    3. Writes to remote crontab
    4. Checks exit status
    5. Returns success/failure
- **Goal:** Update remote crontab after deletion

---

### 6. CronEncrypt (CronEncrypt.py)

**Purpose:** Encrypt and decrypt passwords for secure storage.

#### Algorithms:

##### `get_or_create_key()`

- **Input:** None
- **Output:** Encryption key (bytes)
- **Steps:**
    1. Creates `~/.config/cronboard/` if doesn't exist
    2. Checks if `secret.key` exists
    3. If not:
        1. Generates new Fernet key with `Fernet.generate_key()`
        2. Writes to file
        3. Sets file permissions to 0o600 (owner read/write only)
    4. If exists:
        - Reads key from file
    5. Returns key
- **Goal:** Ensure persistent encryption key per user

##### `encrypt_password(password)`

- **Input:** `password` - Plaintext password (string)
- **Output:** Encrypted token (string)
- **Steps:**
    1. Checks if password is empty
    2. If empty: Returns empty string
    3. Encodes password to bytes
    4. Encrypts with Fernet
    5. Decodes to string for storage
    6. Returns encrypted token
- **Algorithm:** Fernet (symmetric encryption with AES-128-CBC)
- **Goal:** Convert plaintext to encrypted format

##### `decrypt_password(token)`

- **Input:** `token` - Encrypted password (string)
- **Output:** Decrypted password (string)
- **Steps:**
    1. Checks if token is empty
    2. If empty: Returns empty string
    3. Encodes token to bytes
    4. Decrypts with Fernet
    5. Decodes to string
    6. Returns decrypted password
- **Goal:** Convert encrypted format to plaintext

**Security Features:**

- Uses Fernet (symmetric encryption based on AES-128-CBC)
- Key file protected with 0o600 permissions
- Passwords never stored in plaintext on disk
- Each installation has unique key

---

### 7. CronSSHModal (CronSSHModal.py)

**Purpose:** Modal for adding new SSH servers.

#### Functions:

##### `compose()`

- **Input:** None
- **Output:** ComposeResult with input fields
- **Steps:**
    1. Creates Grid container
    2. Adds Input fields for:
        - Hostname (format: host:port)
        - Username
        - Password (with password=True for masking)
        - Crontab user (optional)
    3. Adds information labels
    4. Adds buttons (Add Server/Cancel)
- **Goal:** Collect server details

##### `on_input_changed(event)`

- **Input:** `event` - Input.Changed event
- **Output:** None (removes error messages)
- **Steps:**
    1. Removes existing error labels
- **Goal:** Reset error messages on change

##### `on_button_pressed(event)`

- **Input:** `event` - Button.Pressed event
- **Output:** None (returns server data or cancels)
- **Steps:**
    1. If Cancel: Dismiss with False
    2. If Add Server:
        1. Gets values from all input fields
        2. Parses hostname:port with `split(':')`
        3. Converts port to int
        4. On ValueError: Shows error "Invalid host format"
        5. Builds server dictionary with:
            - hostname, port, username, password
            - ssh_key=True if no password
            - crontab_user if provided
        6. Dismiss with server dictionary
- **Goal:** Validate and return server configuration

---

### 8. CronTree (CronTree.py)

**Purpose:** Custom Tree widget with Vim-like navigation.

#### Functions:

##### `__init__(*args, **kwargs)`

- **Input:** Standard Tree arguments
- **Output:** CronTree instance
- **Goal:** Initialize tree with custom bindings

**Key Bindings:**

- `j` → cursor_down (Down)
- `k` → cursor_up (Up)

**Purpose:** Provide Vim users with familiar navigation

---

## Data Flow

### Local Cron Job Creation:

1. User presses 'c' in CronTable
2. CronTable calls `app.action_create_cronjob()` with local cron
3. App opens CronCreator modal
4. User fills in fields (expression, command, identificator)
5. Real-time validation with `expression_description()`
6. On Save: `on_button_pressed()` validates input
7. Creates new job with `cron.new()`
8. Sets expression with `job.setall()`
9. Writes with `cron.write()`
10. Modal closes and table refreshes

### Remote Cron Job Creation:

1-3. Same as local, but with SSH parameters
4-6. Same as local 7. Creates job in SSH cron object 8. Sets expression 9. `write_cron_changes()` renders crontab 10. Executes `crontab -` via SSH 11. Writes content to stdin 12. Checks exit status 13. Modal closes and remote table refreshes

### Server Connection:

1. User adds server with 'a' in CronServers
2. CronSSHModal collects host, port, username, password/key
3. Server saved in servers.toml with encrypted password
4. User presses 'c' to connect
5. `connect_to_server()` creates Paramiko SSHClient
6. Loads system host keys
7. Connects with password or key
8. `show_cron_table_for_server()` creates remote CronTable
9. CronTable executes `crontab -l` via SSH
10. Parses output and displays in table

### Pause/Resume Cron Job:

1. User selects job and presses 'p'
2. `action_pause_cronjob()` gets row data
3. Finds matching job in crontab
4. Toggles status with `job.enable(False/True)`
5. If local: Writes with `cron.write()`
6. If remote: Calls `write_remote_crontab()`
7. Table reloads with updated status

---

## Error Handling

### Validation:

- **Cron expressions:** Validated with python-crontab's `setall()`, ValueError raised on invalid format
- **SSH connection:** Handles AuthenticationException and general exceptions
- **Decryption:** Try-catch on decryption, fallback to None
- **Remote crontab:** Checks exit status and stderr for errors

### User Feedback:

- Real-time cron description (green for valid, red for invalid)
- Notifications for connections, errors and success
- Error labels in modals on invalid input

---

## Security

### Passwords:

- Encrypted with Fernet (AES-128-CBC)
- Key stored in `~/.config/cronboard/secret.key` with 0o600
- Never stored in plaintext

### SSH:

- Uses system host keys (`~/.ssh/known_hosts`)
- WarningPolicy for unknown hosts
- Supports both password and key-based authentication

### Configuration:

- Stored in `~/.config/cronboard/`
- TOML format for readability
- Per-user configuration

---

## Dependencies and Libraries

### Core Libraries:

- **textual** (6.2.1+): TUI framework for terminal UI
- **python-crontab** (3.3.0+): Crontab parsing and manipulation
- **cron-descriptor** (2.0.6+): Conversion to human-readable text
- **paramiko** (4.0.0+): SSH client for remote connections
- **cryptography (via Fernet)**: Password encryption
- **croniter** (6.0.0+): Cron schedule calculations
- **tomlkit** (0.13.3+): TOML parsing and writing

### Helper Modules:

- **bcrypt** (5.0.0+): Password hashing (dependency)
- **dt-croniter** (6.0.1+): Datetime support for croniter

---

## Testing

The project includes pytest setup with:

- **pytest** (8.4.2+)
- **pytest-asyncio** (1.2.0+)

Test files located in `src/test/cronboard_test.py`.

---

## Command-Line Interface

### Main Commands:

#### CronBoard App:

- `Ctrl+Q` - Quit application
- `Tab` - Switch panel/focus

#### CronTable:

- `h/l` - Left/right (Vim-style)
- `j/k` - Down/up (Vim-style)
- `c` - Create new cron job
- `e` - Edit selected job
- `D` - Delete selected job
- `p` - Pause/resume job
- `r` - Refresh table

#### CronServers:

- `a` - Add server
- `c` - Connect to selected server
- `d` - Disconnect from server
- `D` - Delete server
- `j/k` - Navigate tree

---

## Configuration Files

### `~/.config/cronboard/config.toml`

```toml
theme = "catppuccin-mocha"
```

### `~/.config/cronboard/servers.toml`

```toml
[username@hostname:crontab_user]
name = "username@hostname"
host = "hostname"
port = 22
username = "username"
encrypted_password = "encrypted_token_here"
ssh_key = false
connected = false
crontab_user = "username"
```

### `~/.config/cronboard/secret.key`

Binary file with Fernet encryption key (auto-generated).

---

## Conclusion

Cronboard is a comprehensive solution for cron management that combines simple local handling with powerful remote SSH functionality. Through proper validation, real-time feedback and secure password storage, it provides a user-friendly experience while maintaining security and reliability.

The architecture is modular with clear responsibilities: app.py coordinates, widgets handle UI, and encryption secures data. All components work together through well-defined interfaces and callback patterns.
