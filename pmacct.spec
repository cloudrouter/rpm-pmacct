%global _hardened_build 1

%if ! 0%{?fedora} >= 23
%define _enable_ulog --enable-ulog
%define _use_ulog 1
%else
%define _use_ulog 0
%endif

Name:               pmacct
Version:            1.6.0
Release:            1%{?dist}
Summary:            Accounting and aggregation toolsuite for IPv4 and IPv6
License:            GPLv2+
Group:              Applications/Engineering
URL:                http://www.pmacct.net/
Source0:            http://www.pmacct.net/pmacct-%{version}.tar.gz
Source1:            nfacctd.service
Source2:            nfacctd
Source3:            pmacctd.service
Source4:            pmacctd
Source5:            sfacctd.service
Source6:            sfacctd
Source7:            uacctd.service
Source8:            uacctd

Patch1:             pmacct-fix-implicit-pointer-decl.diff

BuildRequires:      gcc
BuildRequires:      GeoIP-devel
BuildRequires:      libpcap-devel
BuildRequires:      libstdc++-static
BuildRequires:      make
BuildRequires:      mariadb-devel
BuildRequires:      pkgconfig
BuildRequires:      pkgconfig(geoip)
BuildRequires:      pkgconfig(jansson)
BuildRequires:      postgresql-devel
BuildRequires:      sqlite-devel >= 3.0.0
BuildRequires:      systemd

Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
pmacct is a small set of passive network monitoring tools to measure, account,
classify and aggregate IPv4 and IPv6 traffic; a pluggable and flexible
architecture allows to store the collected traffic data into memory tables or
SQL (MySQL, SQLite, PostgreSQL) databases. pmacct supports fully customizable
historical data breakdown, flow sampling, filtering and tagging, recovery
actions, and triggers. Libpcap, sFlow v2/v4/v5 and NetFlow v1/v5/v7/v8/v9 are
supported, both unicast and multicast. Also, a client program makes it easy to
export data to tools like RRDtool, GNUPlot, Net-SNMP, MRTG, and Cacti.

%prep
%autosetup -p1

# fix permissions
chmod -x sql/pmacct-*

%build
export CFLAGS="%{optflags} -Wno-return-type -Wno-error=format-security -Wmaybe-uninitialized"

%configure \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --prefix=%{_prefix} \
    --exec-prefix=%{_exec_prefix} \
    --sbindir=%{_sbindir} \
    --enable-v4-mapped \
    --enable-l2 \
    --enable-ipv6 \
    --enable-mysql \
    --enable-pgsql \
    --enable-sqlite3 \
    --enable-geoip \
    --enable-jansson \
    --enable-64bit \
    --enable-threads \
    %{?_enable_ulog}

make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install %{?_smp_mflags}

# install sample configuration files
install -Dp examples/nfacctd-sql_v2.conf.example %{buildroot}/%{_sysconfdir}/%{name}/nfacctd.conf
install -Dp examples/pmacctd-sql_v2.conf.example %{buildroot}/%{_sysconfdir}/%{name}/pmacctd.conf

# install systemd units
install -d %{buildroot}/%{_unitdir} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
install %{SOURCE1} %{SOURCE3} %{SOURCE5} %{buildroot}/%{_unitdir}
install %{SOURCE2} %{SOURCE4} %{SOURCE6} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}

%if 0%{?_use_ulog}
install %{SOURCE7} %{buildroot}/%{_unitdir}
install %{SOURCE8} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
%endif

%post
%systemd_post nfacctd.service
%systemd_post pmacctd.service
%systemd_post sfacctd.service
%if 0%{?_use_ulog}
%systemd_post uacctd.service
%endif

%preun
%systemd_preun nfacctd.service
%systemd_preun pmacctd.service
%systemd_preun sfacctd.service
%if 0%{?_use_ulog}
%systemd_preun uacctd.service
%endif

%postun
%systemd_postun_with_restart nfacctd.service
%systemd_postun_with_restart pmacctd.service
%systemd_postun_with_restart sfacctd.service
%if 0%{?_use_ulog}
%systemd_postun_with_restart uacctd.service
%endif


%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog CONFIG-KEYS COPYING FAQS QUICKSTART TOOLS UPGRADE
%doc docs examples sql
%{_bindir}/pmacct
%{_sbindir}/nfacctd
%{_sbindir}/pmacctd
%{_sbindir}/pmtelemetryd
%{_sbindir}/sfacctd
%if 0%{?_use_ulog}
%{_sbindir}/uacctd
%endif
%{_unitdir}/nfacctd.service
%{_unitdir}/pmacctd.service
%{_unitdir}/sfacctd.service
%if 0%{?_use_ulog}
%{_unitdir}/uacctd.service
%endif
%{_sysconfdir}/sysconfig/%{name}/nfacctd
%{_sysconfdir}/sysconfig/%{name}/pmacctd
%{_sysconfdir}/sysconfig/%{name}/sfacctd
%if 0%{?_use_ulog}
%{_sysconfdir}/sysconfig/%{name}/uacctd
%endif

%dir %{_sysconfdir}/pmacct
%attr(600,root,root) %config(noreplace) %{_sysconfdir}/pmacct/nfacctd.conf
%attr(600,root,root) %config(noreplace) %{_sysconfdir}/pmacct/pmacctd.conf

%changelog
* Mon Oct 17 2016 John Siegrist <john@complects.com> - 1.6.0-1
- Update to version 1.6.0
* Tue Dec 29 2015 John Siegrist <john@complects.com> - 1.5.2-3
- Conditionally disabled ULOG for newer versions of Fedora
- Disabled build Warnings as Errors that were causing failures.
* Mon Dec 21 2015 Arun Babu Neelicattu <arun.neelicattu@gmail.com> - 1.5.2-2
- Enable ULOG
* Sun Dec 13 2015 Arun Babu Neelicattu <arun.neelicattu@gmail.com> - 1.5.2-1
- Initial packaging based on OpenSUSE rpms packaged by Peter Nixon and available
  at http://download.opensuse.org/repositories/server:/monitoring/
