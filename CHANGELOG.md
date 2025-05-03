<!-- markdownlint-configure-file {"MD024": { "siblings_only": true } } -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0]

### Added

- Added man page.
- Added docs.
- Added tests.

### Fixed

- All broken commands.

### Changed

- Does authorised requests solely by getting cookies from a supported browser.
- Interface is now a single command `youtube` with subcommands.

### Removed

- Log in feature.
- 'Community' commands such as getting comments. These have moved to My Activity.
- Download commands. All of these can be achieved with yt-dlp alone now.
- Command to clear search history. Moved to My Activity.

[unreleased]: https://github.com/Tatsh/youtube-unofficial/compare/v0.3.0...HEAD
