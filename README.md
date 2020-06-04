# SynthTool (for client libraries)

This repository contains two, related tools for generating source code for
Google Cloud client libraries.

## Synthtool

Synthtool is a library of common templates and code that makes generating
source code easier.  With synthtool, the source code for an API can be generated
in 10 lines of code or less.  For an example, see 
[googleapis/java-asset/synth.py](https://github.com/googleapis/java-asset/blob/master/synth.py).

More details about Synthtool can be found in its [README](./synthtool/README.md).

## Autosynth

Autosynth automatically runs nightly or more frequently.  It finds and runs
synth.py scripts like
[googleapis/java-asset/synth.py](https://github.com/googleapis/java-asset/blob/master/synth.py),
collects the generated code, and creates a new pull request like
[this one](https://github.com/googleapis/java-asset/pull/180) if the generated
code differs.

## Autosynth & Synthtool

Autosynth and Synthtool communicate with each other via a file protocol
described [here](./synthtool/protos/README.md).
