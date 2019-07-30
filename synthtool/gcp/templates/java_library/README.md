# Google Cloud Java Client for {{metadata['repo']['name_pretty']}}

Java idiomatic client for [{{metadata['repo']['name_pretty']}}][api-reference].

[![Kokoro CI][kokoro-badge-image]][kokoro-badge-link]
[![Maven][maven-version-image]][maven-version-link]

- [Product Documentation][product-docs]
- [Client Library Documentation][javadocs]

> Note: This client is a work-in-progress, and may occasionally
> make backwards-incompatible changes.

## Quickstart

[//]: # ({x-version-update-start:{{metadata['repo']['name']}}:released})
If you are using Maven, add this to your pom.xml file
```xml
<dependency>
  <groupId>com.google.cloud</groupId>
  <artifactId>{{metadata['repo']['name']}}</artifactId>
  <version>0.102.0-beta</version>
</dependency>
```
If you are using Gradle, add this to your dependencies
```Groovy
compile 'com.google.cloud:{{metadata['repo']['name']}}:0.102.0-beta'
```
If you are using SBT, add this to your dependencies
```Scala
libraryDependencies += "com.google.cloud" % "{{metadata['repo']['name']}}" % "0.102.0-beta"
```
[//]: # ({x-version-update-end})

## Authentication

See the [Authentication][authentication] section in the base directory's README.

## About {{metadata['repo']['name_pretty']}}

[{{metadata['repo']['name_pretty']}}][api-reference] is a suite of Machine Learning products.

See the [[{{metadata['repo']['name_pretty']}}][api-reference] client library docs][javadocs] to learn how to
use this {{metadata['repo']['name_pretty']}} Client Library.

## Getting Started

### Prerequisites

You will need a [Google Developers Console][developer-console] project with the
{{metadata['repo']['name_pretty']}} API enabled. [Follow these instructions][create-project] to get your
project set up. You will also need to set up the local development environment by
[installing the Google Cloud SDK][cloud-sdk] and running the following commands in command line:
`gcloud auth login` and `gcloud config set project [YOUR PROJECT ID]`.

### Installation and setup

You'll need to obtain the `{{metadata['repo']['name']}}` library.  See the [Quickstart](#quickstart) section
to add `{{metadata['repo']['name']}}` as a dependency in your code.

## Troubleshooting

To get help, follow the instructions in the [shared Troubleshooting document][troubleshooting].

## Transport

{{metadata['repo']['name_pretty']}} uses gRPC for the transport layer.

## Java Versions

Java 7 or above is required for using this client.

## Versioning

This library follows [Semantic Versioning](http://semver.org/).

It is currently in major version zero (``0.y.z``), which means that anything may change at any time
and the public API should not be considered stable.

## Contributing

Contributions to this library are always welcome and highly encouraged.

See [CONTRIBUTING.md][contributing] documentation for more information on how to get started.

Please note that this project is released with a Contributor Code of Conduct. By participating in
this project you agree to abide by its terms. See [Code of Conduct][code-of-conduct] for more
information.

## License

Apache 2.0 - See [LICENSE][license] for more information.

[api-reference]: {{metadata['repo']['api_reference']}}
[product-docs]: {{metadata['repo']['product_documentation']}}
[javadocs]: {{metadata['repo']['client_documentation']}}
[kokoro-badge-image]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{metadata['repo']['repo_short']}}/master.svg
[kokoro-badge-link]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{metadata['repo']['repo_short']}}/master.html
[maven-version-image]: https://img.shields.io/maven-central/v/com.google.cloud/{{metadata['repo']['name']}}.svg
[maven-version-link]: https://search.maven.org/search?q=g:com.google.cloud%20AND%20a:{{metadata['repo']['name']}}&core=gav
[authentication]: https://github.com/googleapis/google-cloud-java#authentication
[developer-console]: https://console.developers.google.com/
[create-project]: https://cloud.google.com/resource-manager/docs/creating-managing-projects
[cloud-sdk]: https://cloud.google.com/sdk/
[troubleshooting]: https://github.com/googleapis/google-cloud-common/blob/master/troubleshooting/readme.md#troubleshooting

[contributing]: https://github.com/{{metadata['repo']['repo']}}/blob/master/CONTRIBUTING.md
[code-of-conduct]: https://github.com/{{metadata['repo']['repo']}}/blob/master/CODE_OF_CONDUCT.md#contributor-code-of-conduct
[license]: https://github.com/{{metadata['repo']['repo']}}/blob/master/LICENSE