#
# spec file for package prometheus-hanadb_exporter
#
# Copyright (c) 2022-2024 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#

%if 0%{?suse_version} < 1500
%bcond_with test
%else
%bcond_without test
%endif

%define _prefix /usr
%define oldsyscondir /etc
%define _sysconfdir %{_prefix}/etc
%define pythons python3

%{?!python_module:%define python_module() python3-%{**}}
Name:           prometheus-hanadb_exporter
Version:        0
Release:        0
Summary:        SAP HANA database metrics exporter
License:        Apache-2.0
Group:          System/Monitoring
URL:            https://github.com/SUSE/hanadb_exporter
Source:        %{name}-%{version}.tar.gz
%if %{with test}
BuildRequires:  %{python_module pytest}
BuildRequires:  %{python_module boto3}
BuildRequires:  %{python_module certifi}
%endif
BuildRequires:  %{python_module setuptools}
BuildRequires:  python-rpm-macros
Provides:       hanadb_exporter = %{version}-%{release}
BuildRequires:  fdupes
BuildRequires:  systemd-rpm-macros
%{?systemd_requires}
Requires:       %{python_module prometheus_client} >= 0.6.0
Requires:       %{python_module shaptools}
Requires:       %{python_module boto3}
Recommends:     %{python_module certifi}
BuildArch:      noarch

%description
SAP HANA database metrics exporter

%define shortname hanadb_exporter

%prep
%setup -q -n %{name}-%{version}

%build
%python_build

%install
%python_install
%python_expand %fdupes %{buildroot}%{$python_sitelib}
# do not install tests
%python_expand rm -r %{buildroot}%{$python_sitelib}/tests

# Add daemon files
mkdir -p %{buildroot}%{oldsyscondir}/%{shortname}
mkdir -p %{buildroot}%{_sysconfdir}/%{shortname}
install -D -m 644 daemon/%{shortname}@.service %{buildroot}%{_unitdir}/%{name}@.service

install -D -m 0644 config.json.example %{buildroot}%{_docdir}/%{name}/config.json.example
install -D -m 0644 metrics.json %{buildroot}%{_docdir}/%{name}/metrics.json
install -D -m 0644 logging_config.ini %{buildroot}%{_docdir}/%{name}/logging_config.ini
install -D -m 755 bin/supportconfig-hanadb_exporter %{buildroot}%{_prefix}/lib/supportconfig/plugins/%{shortname}

%post
%service_add_post %{name}@.service
rm -rf  %{_sysconfdir}/%{shortname}/*
ln -s %{_docdir}/%{name}/config.json.example %{_sysconfdir}/%{shortname}/config.json.example
ln -s %{_docdir}/%{name}/metrics.json  %{_sysconfdir}/%{shortname}/metrics.json
ln -s %{_docdir}/%{name}/logging_config.ini  %{_sysconfdir}/%{shortname}/logging_config.ini

%pre
%service_add_pre %{name}@.service

%preun
%service_del_preun %{name}@.service

%postun
%service_del_postun %{name}@.service

%if %{with test}
%check
pytest tests
%endif

%files
%defattr(-,root,root,-)
%if 0%{?sle_version:1} && 0%{?sle_version} < 120300
%doc README.md docs/METRICS.md LICENSE
%else
%doc README.md docs/METRICS.md
%license LICENSE
%endif
%{python_sitelib}/*
%{_bindir}/%{shortname}

%dir %{_sysconfdir}
%dir %{oldsyscondir}/%{shortname}
%dir %{_sysconfdir}/%{shortname}
%{_docdir}/%{name}/config.json.example
%{_docdir}/%{name}/metrics.json
%{_docdir}/%{name}/logging_config.ini
%{_unitdir}/%{name}@.service
%dir %{_prefix}/lib/supportconfig
%dir %{_prefix}/lib/supportconfig/plugins
%{_prefix}/lib/supportconfig/plugins/%{shortname}

%changelog
