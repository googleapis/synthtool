# Changelog

[PyPI History][1]

[1]: https://pypi.org/project/gcp-synthtool/#history

## 2018.11.27

11-27-2018 10:09 PST


### Implementation Changes
- add noxfile template ([#144](https://github.com/GoogleCloudPlatform/synthtool/pull/144))
- Lazily clone googleapis{-private} ([#140](https://github.com/GoogleCloudPlatform/synthtool/pull/140))
- Report Artman info to metadata ([#136](https://github.com/GoogleCloudPlatform/synthtool/pull/136))
- Add metadata reporting for Git sources. ([#132](https://github.com/GoogleCloudPlatform/synthtool/pull/132))
- Construct the artman instance only once. ([#135](https://github.com/GoogleCloudPlatform/synthtool/pull/135))
- Harden replace ([#129](https://github.com/GoogleCloudPlatform/synthtool/pull/129))
- Add basic metadata protos ([#127](https://github.com/GoogleCloudPlatform/synthtool/pull/127))
- Update eslintignore rules for nodejs ([#125](https://github.com/GoogleCloudPlatform/synthtool/pull/125))

### New Features
- Add ability to format java code with a custom google-java-format version ([#145](https://github.com/GoogleCloudPlatform/synthtool/pull/145))
- Warn when running the synthesis script directly ([#142](https://github.com/GoogleCloudPlatform/synthtool/pull/142))
- Add option to change metadata output location ([#141](https://github.com/GoogleCloudPlatform/synthtool/pull/141))
- Add initial python templates ([#131](https://github.com/GoogleCloudPlatform/synthtool/pull/131))

## 2018.11.08

11-08-2018 12:36 PST

### Implementation Changes

- Show stdout for docker pull ([#121](https://github.com/googleapis/synthtool/pull/121))
- Prefer https URLs for cloning from GitHub, add SYNTHTOOL_USE_SSH to use ssh ([#120](https://github.com/googleapis/synthtool/pull/120))
- Drop the PR template for nodejs ([#117](https://github.com/googleapis/synthtool/pull/117))
- Update github issue templates ([#116](https://github.com/googleapis/synthtool/pull/116))
- Incude build/ in eslint ignore ([#115](https://github.com/googleapis/synthtool/pull/115))
- feat: make npm link work for system tests ([#114](https://github.com/googleapis/synthtool/pull/114))
- fix: update nodejs issue templates ([#112](https://github.com/googleapis/synthtool/pull/112))
- feat(node): add node11 test env ([#110](https://github.com/googleapis/synthtool/pull/110))
- fix(node): remove store_artifact for windows builds ([#103](https://github.com/googleapis/synthtool/pull/103))
- feat(node): upload code coverage for continuous builds too ([#102](https://github.com/googleapis/synthtool/pull/102))
- docs: update the new issue templates for nodejs ([#101](https://github.com/googleapis/synthtool/pull/101))
- node: use latest npm for Windows ([#119](https://github.com/googleapis/synthtool/pull/119))
- Stop installing Artman outside of Docker. ([#99](https://github.com/googleapis/synthtool/pull/99))

### New Features

- Add option to specify local googleapis directory ([#100](https://github.com/googleapis/synthtool/pull/100))

### Internal / Testing Changes

- Enable the autorelease reporter ([#122](https://github.com/googleapis/synthtool/pull/122))
- Fix lint error ([#113](https://github.com/googleapis/synthtool/pull/113))

## 0.10.0

10-17-2018 12:23 PDT

### Implementation Changes
- fix(node): move fetch codecov token to node8/test.cfg ([#92](https://github.com/GoogleCloudPlatform/synthtool/pull/92))
- fix(node): bring in codecov master token into nodejs builds ([#88](https://github.com/GoogleCloudPlatform/synthtool/pull/88))
- nodejs: add test_project arg for templates ([#63](https://github.com/GoogleCloudPlatform/synthtool/pull/63))
- npm bundled in win VM has a known issue with fsevents, upgrade it ([#86](https://github.com/GoogleCloudPlatform/synthtool/pull/86))
- pre test hooks usually sets secrets, set +x to prevent them from leaking ([#84](https://github.com/GoogleCloudPlatform/synthtool/pull/84))
- chore(node): remove .appveyor.yaml from templating ([#82](https://github.com/GoogleCloudPlatform/synthtool/pull/82))
- Add optional env var for npm install timeout ([#79](https://github.com/GoogleCloudPlatform/synthtool/pull/79))
- Use prefer-const in the .eslintrc.yaml ([#78](https://github.com/GoogleCloudPlatform/synthtool/pull/78))

### New Features
- Add discogapic generator ([#90](https://github.com/GoogleCloudPlatform/synthtool/pull/90))
- feat(node): Migrate uploading of test coverage report from CircleCI to Kokoro ([#87](https://github.com/GoogleCloudPlatform/synthtool/pull/87))
- feat(node): match different styles of repository string ([#83](https://github.com/GoogleCloudPlatform/synthtool/pull/83))
- feat(node): allow pre-samples-test.sh hook ([#81](https://github.com/GoogleCloudPlatform/synthtool/pull/81))

### Documentation
- Fixed repo org in CONTRIBUTING template ([#95](https://github.com/GoogleCloudPlatform/synthtool/pull/95))

### Internal / Testing Changes
- Remove nox-automation uninstall from build.sh ([#97](https://github.com/GoogleCloudPlatform/synthtool/pull/97))
- Use new Nox ([#80](https://github.com/GoogleCloudPlatform/synthtool/pull/80))

## 0.9.0

### New Features
- Make synthtool an executable ([#74](https://github.com/GoogleCloudPlatform/synthtool/pull/74))

### Internal / Testing Changes
- Run system and samples test on Kokoro for nodejs repos ([#75](https://github.com/GoogleCloudPlatform/synthtool/pull/75))
- Update eslint rules for nodejs ([#73](https://github.com/GoogleCloudPlatform/synthtool/pull/73))

## 0.8.0

### Implementation Changes
- Correct a wrong path in the PHP template ([#65](https://github.com/GoogleCloudPlatform/synthtool/pull/65))

### Internal / Testing Changes
- Add release build files ([#68](https://github.com/GoogleCloudPlatform/synthtool/pull/68))

## 0.7.1

### Implementation Changes
- node: add arg `source_location` to .jsdoc.js ([#62](https://github.com/GoogleCloudPlatform/synthtool/pull/62))
- Fix error on missing ~/.cache
- nodejs: use Docker node version that runs in non-root ([#59](https://github.com/GoogleCloudPlatform/synthtool/pull/59))
- fix: circle.yml decrypt multiple ([#58](https://github.com/GoogleCloudPlatform/synthtool/pull/58))
- add GCLOUD_PROJECT env var to config.yml ([#56](https://github.com/GoogleCloudPlatform/synthtool/pull/56))
- chmod +x for npm-install-retry.js ([#55](https://github.com/GoogleCloudPlatform/synthtool/pull/55))
- node: decrypt all service-account keys ([#54](https://github.com/GoogleCloudPlatform/synthtool/pull/54))
- Update CircleCI config for npm to retry install ([#53](https://github.com/GoogleCloudPlatform/synthtool/pull/53))

### Internal / Testing Changes
- nodejs: export GCLOUD_PROJECT in system-test ([#60](https://github.com/GoogleCloudPlatform/synthtool/pull/60))
- node: add a pretest hook on system test ([#57](https://github.com/GoogleCloudPlatform/synthtool/pull/57))

## 0.7.0

### Implementation Changes
- Move: excludes arg paths should be relative to source, not destination (#48)
- Update CircleCI config for nodejs (#50)
- fix: CircleCI config should not try to decrypt if no key is present (#49)

### New Features
- feat: preserve file mode in templates (#47)

## 0.6.2

### Implementation Changes

- Use manifest.in for package data

## 0.6.1

### Implementation Changes

- Include subdirectories under node_library/.kokoro (#43)

## 0.6.0

### Implementation Changes

- Run `npm install` before publishing (#41)
- Add missing resources

### New Features

- Allow synthtool to build java Gapic clients (#40)

## 0.5.0

### New Features
- Add Kokoro configs for nodejs repos (#38)

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

