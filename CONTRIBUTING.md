# How to contribute

## OBS Packaging

The CI will automatically interact with SUSE's [Open Build Service](https://build.opensuse.org): the `main` branch will be kept in sync with the `network:ha-clustering:sap-deployments:devel` project.

### Publishing the Exporter RPM in openSUSE code stream.

For the exporter only, a new Submit Request against the `server:monitoring` project can be triggered by publishing a new GitHub release.

Please ensure that tags always follow the [SemVer] scheme, and the text of the release adheres to the [_keep a changelog_](https://keepachangelog.com/) format.

When accepting Submit Requests against `server:monitoring`, you can contextually forward them to the `openSUSE:Factory` project.

### Publishing Grafana Dashboards
 
While Grafana dashboard are not continuously deployed like the exporter, the [OBS development package](https://build.opensuse.org/package/show/network:ha-clustering:sap-deployments:devel/grafana-sap-hana-dashboards) is still kept in sync with the `main` branch of this repository.  
GitHub releases do not apply in this case, they are only used for the exporter; the dashboards RPM version number is instead hard-coded in the OBS source services configuration.

To publish a new release:
- update the numerical prefix of the `versionformat` field in the [_service](packaging/obs/grafana-sap-hana-dashboards/_service) file;
- add an entry to the [changelog](packaging/obs/grafana-sap-hana-dashboards/grafana-sap-hana-dashboards.changes) file;
- commit these changes directly in the `main` branch;
- perform a Submit Request via [`osc`] manually:  
  `osc sr network:ha-clustering:sap-deployments:devel grafana-sap-hana-dashboards openSUSE:Factory`

 
### Publishing RPMs in OBS manually 

For both the exporter and the dashboards, assuming you have  configured [`osc`] already, you can use the same make targets used in the CI to produce a local OBS package working directory.

The following:
```
make exporter-obs-workdir
```
will checkout the exporter OBS package and prepare a new OBS commit in the `build/obs` directory.

You can use the `OSB_PROJECT`, `REPOSITORY`, `VERSION` and `REVISION` environment variables to change the behaviour these make targets.

By default, the current Git working directory is used to infer the values of `VERSION` and `REVISION`, which are used by OBS source services to generate a compressed archive of the sources.

For example, if wanted to update the RPM package in your own OBS branch with the latest sources from a Git feature branch in your own GitHub fork, you might do the following:
```bash
git checkout feature/xyz
git push johndoe feature/xyz # don't forget to push changes in your own fork
export OBS_PROJECT=home:JohnDoe
export REPOSITORY=johndoe/my_forked_repo
make clean
make exporter-obs-workdir
``` 
This will prepare to commit in the `home:JohnDoe/my_forked_repo` OBS package by checking out the `feature/xyz` branch from `github.com/johndoe/my_forked_repo`, updating the version number of the RPM spec file, and producing a compressed archive of the sources.

To actually perform the OBS commit, run: 
```bash
make exporter-obs-commit
```

Note that that actual releases may also involve an intermediate step that updates the changelog automatically, but this is only used when triggering the CI/CD via GitHub releases.

The equivalent targets for the dashboard package are `make dashboards-obs-workdir` and `make dashboards-obs-commit`

[SemVer]: https://semver.org
[`osc`]: https://en.opensuse.org/openSUSE:OSC

### Note about SemVer usage

Please be aware that RPM doesn't allow hyphens in the version number:  `~` can been used as a replacement, although it's not entirely compliant with the SemVer spec.

For more information, please refer to: https://github.com/semver/semver/issues/145
