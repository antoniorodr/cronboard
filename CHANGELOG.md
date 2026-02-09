# Changelog

All notable changes to this project will be documented in this file.

## [0.4.1] - 09.02.2026

Thanks to @it-education-md for this fix.

### Fixed

- Fixed a bug in **Add Server** where host-only input (without port) could raise an `UnboundLocalError`. Fixes #16.
  - The parser now safely accepts both `host` and `host:port`
  - Defaults to port **22** when no port is provided
  - Validates port range and surfaces clear input errors instead of crashing

### Tests

- Added pytest coverage for server parsing in `src/test/cronboard_test.py`

## [0.4.0] - 11.11.2025

### Added

- Autocompletion for the `command` field when creating or editing cron jobs, when typing a `PATH` which exists in the system. It closes #1. Merged PR #14. Thanks to @Zaloog for this!

### Changed

- Small change on the `pyproject.toml` file to avoid configuration errors when building the package. Merged PR #13. Thanks @micisse for reporting and solving this!

## [0.3.1] - 24.10.2025

### Changed

- Color enhancements for better visibility and user experience.
- Color change when the cron job is paused and active to improve differentiation.
- Changes in the algorithm when pausing, resuming, deleting and editing cron jobs to take into account the cron jobs with "No ID" label.
- Label "Identificator" changed to "ID" for better clarity and spacing.

## [0.3.0] - 22.10.2025

### Added

- Possibility to connect to remote servers via SSH with a user, but choosing another user (`crontab user`) to manage cron jobs from. To this, the user you login with must have `sudo` privileges.
- Some tests to control the correct functioning of `Cronboard`.

### Changed

- Refactored some functions to improve code readability and maintainability.
- How the server is displayed on the tree view, adding the `crontab user` for better identification.

### Breaking Changes

- The server bookmark format has changed to include the `crontab user` field. Old server bookmarks will maybe not work as expected.
- The server file located in `~/.config/cronboard/servers.toml` will need to be updated to include the new `crontab user` field for each server. Another option is to delete the servers from the tree view and re-add them.

## [0.2.2] - 17.10.2025

### Changed

- Cronboard will now keep the `special strings` as it is when writing back to the crontab, instead of converting them to their equivalent standard cron expression.

## [0.2.1] - 17.10.2025

### Added

- Support for `special strings` in cron expressions, such as `@weekly`, `@yearly`, `@monthly`, as well as the descriptions.

### Fixed

- Fixed missing `tomlkit` dependency in the `prpyoject.toml` file. Closes #6.

## [0.2.0] - 15.10.2025

### Modified

- Redesigned the SSH connection interface for better user experience.
- Refactored codebase to make the new SSH connection interface possible.

### Added

- New `server bookmark` tab to manage and quickly connect to SSH servers.
- Add and delete servers from the tree view.
- Connect to a server by clicking `c` in the tree view after adding it.
- Column view for visibility of the server cron jobs on the same tab.
- Servers are saved in a `TOML` file located at `~/.config/cronboard/servers.toml`, with the password field encrypted.

## [0.1.2] - 13.10.2025

### Added

- Connection to remote servers via SSH using SSH keys.

## [0.1.1] - 11.10.2025

### Added

- Possibility to disconnect from the current server.

## [0.1.0] - 10.10.2025

Initial Release.

### Added

Initial release with the following features:

- Check cron jobs
- Create cron jobs, with feedback on cron expression validity and "translation" to human-readable format
- Pause and resume cron jobs
- Edit cron jobs
- Delete cron jobs
- Check "last run" and "next run" times, in a formatted way

[0.4.0]: https://github.com/antoniorodr/cronboard/releases/tag/v0.3.1
[0.3.1]: https://github.com/antoniorodr/cronboard/releases/tag/v0.3.1
[0.3.0]: https://github.com/antoniorodr/cronboard/releases/tag/v0.3.0
[0.2.2]: https://github.com/antoniorodr/cronboard/releases/tag/v0.2.2
[0.2.1]: https://github.com/antoniorodr/cronboard/releases/tag/v0.2.1
[0.2.0]: https://github.com/antoniorodr/cronboard/releases/tag/v0.2.0
[0.1.2]: https://github.com/antoniorodr/cronboard/releases/tag/v0.1.2
[0.1.1]: https://github.com/antoniorodr/cronboard/releases/tag/v0.1.1
[0.1.0]: https://github.com/antoniorodr/cronboard/releases/tag/v0.1.0
