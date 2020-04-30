# How to run the integration tests.

Integration tests depend on the live state of repos on github, so they break
everyday.

So, to run the tests to see if your changes actually broke something, follow these
steps:

1.  `git checkout master`
2.  `git checkout -b refresh`
3.  `./refresh-golden-files.sh`
4.  `git commit -am refresh`
5.  `git merge my-development-branch`
6.  `python -m pytest .`