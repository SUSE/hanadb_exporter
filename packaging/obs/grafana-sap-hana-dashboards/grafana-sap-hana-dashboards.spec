#
# Copyright 2020 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
Name:           grafana-sap-hana-dashboards
# Version will be processed via set_version source service
Version:        0
Release:        0
License:        Apache-2.0
Summary:        Grafana Dashboards displaying metrics about SAP HANA databases.
Group:          System/Monitoring
Url:            https://github.com/SUSE/hanadb_exporter
Source:         %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       grafana-sap-providers
BuildRequires:  grafana-sap-providers

%description
Grafana Dashboards displaying metrics about SAP HANA databases.

%prep
%setup -q

%build

%install
install -dm0755 %{buildroot}%{_localstatedir}/lib/grafana/dashboards/sles4sap
install -m644 dashboards/*.json %{buildroot}%{_localstatedir}/lib/grafana/dashboards/sles4sap

%files
%defattr(-,root,root)
%doc dashboards/README.md
%license LICENSE
%attr(0755,grafana,grafana) %dir %{_localstatedir}/lib/grafana/dashboards/sles4sap
%attr(0644,grafana,grafana) %config %{_localstatedir}/lib/grafana/dashboards/sles4sap/*

%changelog
