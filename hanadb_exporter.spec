#
# spec file for package hanadb_exporter
#
# Copyright (c) 2019 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/

%if 0%{?suse_version} < 1500
%bcond_with test
%else
%bcond_without test
%endif

# Compat macro for new _fillupdir macro introduced in Nov 2017
%if ! %{defined _fillupdir}
  %define _fillupdir /var/adm/fillup-templates
%endif

Name:           hanadb_exporter
Version:        0.5.1
Release:        0
Summary:        SAP HANA database metrics exporter
License:        Apache-2.0
Group:          Development/Languages/Python
Url:            https://github.com/SUSE/hanadb_exporter
Source:         hanadb_exporter-%{version}.tar.gz
%if %{with test}
BuildRequires:  python3-mock
BuildRequires:  python3-pytest
%endif
BuildRequires:  python3-setuptools
BuildRequires:  fdupes
BuildRequires:  systemd-rpm-macros
%{?systemd_requires}
Requires:       python3-shaptools >= 0.3.2
Requires:       python3-prometheus_client >= 0.6.0
BuildArch:      noarch

%description
SAP HANA database metrics exporter

%prep
%setup -q -n hanadb_exporter-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --root %{buildroot} --prefix=%{_prefix}
%fdupes %{buildroot}%{python3_sitelib}
# do not install tests
rm -r %{buildroot}%{python3_sitelib}/tests

# Add daemon files
mkdir -p %{buildroot}%{_sysconfdir}/hanadb_exporter
install -D -m 644 daemon/hanadb_exporter@.service %{buildroot}%{_unitdir}/hanadb_exporter@.service

mkdir -p %{buildroot}%{_fillupdir}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -D -m 0644 daemon/hanadb_exporter.sysconfig %{buildroot}%{_fillupdir}/sysconfig.hanadb_exporter
install -D -m 0644 config.json.example %{buildroot}%{_docdir}/hanadb_exporter/config.json.example
install -D -m 0644 metrics.json %{buildroot}%{_docdir}/hanadb_exporter/metrics.json
install -D -m 0644 logging_config.ini %{buildroot}%{_docdir}/hanadb_exporter/logging_config.ini

%post
%service_add_post hanadb_exporter@.service
if [ ! -e %{_sysconfdir}/sysconfig/hanadb_exporter ]; then
    %fillup_only hanadb_exporter
fi
rm -rf  %{_sysconfdir}/hanadb_exporter/*
ln -s %{_docdir}/hanadb_exporter/config.json.example %{_sysconfdir}/hanadb_exporter/config.json.example
ln -s %{_docdir}/hanadb_exporter/metrics.json  %{_sysconfdir}/hanadb_exporter/metrics.json
ln -s %{_docdir}/hanadb_exporter/logging_config.ini  %{_sysconfdir}/hanadb_exporter/logging_config.ini

%pre
%service_add_pre hanadb_exporter@.service

%preun
%service_del_preun -n hanadb_exporter@.service

%postun
%service_del_postun -n hanadb_exporter@.service

%if %{with test}
%check
pytest tests
%endif

%files
%if 0%{?sle_version:1} && 0%{?sle_version} < 120300
%doc README.md docs/METRICS.md LICENSE
%else
%doc README.md docs/METRICS.md
%license LICENSE
%endif
%{python3_sitelib}/*
%{_bindir}/hanadb_exporter

%dir %{_sysconfdir}/hanadb_exporter
%{_docdir}/hanadb_exporter/config.json.example
%{_docdir}/hanadb_exporter/metrics.json
%{_docdir}/hanadb_exporter/logging_config.ini
%{_fillupdir}/sysconfig.hanadb_exporter
%{_unitdir}/hanadb_exporter@.service

%changelog
