# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Add typing to tests by @antoniorodr
- Add more test on CronDeleteConfirmation by @RunningKuma
- Add more test about CronSSHModal by @RunningKuma
- Add terminal trove badge local by @antoniorodr
- Add README for recording real GIFs in docs/images by @bitloi
- Add favicon to zensical docs by @antoniorodr
- Add nix flake by @antoniorodr

### Changed
- Merge pull request #38 from RunningKuma/feat/test_complement by @antoniorodr in [#38](https://github.com/antoniorodr/cronboard/pull/38)
- Consolidate test setup by moving helper functions to conftest.py by @RunningKuma
- Merge branch 'main' into feat/test_complement by @RunningKuma
- Move `create_event` to `confetst` to reduce duplidcation in test. by @RunningKuma
- Reduce repeated setup in modal tests by @RunningKuma
- Fix the test to keep it DRY by @RunningKuma
- Update terminal trove badge from readme by @antoniorodr
- Delete unused assets (logo and terminal trove) by @antoniorodr
- Delete logo from readme by @antoniorodr
- Delete back to top from readme by @antoniorodr
- Update readme by @antoniorodr
- Update logo size by @antoniorodr
- Delete extra readme.html by @antoniorodr
- Update readme by @antoniorodr
- Update readme with icons by @antoniorodr
- Update license on pyproject by @antoniorodr
- Update readme by @antoniorodr
- Update release and tests workflow by @antoniorodr
- Update readme by @antoniorodr
- Update license by @antoniorodr
- Update release workflow by @antoniorodr
- Update notify job on PR workflow by @antoniorodr
- Merge branch 'docs/issue-32-improve-documentation' by @antoniorodr
- Replace gif placeholders for good ones by @antoniorodr in [#34](https://github.com/antoniorodr/cronboard/pull/34)
- Improve documentation with detailed explanations and GIF examples by @bitloi
- Create the necessary files and workflows for the no autopilot action by @antoniorodr
- Edit docs workflow by @antoniorodr
- Update docs workflow by @antoniorodr
- Update readme by @antoniorodr
- Update pyproject and uv.lock by @antoniorodr
- Move project_explanation to root by @antoniorodr
- Create zensical documentation by @antoniorodr
- Create workflow to publish the documentation to Zensical by @antoniorodr
- Fix typo on readme file by @antoniorodr
- Update readme with nix installation by @antoniorodr
- Update flake and pyproject by @antoniorodr
- Update nix flake and create nix workflow by @antoniorodr
- Update release workflow by @antoniorodr
- Update changelog links by @antoniorodr

### Fixed
- Fix wrong year for Terminal Trove Tool of the week by @antoniorodr
- Fix a typo by @antoniorodr

### New Contributors
* @RunningKuma made their first contribution
* @bitloi made their first contribution

## [0.5.1] - 2026-03-06

### Added
- Add release workflow by @antoniorodr
- Add pytest-mock to the uv.lock file and contributing by @antoniorodr

### Changed
- Update changelog and pyproject by @antoniorodr
- Update workflows to add telegram notification by @antoniorodr
- Move stale.yml into workflows by @antoniorodr
- Update app fixture to mock cronboard app by @antoniorodr
- Create github actions for testing PR and merge by @antoniorodr
- Update uv.lock by @antoniorodr
- Move the tests to the root by @antoniorodr
- Refactor the test file into multiple files by module by @antoniorodr
- Move dev dependencies to "dev" dependency-groups by @antoniorodr

## [main] - 2026-03-04

### Changed
- Update readme and contributing by @antoniorodr
- Update pyproject for coverage by @antoniorodr

## [0.5.0] - 2026-03-04

### Added
- Add q as an additional way to close app by @Zaloog
- Add clear search binding by @antoniorodr
- Add next and prev match on check_action by @antoniorodr

### Changed
- Update changelog and pyproject by @antoniorodr
- Merge branch 'lg/fix-app-closing-on-modal' by @antoniorodr in [#27](https://github.com/antoniorodr/cronboard/pull/27)
- Fix closing not working on modal screens by @Zaloog
- Merge branch 'feat/search' by @antoniorodr
- Delete unused imports by @antoniorodr
- Modify tests to use the parameter app by @antoniorodr
- Create conftest with pytest configuration by @antoniorodr
- Merge branch 'feat/search' by @antoniorodr
- Update readme with search function by @antoniorodr
- Merge branch 'feat/search' by @antoniorodr
- Update CronTable to fetch the search term from CronInputSearch by @antoniorodr
- Create new modal CronInputSearch to search cronjobs by @antoniorodr
- Update tcss to style the new CronInputSearch modal by @antoniorodr

## [0.4.3] - 2026-02-23

### Added
- Add escape binding also to ModalDeleteScreen by @Zaloog
- Added escape binding to close ModalScreen by @Zaloog
- Add workflow for mirroring by @antoniorodr

### Changed
- Update changelog and pyproject for the new version by @antoniorodr
- Fix format after merge by @antoniorodr
- Merge branch 'lg/fix-error-on-empty-edit' by @antoniorodr in [#23](https://github.com/antoniorodr/cronboard/pull/23)
- Adjusted Binding visibility by @Zaloog
- Fix format after merging by @antoniorodr
- Merge branch 'lg/close-modal-on-escape' by @antoniorodr in [#22](https://github.com/antoniorodr/cronboard/pull/22)
- Undo license change. Back to MIT. by @antoniorodr
- Update LICENSE to Apache 2.0 non AI by @antoniorodr
- Delete aur workflow by @antoniorodr

## [0.4.2] - 2026-02-17

### Added
- Add editorconfig file to the project by @antoniorodr
- Add new info to CONTRIBUTING.md by @antoniorodr

### Changed
- Update version pyproject by @antoniorodr
- Merge pull request #19 from antoniorodr/upt/dependencies by @antoniorodr in [#19](https://github.com/antoniorodr/cronboard/pull/19)
- Update dependencies by @antoniorodr
- Merge pull request #18 from antoniorodr/feat/editorconfig by @antoniorodr in [#18](https://github.com/antoniorodr/cronboard/pull/18)
- Update PKGBUILD and SRCINFO by @antoniorodr
- Update Changelog by @antoniorodr

## [0.4.1] - 2026-02-09

### Added
- Add stale.yml to automate closing and stale status by @antoniorodr

### Changed
- Change changelog and pyproject by @antoniorodr
- Update readme with the new bottle/formula by @antoniorodr
- Update readme to correctly show project size by @antoniorodr

### Fixed
- Validate host input in Add Server by @it-education-md in [#17](https://github.com/antoniorodr/cronboard/pull/17)

### New Contributors
* @it-education-md made their first contribution in [#17](https://github.com/antoniorodr/cronboard/pull/17)

## [0.4.0] - 2025-11-11

### Added
- Add autocompletion when creating cron jobs by @antoniorodr
- Add completion for three parts by @Zaloog
- Add initial autocompleter for command input by @Zaloog

### Changed
- Merge branch 'lg/create-command-autocompleter' by @antoniorodr in [#14](https://github.com/antoniorodr/cronboard/pull/14)
- Update gitignore by @antoniorodr
- Change banner and demo folder path by @antoniorodr
- Change link on Terminal Trove badge by @antoniorodr
- Update README: Terminal Trove tool of the week by @antoniorodr

### Fixed
- Fixing license metadata in pyproject.toml and add .gitignore file by @micisse in [#13](https://github.com/antoniorodr/cronboard/pull/13)

### Removed
- Remove unused dependencies and cleaned gitignore by @Zaloog

### New Contributors
* @Zaloog made their first contribution
* @micisse made their first contribution in [#13](https://github.com/antoniorodr/cronboard/pull/13)

## [0.3.1] - 2025-10-24

### Added
- Add documentation file in markdown by @antoniorodr

### Changed
- Update PKGBUILD and pyproject by @antoniorodr
- Change colors, identificator label and pause/delete/edit algorithm by @antoniorodr
- Update CONTRIBUTING file by @antoniorodr
- Update CONTRIBUTING.md file by @antoniorodr

## [0.3.0] - 2025-10-22

### Added
- Added possibility to choose crontab user by @antoniorodr
- Add sponsorship badget on README by @antoniorodr

### Changed
- Update PKGBUILD by @antoniorodr
- Update README file by @antoniorodr
- Create test file by @antoniorodr
- Merge pull request #9 from antoniorodr/antoniorodr-patch-1 by @antoniorodr in [#9](https://github.com/antoniorodr/cronboard/pull/9)
- Set GitHub Sponsors username to 'antoniorodr' by @antoniorodr
- Update README by @antoniorodr

## [0.2.2] - 2025-10-17

### Changed
- Change to behold the special expressions as it is when saving the cronjob by @antoniorodr
- Update README with new logo by @antoniorodr
- Update readme by @antoniorodr

## [0.2.1] - 2025-10-17

### Changed
- Update README for SSH by @antoniorodr
- Update PKGBUILD by @antoniorodr
- Update gif on README by @antoniorodr
- Update PKGBUILD and SRCINFO by @antoniorodr

### Fixed
- Fix tomlkit dependency and add support for special strings (@weekly etc) by @antoniorodr

## [0.2.0] - 2025-10-15

### Added
- Add .SRCINFO file to AUR by @antoniorodr

### Changed
- Merge branch 'servers_bookmarks' by @antoniorodr
- Redesign ssh connections tab by @antoniorodr
- Update README by @antoniorodr
- Create pkgbuild and workflow by @antoniorodr

## [0.1.2] - 2025-10-13

### Added
- Add ssh connection using ssh key by @antoniorodr
- Add bug and feature request templates by @antoniorodr
- Add changelog by @antoniorodr

### Changed
- Update asciinema gif by @antoniorodr
- Update readme with uv installation by @antoniorodr
- Fix CronBoard folder casing to lowercase by @antoniorodr
- Update readme with demo by @antoniorodr
- Change version function by @antoniorodr
- Small fix in version by @antoniorodr
- Update readme by @antoniorodr

## [0.1.1] - 2025-10-11

### Changed
- V0.1.1 release by @antoniorodr
- Update pyproject by @antoniorodr
- Update readme by @antoniorodr
- Update pyproject by @antoniorodr
- Update readme by @antoniorodr
- Change dependencies by @antoniorodr
- Update pyproject by @antoniorodr
- Project structure update by @antoniorodr
- Change email in code of conduct by @antoniorodr

## [0.1.0] - 2025-10-10

### Added
- Add SSH connection by @antoniorodr
- Add refresh after creation, edit and deletion of cronjobs by @antoniorodr
- Add different markdown files by @antoniorodr

### Changed
- Update readme by @antoniorodr
- Refactor by @antoniorodr
- Refactor cron parsing by @antoniorodr
- Create edit option and update readme by @antoniorodr
- Create dynamic tabs, deletion, creation and deactivation for cronjobs by @antoniorodr
- Initial commit by @antoniorodr

### Fixed
- Fix bug with error labels in ssh connection by @antoniorodr
- Fix cronjobs deletion on ssh by @antoniorodr
- Fix persistance creation in ssh by @antoniorodr

### New Contributors
* @antoniorodr made their first contribution

[unreleased]: https://github.com/antoniorodr/cronboard/compare/v0.5.1...HEAD
[0.5.1]: https://github.com/antoniorodr/cronboard/compare/main...v0.5.1
[main]: https://github.com/antoniorodr/cronboard/compare/v0.5.0...main
[0.5.0]: https://github.com/antoniorodr/cronboard/compare/v0.4.3...v0.5.0
[0.4.3]: https://github.com/antoniorodr/cronboard/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/antoniorodr/cronboard/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/antoniorodr/cronboard/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/antoniorodr/cronboard/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/antoniorodr/cronboard/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/antoniorodr/cronboard/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/antoniorodr/cronboard/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/antoniorodr/cronboard/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/antoniorodr/cronboard/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/antoniorodr/cronboard/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/antoniorodr/cronboard/compare/v0.1.0...v0.1.1

<!-- generated by git-cliff -->
