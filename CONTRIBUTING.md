# How to contribute

## OBS Releases

The CI will automatically interact with SUSE's [Open Build Service](https://build.opensuse.org): the master branch will be kept in sync with the `server:monitoring` project (the development upstream), while a new Submit Request against the `openSUSE:Factory` project (the stable downstream) will can be triggered by publishing a new GitHub release or pushing a new Git tag.
 
When releasing to `openSUSE:Factory`, please ensure that tags always follow the [SemVer](https://semver.org/) scheme, and that [the changelog](prometheus-hanadb_exporter.changes) contains a new entry.
 
 
