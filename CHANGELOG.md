# Changelog

[PyPI History][1]

[1]: https://pypi.org/project/gcp-synthtool/#history

## 0.4.0

### Implementation Changes

- Fix tracked paths issue by preferentially matching the longest path (#36)
- set Jinja2 option to keep new line char at EOF (#35)

### New Features

- (nodejs) read repo_name and package_name from package.json (#34)
- Add Ruby-specific tools (#22)
- Adding php templates (#33)
- Add git sources to tracked_paths (#31)

### Internal / Testing Changes

- Fix trampoline script

## 0.3.1

### Implementation Changes
- nodejs: remove lock file workflows from CI (#28)

## 0.3.0

### New Features
- Support optional merge function during copy (#21)
- add more templates for nodejs (#23)

### Internal / Testing Changes
- Use new Nox (#24)

## 0.2.0

### Implementation Changes

- Fix #8 by expanding/globbing paths to excludes param (#12)

### New Features

- add template for .circleci config for node libraries (#6, #7, #17)
- Warn when copy/move/replace can not find any sources (#4)
- Add warning for non-replacement
- Add an update checker.
- added get_workflow_name.py (#15)

### Dependencies

### Documentation

- Update README to explain how to use templating. (#18)

### Internal / Testing Changes

- Add kokoro config

## 0.1.0

Initial release

