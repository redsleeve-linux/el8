%global __remake_config 1

Name:    opensm
Version: 3.3.21
Release: 2%{?dist}
Summary: OpenIB InfiniBand Subnet Manager and management utilities
Group:   System Environment/Daemons
License: GPLv2 or BSD
Url:     https://github.com/linux-rdma/opensm

Source0: https://github.com/linux-rdma/opensm/releases/download/%{version}/%{name}-%{version}.tar.gz
Source2: opensm.logrotate
Source4: opensm.sysconfig
Source5: opensm.service
Source6: opensm.launch
Source7: opensm.rwtab
Source8: opensm.partitions
Patch1:  opensm-3.3.13-prefix.patch

BuildRequires: libibumad-devel, systemd, systemd-units
BuildRequires: bison, flex, byacc, gcc
%if %{__remake_config}
BuildRequires: libtool, autoconf, automake
%endif
Requires: %{name}-libs%{?_isa} = %{version}-%{release}, logrotate, rdma
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
# RDMA is not currently built on 32-bit ARM: #1484155
ExcludeArch: s390 %{arm}

%description
OpenSM is the OpenIB project's Subnet Manager for Infiniband networks.
The subnet manager is run as a system daemon on one of the machines in
the infiniband fabric to manage the fabric's routing state.  This package
also contains various tools for diagnosing and testing Infiniband networks
that can be used from any machine and do not need to be run on a machine
running the opensm daemon.

%package libs
Summary: Libraries used by opensm and included utilities
Group: System Environment/Libraries

%description libs
Shared libraries for Infiniband user space access

%package devel
Summary: Development files for the opensm-libs libraries
Group: Development/Libraries
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
Development environment for the opensm libraries

%package static
Summary: Static version of the opensm libraries
Group: Development/Libraries
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
%description static
Static version of opensm libraries

%prep
%setup -q
%patch1 -p1

%build
%if %{__remake_config}
./autogen.sh
%endif
%configure --with-opensm-conf-sub-dir=rdma CFLAGS="$CFLAGS -fno-strict-aliasing"
make %{?_smp_mflags}
cd opensm
./opensm -c ../opensm-%{version}.conf

%install
make install DESTDIR=%{buildroot}
# remove unpackaged files from the buildroot
rm -f %{buildroot}%{_libdir}/*.la
rm -fr %{buildroot}%{_sysconfdir}/init.d
install -D -m644 opensm-%{version}.conf %{buildroot}%{_sysconfdir}/rdma/opensm.conf
install -D -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/opensm
install -D -m644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/opensm
install -D -m644 %{SOURCE5} %{buildroot}%{_unitdir}/opensm.service
install -D -m755 %{SOURCE6} %{buildroot}%{_libexecdir}/opensm-launch
install -D -m644 %{SOURCE7} %{buildroot}%{_sysconfdir}/rwtab.d/opensm
install -D -m644 %{SOURCE8} %{buildroot}%{_sysconfdir}/rdma/partitions.conf
mkdir -p ${RPM_BUILD_ROOT}/var/cache/opensm

%post
%systemd_post opensm.service

%preun
%systemd_preun opensm.service

%postun
if [ -d /var/cache/opensm ]; then
	rm -fr /var/cache/opensm
fi
%systemd_postun_with_restart opensm.service

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%dir /var/cache/opensm
%{_sbindir}/*
%{_mandir}/*/*
%{_unitdir}/*
%{_libexecdir}/*
%config(noreplace) %{_sysconfdir}/logrotate.d/opensm
%config(noreplace) %{_sysconfdir}/rdma/opensm.conf
%config(noreplace) %{_sysconfdir}/rdma/partitions.conf
%config(noreplace) %{_sysconfdir}/sysconfig/opensm
%{_sysconfdir}/rwtab.d/opensm
%doc AUTHORS ChangeLog INSTALL README NEWS
%license COPYING

%files libs
%{_libdir}/lib*.so.*

%files devel
%{_libdir}/lib*.so
%{_includedir}/infiniband

%files static
%{_libdir}/lib*.a

%changelog
* Fri Jan 11 2019 Honggang Li <honli@redhat.com> - 3.3.21-2
- Restore the 'subnet_prefix' option
- Resolves: bz1664575

* Mon Sep 24 2018 Honggang Li <honli@redhat.com> - 3.3.21-1
- Rebase to latest upstream release 3.3.21
- Resolves: bz1602645

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.20-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Feb  1 2018 Honggang Li <honli@redhat.com> - 3.3.20-7
- Fix BuildRequires
- Fix preuninstall script
- Resolves: bz1540934

* Mon Aug 28 2017 Honggang Li <honli@redhat.com> - 3.3.20-6
- Add support for s309x

* Sat Aug 26 2017 Honggang Li <honli@redhat.com> - 3.3.20-5
- Disable support for ARM32.
- Resolves: bz1484155

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.20-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.20-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jun 10 2016 Honggang Li <honli@redhat.com> - 3.3.20-1
- Update to latest upstream release
- Resolves: bz1344691

* Wed Mar 16 2016 Doug Ledford <dledford@redhat.com> - 3.3.19-1
- Update to latest upstream release
- Incorporate features from RHEL opensm
- Resolves: bz1124202

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.17-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.17-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.17-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.17-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Michael Schwendt <mschwendt@fedoraproject.org> - 3.3.17-2
- Don't include manual page directories (#1089412).
- Use standard group Development/Libraries in library devel packages.
- Use %%?_isa in base package dependencies.

* Mon Mar 17 2014 Peter Robinson <pbrobinson@fedoraproject.org> 3.3.17-1
- Update to 3.3.17

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.15-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Mar 25 2013 Doug Ledford <dledford@redhat.com> - 3.3.15-6
- Oops, forgot to remove the -B option to opensm when starting it

* Mon Mar 25 2013 Doug Ledford <dledford@redhat.com> - 3.3.15-5
- Drop the old sysv init script
- Fix opensm-launch to restart opensm in a loop.  This works around the
  fact that systemd starts opensm so early that we very well might not have
  sync on the link yet.  Without the physical link being up, opensm exits
  immediately.  This way opensm will get restarted every 30 seconds until
  sync is active on the link or until the opensm service is stopped.
- Always install the newly generated opensm-%%{version}.conf as opensm.conf
- Make the launch work properly in the event that no GUIDs are set and
  there are no numbered config files

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.15-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Dec 05 2012 Doug Ledford <dledford@redhat.com> - 3.3.15-3
- Fix startup on read only root
- Update default config file
- Resolves: bz817591

* Wed Dec 05 2012 Doug Ledford <dledford@redhat.com> - 3.3.15-2
- More tweaks to systemd setup (proper scriptlets now)
- More tweaks to old sysv init script support (fix Requires)

* Tue Nov 27 2012 Doug Ledford <dledford@redhat.com> - 3.3.15-1
- Update to latest upstream release
- Update to systemd startup

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.13-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Mar 13 2012 Doug Ledford <dledford@redhat.com> - 3.3.13-2
- Fix the config file comment in the opensm init script
- Resolves: bz802727

* Tue Feb 28 2012 Doug Ledford <dledford@redhat.com> - 3.3.13-1
- Update to latest upstream version
- Fix a minor issue in init scripts that would cause systemd to try and
  start/stop things in the wrong order
- Add a patch to allow us to specify the subnet prefix on the command line

* Tue Jan 03 2012 Doug Ledford <dledford@redhat.com> - 3.3.12-1
- Update to latest upstream version

* Mon Aug 15 2011 Kalev Lember <kalevlember@gmail.com> - 3.3.9-2
- Rebuilt for rpm bug #728707

* Wed Jul 20 2011 Doug Ledford <dledford@redhat.com> - 3.3.9-1
- Update to latest upstream version
- Add /etc/sysconfig/opensm for use by opensm init script
- Enable the ability to start more than one instance of opensm for multiple
  fabric support
- Enable the ability to start opensm with a priority other than default for
  support of backup opensm instances

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Mar 08 2010 Doug Ledford <dledford@redhat.com> - 3.3.5-1
- Update to latest upstream release.  We need various defines in ib_types.h
  for the latest ibutils package to build properly, and the latest ibutils
  package is needed because we found licensing problems in the older
  tarballs during review.

* Mon Jan 11 2010 Doug Ledford <dledford@redhat.com> - 3.3.3-2
- ExcludeArch s390(x) as there's no hardware support there

* Thu Dec 03 2009 Doug Ledford <dledford@redhat.com> - 3.3.3-1
- Update to latest upstream release
- Minor tweaks to init script for LSB compliance

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 20 2009 Doug Ledford <dledford@redhat.com> - 3.3.2-1
- Update to latest upstream version

* Wed Apr 22 2009 Doug Ledford <dledford@redhat.com> - 3.3.1-1
- Update to latest upstream version

* Fri Mar 06 2009 Caolán McNamara <caolanm@redhat.com> - 3.2.1-3
- fix bare elifs to rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jun 08 2008 Doug Ledford <dledford@redhat.com> - 3.2.1-1
- Initial package for Fedora review process