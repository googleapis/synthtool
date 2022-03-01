![Diagram of relationship between Autosynth, Synthtool, and Github](./images/flow.png)

# SynthTool (for client libraries)

This repository contains two, related tools for generating source code for
Google Cloud client libraries.

## Synthtool

Synthtool is a library of common templates and code that makes generating
source code easier.  With synthtool, the source code for an API can be generated
in 10 lines of code or less.  For an example, see 
[googleapis/java-asset/synth.py](https://github.com/googleapis/java-asset/blob/master/synth.py).

More details about Synthtool can be found in its [README](./synthtool/README.md).
