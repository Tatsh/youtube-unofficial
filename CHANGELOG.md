<!-- markdownlint-configure-file {"MD024": { "siblings_only": true } } -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.1/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.4.0] - 2026-04-26

### Added

- New `build_youtube_session()` function for creating an async HTTP session with browser cookies.
- New `session` module exposing session-creation utilities.
- Support for Python 3.10 and 3.11.
- Expanded test coverage for the client.

### Changed

- Switched from `requests` to `niquests` for HTTP; the entire Python API is now fully async.
- `YouTubeClient` constructor now accepts an `AsyncSession` instead of browser name and profile
  strings.
- All client methods are now coroutines and all generators are now async generators.
- CLI commands are unchanged; async calls are wrapped internally with `anyio.run`.
- Replaced internal assertions with explicit exceptions for playlist API calls, session validation,
  and continuation handling so missing keys, unexpected response shapes, and absent cookies surface
  as `KeyError`, `RuntimeError`, or `TypeError` instead of `AssertionError`.
- Trimmed the playlist `ytcfg` guard to be less strict.
- Replaced documentation badges.

### Fixed

- Snapcraft binary path.

### Removed

- `requests` dependency, replaced by `niquests-cache`.

## [0.3.1]

### Added

- Attestation.

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

[unreleased]: https://github.com/Tatsh/youtube-unofficial/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/Tatsh/youtube-unofficial/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/Tatsh/youtube-unofficial/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/Tatsh/youtube-unofficial/compare/v0.2.0...v0.3.0
