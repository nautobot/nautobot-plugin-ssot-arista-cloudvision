# Changelog

## v1.4.0 - 2022-10-21

### Added

- #101 - Added support for the Device Lifecycle Management plug-in. Addresses #87.
- #99 - Added support for getting interface description.
- #103 - Added support for importing IP Addresses from CloudVision. Addresses #52.
- #108 - Added support for hostname parsing to dynamically create Site/Role. #51

### Fixed

- #101 - Fix Platform creation to be single item instead of matching DeviceType.
- #101 - Corrected Nautobot adapter load method
- #101 - Ensure only CustomFields with `arista_` prepend are loaded. Addresses #95.
- #101 - Validated enabledState key in chassis interface. Addresses #102.
- #101 - Fixed MAC address string to match CVP so diff is idempotent.
- #104 - Fixes display of plugin settings. Addresses #86.

### Performance

- #101 - Optimized query for Devices to improve load times. Addresses #93.

### Refactor

- #104 - Refactored Jobs to use load source/target adapter methods for performance metrics.

## v1.3.0 - 2022-10-13

### Added

- #94 - Added support for importing interfaces from CloudVision.
- #94 - Added support for CloudvisionApi to be used as context manager.
- #94 - Added unit tests covering multiple CloudVision utility methods an

### Fixed

- #94 - Ensured that device ID is imported as the Nautobot Device serial.

## v1.2.1 - 2022-08-31

### Fixed

- #85 - Refactor project to current SSoT pattern. Addressed various linter complaints.

## v1.2.0 - 2022-8-19

### Added

- #79 Add support for Token with On Prem CloudVision
- #82 Import all devices option

### Changed

- #65 Update Nautobot Job names
- #70 Update signals.py

### Fixed

- #74 Cloudvision dependency pinned

## v1.0.3 - 2021-10-21

### Added

- #56 Add config option for gRPC port

### Changed

- #57 - Add the name for the section in Nautobot jobs and update SSoT plugin dep to v1.0.1

### Fixed

- #55 Raise error when auth fails to on-prem CVP

## v1.0.2 - 2021-09-20

### Added

- #44 Customization of CVaaS URL

### Changed

- #43 Container tag is skipped for sync

### Fixed

- delete_devices_on_sync documentation

## v1.0.1 - 2021-08-24

### Added

- Default values for import variables when not specified in configuration file.

## v1.0.0 - 2021-08-11

Initial release
