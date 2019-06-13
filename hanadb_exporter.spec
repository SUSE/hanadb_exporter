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

Name:           hanadb_exporter
Version:        0.2.0
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
Requires:       python3-shaptools >= 0.2.1
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

%if %{with test}
%check
pytest tests
%endif

%files
%if 0%{?sle_version:1} && 0%{?sle_version} < 120300
%doc README.md LICENSE
%else
%doc README.md
%license LICENSE
%endif
%{python3_sitelib}/*
%{_bindir}/hanadb_exporter

%changelog
