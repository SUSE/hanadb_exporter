# this is the what ends up in the RPM "Version" field and embedded in the --version CLI flag
VERSION ?= $(shell .ci/get_version_from_git.sh)

# this will be used as the build date by the Go compile task
DATE = $(shell date --iso-8601=seconds)

# if you want to release to OBS, this must be a remotely available Git reference
REVISION ?= $(shell git rev-parse --abbrev-ref HEAD)

# we only use this to comply with RPM changelog conventions at SUSE
AUTHOR ?= shap-staff@suse.de

# you can customize any of the following to build forks
OBS_PROJECT ?= network:ha-clustering:sap-deployments:devel
REPOSITORY ?= SUSE/hanadb_exporter

default: deps test

deps:
	python -m pip install --upgrade pip
	pip install tox

test:
	tox -e py

test-all:
	tox

static-checks:
	tox -e pylint

checks: test static-checks

coverage: tests/coverage.xml tests/htmlcov tests/.coverage
tests/coverage.xml tests/htmlcov tests/.coverage:
	tox -e coverage

clean:
	rm -rf .tox tests/{coverage.xml,.coverage,htmlcov} build

exporter-obs-workdir: build/obs/prometheus-hanadb_exporter
build/obs/prometheus-hanadb_exporter:
	@mkdir -p $@
	osc checkout $(OBS_PROJECT) prometheus-hanadb_exporter -o $@
	rm -f $@/*.tar.gz
	cp -rv packaging/obs/prometheus-hanadb_exporter/* $@/
# we interpolate environment variables in OBS _service file so that we control what is downloaded by the tar_scm source service
	sed -i 's~%%VERSION%%~$(VERSION)~' $@/_service
	sed -i 's~%%REVISION%%~$(REVISION)~' $@/_service
	sed -i 's~%%REPOSITORY%%~$(REPOSITORY)~' $@/_service
	cd $@; osc service runall

exporter-obs-changelog: exporter-obs-workdir
	.ci/gh_release_to_obs_changeset.py $(REPOSITORY) -a $(AUTHOR) -t $(REVISION) -f build/obs/prometheus-hanadb_exporter/prometheus-hanadb_exporter.changes

exporter-obs-commit: exporter-obs-workdir
	cd build/obs/prometheus-hanadb_exporter; osc addremove
	cd build/obs/prometheus-hanadb_exporter; osc commit -m "Update from git rev $(REVISION)"

dashboards-obs-workdir: build/obs/grafana-sap-hana-dashboards
build/obs/grafana-sap-hana-dashboards:
	@mkdir -p $@
	osc checkout $(OBS_PROJECT) grafana-sap-hana-dashboards -o $@
	rm -f $@/*.tar.gz
	cp -rv packaging/obs/grafana-sap-hana-dashboards/* $@/
# we interpolate environment variables in OBS _service file so that we control what is downloaded by the tar_scm source service
	sed -i 's~%%REVISION%%~$(REVISION)~' $@/_service
	sed -i 's~%%REPOSITORY%%~$(REPOSITORY)~' $@/_service
	cd $@; osc service runall

dashboards-obs-commit: dashboards-obs-workdir
	cd build/obs/grafana-sap-hana-dashboards; osc addremove
	cd build/obs/grafana-sap-hana-dashboards; osc commit -m "Update from git rev $(REVISION)"

.PHONY: checks clean coverage deps static-checks test test-all
