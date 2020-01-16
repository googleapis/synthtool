{% set group_id = metadata['repo']['distribution_name'].split(':')|first -%}
{% set artifact_id = metadata['repo']['distribution_name'].split(':')|last -%}
{% set repo_short = metadata['repo']['repo'].split('/')|last -%}
# Google Cloud Java Client for {{metadata['repo']['name_pretty']}}

Java idiomatic client for [{{metadata['repo']['name_pretty']}}][api-reference].

[![Maven][maven-version-image]][maven-version-link]
![Stability][stability-image]

- [Product Documentation][product-docs]
- [Client Library Documentation][javadocs]
{% if metadata['repo']['release_level'] in ['alpha', 'beta'] %}
> Note: This client is a work-in-progress, and may occasionally
> make backwards-incompatible changes.
{% endif %}
## Quickstart

If you are using Maven, add this to your pom.xml file
```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.google.cloud</groupId>
      <artifactId>libraries-bom</artifactId>
      <version>{{ metadata['latest_bom_version'] }}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>

<dependencies>
  <dependency>
    <groupId>{{ group_id }}</groupId>
    <artifactId>{{ artifact_id }}</artifactId>
  </dependency>
</dependencies>
```

If you are using Gradle, add this to your dependencies
[//]: # ({x-version-update-start:{{ artifact_id }}:released})
```Groovy
compile '{{ group_id }}:{{ artifact_id }}:{{ metadata['latest_version'] }}'
```
If you are using SBT, add this to your dependencies
```Scala
libraryDependencies += "{{ group_id }}" % "{{ artifact_id }}" % "{{ metadata['latest_version'] }}"
```
[//]: # ({x-version-update-end})

## Authentication

See the [Authentication][authentication] section in the base directory's README.

## About {{metadata['repo']['name_pretty']}}

{{ metadata['repo']['api_description'] }}

See the [{{metadata['repo']['name_pretty']}} client library docs][javadocs] to learn how to
use this {{metadata['repo']['name_pretty']}} Client Library.

## Getting Started

### Prerequisites

You will need a [Google Developers Console][developer-console] project with the
{{metadata['repo']['name_pretty']}} [API enabled][enable-api]. [Follow these instructions][create-project] to get your
project set up. You will also need to set up the local development environment by
[installing the Google Cloud SDK][cloud-sdk] and running the following commands in command line:
`gcloud auth login` and `gcloud config set project [YOUR PROJECT ID]`.

### Installation and setup

You'll need to obtain the `{{ artifact_id }}` library.  See the [Quickstart](#quickstart) section
to add `{{ artifact_id }}` as a dependency in your code.

## Troubleshooting

To get help, follow the instructions in the [shared Troubleshooting document][troubleshooting].

{% if metadata['repo']['transport'] -%}
## Transport

{% if metadata['repo']['transport'] == 'grpc' -%}
{{metadata['repo']['name_pretty']}} uses gRPC for the transport layer.
{% elif metadata['repo']['transport'] == 'http' -%}
{{metadata['repo']['name_pretty']}} uses HTTP/JSON for the transport layer.
{% elif metadata['repo']['transport'] == 'both' -%}
{{metadata['repo']['name_pretty']}} uses both gRPC and HTTP/JSON for the transport layer.
{% endif %}
{% endif -%}

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

## CI Status

Java Version | Status
------------ | ------
Java 7 | [![Kokoro CI][kokoro-badge-image-1]][kokoro-badge-link-1]
Java 8 | [![Kokoro CI][kokoro-badge-image-2]][kokoro-badge-link-2]
Java 8 OSX | [![Kokoro CI][kokoro-badge-image-3]][kokoro-badge-link-3]
Java 8 Windows | [![Kokoro CI][kokoro-badge-image-4]][kokoro-badge-link-4]
Java 11 | [![Kokoro CI][kokoro-badge-image-5]][kokoro-badge-link-5]

[api-reference]: {{metadata['repo']['api_reference']}}
[product-docs]: {{metadata['repo']['product_documentation']}}
[javadocs]: {{metadata['repo']['client_documentation']}}
[kokoro-badge-image-1]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java7.svg
[kokoro-badge-link-1]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java7.html
[kokoro-badge-image-2]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java8.svg
[kokoro-badge-link-2]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java8.html
[kokoro-badge-image-3]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java8-osx.svg
[kokoro-badge-link-3]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java8-osx.html
[kokoro-badge-image-4]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java8-win.svg
[kokoro-badge-link-4]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java8-win.html
[kokoro-badge-image-5]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java11.svg
[kokoro-badge-link-5]: http://storage.googleapis.com/cloud-devrel-public/java/badges/{{ repo_short }}/java11.html
[stability-image]: https://img.shields.io/badge/stability-{% if metadata['repo']['release_level'] == 'ga' %}ga-green{% elif metadata['repo']['release_level'] == 'beta' %}beta-yellow{% elif metadata['repo']['release_level'] == 'alpha' %}alpha-orange{% else %}unknown-red{% endif %}
[maven-version-image]: https://img.shields.io/maven-central/v/com.google.cloud/google-cloud-{{metadata['repo']['name']}}.svg
[maven-version-link]: https://search.maven.org/search?q=g:com.google.cloud%20AND%20a:google-cloud-{{metadata['repo']['name']}}&core=gav
[authentication]: https://github.com/googleapis/google-cloud-java#authentication
[developer-console]: https://console.developers.google.com/
[enable-api]: https://console.cloud.google.com/flows/enableapi?apiid={{ metadata['repo']['api_id'] }}
[create-project]: https://cloud.google.com/resource-manager/docs/creating-managing-projects
[cloud-sdk]: https://cloud.google.com/sdk/
[troubleshooting]: https://github.com/googleapis/google-cloud-common/blob/master/troubleshooting/readme.md#troubleshooting
[contributing]: https://github.com/{{metadata['repo']['repo']}}/blob/master/CONTRIBUTING.md
[code-of-conduct]: https://github.com/{{metadata['repo']['repo']}}/blob/master/CODE_OF_CONDUCT.md#contributor-code-of-conduct
[license]: https://github.com/{{metadata['repo']['repo']}}/blob/master/LICENSE