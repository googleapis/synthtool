Welcome to the Autosynth and Synthtool dockerfile.

Quick Refresher:

    Synthtool generates client client library source code.

    Autosynth runs Synthtool across a long list of repositories, and runs multiple times
    to determine which upstream change triggered a change in the generated library
    source code.

    More details here:
    https://github.com/googleapis/synthtool/blob/master/README.md

You can use this dockerfile to manually run synthtool on a repo.  Here's how:

$ cd my-repo-dir
$ docker run \
    -v /full/path/to/my/repo:/repo \
    -it gcr.io/cloud-devrel-kokoro-resources/synthtool:latest \
    /bin/bash
/# cd /repo
/# python -m synthtool 
    
