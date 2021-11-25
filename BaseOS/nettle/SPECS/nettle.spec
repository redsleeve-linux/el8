%bcond_without fips

Name:           nettle
Version:        3.4.1
Release:        7%{?dist}
Summary:        A low-level cryptographic library

Group:          Development/Libraries
License:        LGPLv3+ or GPLv2+
URL:            http://www.lysator.liu.se/~nisse/nettle/
Source0:	%{name}-%{version}-hobbled.tar.xz
#Source0:        http://www.lysator.liu.se/~nisse/archive/%{name}-%{version}.tar.gz
Patch0:		nettle-3.3-remove-ecc-testsuite.patch
Patch1:		nettle-3.4-annocheck.patch
Patch2:		nettle-3.4.1-enable-intel-cet.patch
# https://lists.lysator.liu.se/pipermail/nettle-bugs/2021/009458.html
Patch3:		nettle-3.4.1-ecdsa-verify.patch
Patch4:		nettle-3.4.1-powerpc64-aes-asm.patch
Patch5:		nettle-3.4.1-powerpc64-ghash-asm.patch
Patch6:		nettle-3.4.1-rsa-decrypt.patch

BuildRequires:  gcc
BuildRequires:  gmp-devel, m4
BuildRequires:	libtool, automake, autoconf, gettext-devel
%if %{with fips}
BuildRequires:  fipscheck
%endif

Requires(post): info
Requires(preun): info


%package devel
Summary:        Development headers for a low-level cryptographic library
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       gmp-devel%{?_isa}

%description
Nettle is a cryptographic library that is designed to fit easily in more
or less any context: In crypto toolkits for object-oriented languages
(C++, Python, Pike, ...), in applications like LSH or GNUPG, or even in
kernel space.

%description devel
Nettle is a cryptographic library that is designed to fit easily in more
or less any context: In crypto toolkits for object-oriented languages
(C++, Python, Pike, ...), in applications like LSH or GNUPG, or even in
kernel space.  This package contains the files needed for developing 
applications with nettle.


%prep
%setup -q
# Disable -ggdb3 which makes debugedit unhappy
sed s/ggdb3/g/ -i configure
sed 's/ecc-192.c//g' -i Makefile.in
sed 's/ecc-224.c//g' -i Makefile.in
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

%build
autoreconf -ifv
%configure --enable-shared --enable-fat
make %{?_smp_mflags}

%if %{with fips}
%define __spec_install_post \
	%{?__debug_package:%{__debug_install_post}} \
	%{__arch_install_post} \
	%{__os_install_post} \
	fipshmac -d $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_libdir}/libnettle.so.6.* \
	fipshmac -d $RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_libdir}/libhogweed.so.4.* \
	file=`basename $RPM_BUILD_ROOT%{_libdir}/libnettle.so.6.*.hmac` && mv $RPM_BUILD_ROOT%{_libdir}/$file $RPM_BUILD_ROOT%{_libdir}/.$file && ln -s .$file $RPM_BUILD_ROOT%{_libdir}/.libnettle.so.6.hmac \
	file=`basename $RPM_BUILD_ROOT%{_libdir}/libhogweed.so.4.*.hmac` && mv $RPM_BUILD_ROOT%{_libdir}/$file $RPM_BUILD_ROOT%{_libdir}/.$file && ln -s .$file $RPM_BUILD_ROOT%{_libdir}/.libhogweed.so.4.hmac \
%{nil}
%endif

%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p"
make install-shared DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p"
mkdir -p $RPM_BUILD_ROOT%{_infodir}
install -p -m 644 nettle.info $RPM_BUILD_ROOT%{_infodir}/
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-lfib-stream
rm -f $RPM_BUILD_ROOT%{_bindir}/pkcs1-conv
rm -f $RPM_BUILD_ROOT%{_bindir}/sexp-conv
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-hash
rm -f $RPM_BUILD_ROOT%{_bindir}/nettle-pbkdf2

chmod 0755 $RPM_BUILD_ROOT%{_libdir}/libnettle.so.6.*
chmod 0755 $RPM_BUILD_ROOT%{_libdir}/libhogweed.so.4.*

%check
make check

%files
%doc AUTHORS NEWS README TODO
%license COPYINGv2 COPYING.LESSERv3
%{_infodir}/nettle.info.gz
%{_libdir}/libnettle.so.6
%{_libdir}/libnettle.so.6.*
%{_libdir}/libhogweed.so.4
%{_libdir}/libhogweed.so.4.*
%if %{with fips}
%{_libdir}/.libhogweed.so.*.hmac
%{_libdir}/.libnettle.so.*.hmac
%endif

%files devel
%doc descore.README nettle.html nettle.pdf
%{_includedir}/nettle
%{_libdir}/libnettle.so
%{_libdir}/libhogweed.so
%{_libdir}/pkgconfig/hogweed.pc
%{_libdir}/pkgconfig/nettle.pc

%post
/sbin/install-info %{_infodir}/%{name}.info %{_infodir}/dir || :
/sbin/ldconfig

%preun
if [ $1 = 0 ]; then
  /sbin/install-info --delete %{_infodir}/%{name}.info %{_infodir}/dir || :
fi

%postun -p /sbin/ldconfig



%changelog
* Wed Jul 14 2021 Daiki Ueno <dueno@redhat.com> - 3.4.1-7
- Backport CVE-2021-3580 from upstream 3.7.3 release (#1967990)

* Wed Jul 14 2021 Daiki Ueno <dueno@redhat.com> - 3.4.1-6
- Enable CTR mode optimization when the block size is 16

* Wed Jun 30 2021 Daiki Ueno <dueno@redhat.com> - 3.4.1-5
- Backport powerpc64 optimization patches from upstream (#1855228)
  Patch from Christopher M. Riedl.

* Wed Apr  7 2021 Daiki Ueno <dueno@redhat.com> - 3.4.1-4
- Fix patch application

* Tue Mar 30 2021 Daiki Ueno <dueno@redhat.com> - 3.4.1-3
- Port fixes for potential miscalculation in ecdsa_verify (#1942925)

* Fri May 15 2020 Anderson Sasaki <ansasaki@redhat.com> - 3.4.1-2
- Enable Intel CET support (#1737542)

* Tue Dec 11 2018 Daiki Ueno <dueno@redhat.com> - 3.4.1-1
- New upstream release

* Tue Oct 16 2018 Tomáš Mráz <tmraz@redhat.com> - 3.4-4
- Cover the gaps in annotation coverage for assembler sources
- Add .hmac checksums for FIPS mode integrity checking

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Nov 20 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.4-1
- New upstream release

* Wed Aug 09 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.3-5
- Removed executables from the library to allow parallel installation
  of x86-64 and x86 packages. The executables had testing purpose, and
  may be re-introduced in a separate package if needed.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jul 19 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.3-1
- New upstream release
- Allow arm neon instructions (they are enabled via fat builds)

* Tue Jul 19 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.2-3
- Backported a fix for more cache silence on RSA and DSA.

* Thu Feb 18 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.2-2
- Enabled fat builds by default

* Wed Feb  3 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.2-1
- updated to 3.2 (#1301310)
- Fixed CVE-2015-8803 secp256r1 calculation bug (#1304305)

* Wed Dec  9 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.1.1-6
- Made version.h architecture independent (#1289938)

* Wed Dec  2 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.1.1-5
- Disabled arm-neon unconditionally (#1287298)

* Thu Oct 22 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.1.1-4
- Fixed SHA3 implementation to conform to published version (#1252935)

* Sun Aug  2 2015 Peter Robinson <pbrobinson@fedoraproject.org> 3.1.1-3
- No need to ship license in devel too
- Drop ChangeLog as details are in NEWS

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Apr 30 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 3.1.1-1
- Updated to nettle 3.1.1

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 2.7.1-6
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Jan 10 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 2.7.1-3
- Corrected bug number in previous comment.

* Fri Dec 13 2013 Nikos Mavrogiannopoulos <nmav@redhat.com> - 2.7.1-2
- Added patch nettle-tmpalloc.patch to solve #1051455

* Mon Nov 25 2013 Nikos Mavrogiannopoulos <nmav@redhat.com> - 2.7.1-1
- Updated to nettle 2.7.1

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb  6 2013 Tomáš Mráz <tmraz@redhat.com> - 2.6-2
- nettle includes use gmp.h

* Tue Feb  5 2013 Tomáš Mráz <tmraz@redhat.com> - 2.6-1
- New upstream release

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jul 05 2012 David Woodhouse <dwmw2@infradead.org> - 2.4-3
- Remove explicit buildroot handling and defattr.

* Wed Jul 04 2012 David Woodhouse <dwmw2@infradead.org> - 2.4-2
- Review feedback

* Mon Jun 18 2012 David Woodhouse <dwmw2@infradead.org> - 2.4-1
- Revive package (GnuTLS needs it), disable static, update to current release 2.4

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.15-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.15-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Apr 10 2008 Ian Weller <ianweller@gmail.com> 1.15-5
- Moved static lib to -static

* Mon Mar 24 2008 Ian Weller <ianweller@gmail.com> 1.15-4
- Added libraries and ldconfig

* Mon Feb 18 2008 Ian Weller <ianweller@gmail.com> 1.15-3
- Added provides -static to -devel

* Sun Feb 17 2008 Ian Weller <ianweller@gmail.com> 1.15-2
- Removed redundant requires
- Removed redundant documentation between packages
- Fixed license tag
- Fixed -devel description
- Added the static library back to -devel
- Added make clean

* Fri Feb 08 2008 Ian Weller <ianweller@gmail.com> 1.15-1
- First package build.
