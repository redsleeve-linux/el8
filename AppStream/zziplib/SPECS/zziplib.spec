Summary: Lightweight library to easily extract data from zip files
Name: zziplib
Version: 0.13.68
Release: 7%{?dist}
License: LGPLv2+ or MPLv1.1
Group: Applications/Archiving
URL: http://zziplib.sourceforge.net/
Source: https://github.com/gdraheim/zziplib/archive/v%{version}.tar.gz

Patch100: zziplib-0.13.67-multilib.patch
Patch101: zziplib-0.13.67-multilib-32.patch

Patch1: 0001-FIX-port-documentation-scripts-to-python3.patch
Patch2: CVE-2018-7725.patch
#part1 also fixes #1545818 
Patch3: CVE-2018-7726.part1.patch
Patch4: CVE-2018-7726.part2.patch
Patch5: CVE-2018-7726.part3.patch
Patch6: CVE-2018-7727.patch

Patch7: CVE-2018-16548.part1.patch
Patch8: CVE-2018-16548.part2.patch
Patch9: CVE-2018-16548.part3.patch

Patch10: CVE-2018-17828.patch

BuildRequires: perl-interpreter
BuildRequires: python3-devel
BuildRequires: python3-six
BuildRequires: zip
BuildRequires: xmlto
BuildRequires: zlib-devel
BuildRequires: SDL-devel
BuildRequires: pkgconfig
#BuildRequires: autoconf
#BuildRequires: automake

%description
The zziplib library is intentionally lightweight, it offers the ability to
easily extract data from files archived in a single zip file. Applications
can bundle files into a single zip archive and access them. The implementation
is based only on the (free) subset of compression with the zlib algorithm
which is actually used by the zip/unzip tools.

%package utils
Summary: Utilities for the zziplib library
Group: Applications/Archiving
Requires: %{name}%{?_isa} = %{version}-%{release}

%description utils
The zziplib library is intentionally lightweight, it offers the ability to
easily extract data from files archived in a single zip file. Applications
can bundle files into a single zip archive and access them. The implementation
is based only on the (free) subset of compression with the zlib algorithm
which is actually used by the zip/unzip tools.

This packages contains all the utilities that come with the zziplib library.

%package devel
Summary: Development files for the zziplib library
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: pkgconfig
Requires: zlib-devel
Requires: SDL-devel

%description devel
The zziplib library is intentionally lightweight, it offers the ability to
easily extract data from files archived in a single zip file. Applications
can bundle files into a single zip archive and access them. The implementation
is based only on the (free) subset of compression with the zlib algorithm
which is actually used by the zip/unzip tools.

This package contains files required to build applications that will use the
zziplib library.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1

pathfix.py -i %{__python3} -pn docs

%build
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%configure \
    --disable-static \
    --enable-sdl \
    --enable-frame-pointer \
    --enable-builddir=_builddir
# Remove rpath on 64bit archs
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' */libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' */libtool
# Only patch generated _config.h on non-i686 and armv7hl
# These platforms have a correct _config.h already
cd _builddir
%ifarch i686 armv7hl
%apply_patch %{PATCH101} -p2
%endif
%ifnarch i686 armv7hl
%apply_patch %{PATCH100} -p2
%endif
cd ..

%{__make} %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc docs/COPYING* ChangeLog README TODO
%{_libdir}/*.so.*

%files utils
%{_bindir}/*

%files devel
%doc docs/README.SDL docs/*.htm docs/*.html
%{_includedir}/*
%exclude %{_libdir}/*.la
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_datadir}/aclocal/*.m4
%{_mandir}/man3/*

%changelog
* Tue Oct 16 2018 Jakub Martisko <jamartis@redhat.com> - 0.13.68-7
- Fix CVE-2018-17828
- Resolves: #1635890

* Thu Oct 11 2018 Jakub Martisko <jamartis@redhat.com> - 0.13.68-6
- Fix multilib regression by adding a 32bit version of the multilib patch
- Properly bump the release number in the previous changelog message
- Resolves: #1638337

* Thu Oct 04 2018 Jakub Martisko <jamartis@redhat.com> - 0.13.68-5
- Fix memory leak caused by the CVE-2018-16548
- Resolves: #1626202

* Mon Aug 13 2018 Jakub Martisko <jamartis@redhat.com> - 0.13.68-4
- Change the build dependency to python-devel and use the pathfix.py script
- Related: 1592262

* Sat Jul 28 2018 Jakub Martisko <jamartis@redhat.com> - 0.13.68-3
- Fix CVEs 2018-7725, 2018-7726, 2018-7727, 2018-6484, 2018-6869 
- Resolves: 1555082
- Resolves: 1545818

* Tue Jul 03 2018 Jakub Martisko <jamartis@redhat.com> - 0.13.68-2
- Port documentation generating scripts to Python 3
- Include both docs/*.htm and docs/*html files

* Wed Feb 14 2018 Alexander Bokovoy <abokovoy@redhat.com> - 0.13.68-1
- 0.13.68
- Fixes: #1543942 (CVE-2018-6484)

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.13.67-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Feb 01 2018 Alexander Bokovoy <abokovoy@redhat.com> - 0.13.67-1
- Update release
- CVE-2018-6381

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.13.62-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.13.62-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.13.62-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.13.62-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.62-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.62-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.62-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.62-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jan 30 2013 Jindrich Novy <jnovy@redhat.com> 0.13.62-2
- rebuild with -fno-strict-aliasing

* Wed Oct 10 2012 Matthias Saou <matthias@saou.eu> 0.13.62-1
- Update to 0.13.62.
- Remove no longer needed -Wl patch.

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.60-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Mar  8 2012 Tom Callaway <spot@fedoraproject.org> - 0.13.60-1
- update to 0.13.60

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.59-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.59-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Dec  9 2010 Hans de Goede <hdegoede@redhat.com> 0.13.59-2
- Fix broken zzip/_config.h which causes apps using zziplib to fail to compile

* Sat Dec  4 2010 Matthias Saou <http://freshrpms.net/> 0.13.59-1
- Update to 0.13.59.
- Remove no longer needed 'open' patch.
- Rebase the multilib patch, still required.
- Re-enable _smp_mflags, build works again with it apparently.

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.49-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.49-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec 22 2008 Matthias Saou <http://freshrpms.net/> 0.13.49-6
- Patch _config.h to make it identical for 32bit and 64bit archs (#343521).

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org>
- Autorebuild for GCC 4.3

* Wed Aug  8 2007 Matthias Saou <http://freshrpms.net/> 0.13.49-4
- Include patch to fix fd.open calls with recent glibc.
- Disable _smp_mflags since the docs fail to build.

* Fri Aug  3 2007 Matthias Saou <http://freshrpms.net/> 0.13.49-3
- Update License field.

* Tue Jun 19 2007 Matthias Saou <http://freshrpms.net/> 0.13.49-2
- Disable static lib build instead of excluding it later.
- Remove rpath on 64bit archs.
- Switch to using DESTDIR install method.

* Mon Mar 26 2007 Matthias Saou <http://freshrpms.net/> 0.13.49-1
- Update to 0.13.49 to fix CVE-2007-1614 (rhbz #233700).
- Include new man3 pages to the devel sub-package.

* Mon Aug 28 2006 Matthias Saou <http://freshrpms.net/> 0.13.47-1
- Update to 0.13.47.
- FC6 rebuild.

* Mon Jul 24 2006 Matthias Saou <http://freshrpms.net/> 0.13.45-3
- Split off -utils sub-package (#199467). Could have been plain "zzip"?
- Have sub-packages require exact release too.
- Build require automake to make the aclocal-1.9 check happy.
- Use --enable-frame-pointer otherwise -g gets removed from the CFLAGS.

* Mon Mar  6 2006 Matthias Saou <http://freshrpms.net/> 0.13.45-2
- FC5 rebuild.

* Thu Feb  9 2006 Matthias Saou <http://freshrpms.net/> 0.13.45-1
- Update to 0.13.45.
- Exclude static library.

* Sun May 22 2005 Jeremy Katz <katzj@redhat.com> - 0.13.38-2
- rebuild on all arches

* Tue Apr  5 2005 Matthias Saou <http://freshrpms.net/> 0.13.38-1
- Update to 0.13.38, fixes gcc4 compile issues (Adrian Reber).

* Tue Nov 16 2004 Matthias Saou <http://freshrpms.net/> 0.13.36-2
- Bump release to provide Extras upgrade path.

* Tue Jun  8 2004 Matthias Saou <http://freshrpms.net/> 0.13.36-1
- Initial RPM release.

