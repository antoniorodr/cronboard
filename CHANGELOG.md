# Changelog

All notable changes to this project will be documented in this file.

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

[0.2.2]: https://github.com/antoniorodr/cronboard/releases/tag/v0.2.2
[0.2.1]: https://github.com/antoniorodr/cronboard/releases/tag/v0.2.1
[0.2.0]: https://github.com/antoniorodr/cronboard/releases/tag/v0.2.0
[0.1.2]: https://github.com/antoniorodr/cronboard/releases/tag/v0.1.2
[0.1.1]: https://github.com/antoniorodr/cronboard/releases/tag/v0.1.1
[0.1.0]: https://github.com/antoniorodr/cronboard/releases/tag/v0.1.0
