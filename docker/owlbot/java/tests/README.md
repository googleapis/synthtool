# Java OwlBot Image Tests

## New Client

This suite tests the bootstrapping of a new client. In this case, we are
generating the initial artifacts. We expect the post-processor to create all
the necessary `pom.xml` files for the detected artifacts.

## New Version

This suite tests the addition of a new service version. There are existing
`pom.xml` files that need to be modified to add the new modules/artifacts.
