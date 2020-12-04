# Shared object version of libkcapi.
%global vmajor            1
%global vminor            2
%global vpatch            0

# Do we build the replacements packages?
%bcond_with replace_coreutils
# Replace fipscheck by default in Fedora 33+:
%if 0%{?fedora} >= 33 || 0%{?rhel} >= 9
%bcond_without replace_fipscheck
%else
%bcond_with replace_fipscheck
%endif
# Replace hmaccalc by default in Fedora 28+:
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
%bcond_without replace_hmaccalc
%else
%bcond_with replace_hmaccalc
%endif
%if 0%{?fedora} >= 29 || 0%{?rhel} >= 8
%bcond_without test_package
%else
%bcond_with test_package
%endif

# This package needs at least Linux Kernel v4.10.0.
%global min_kernel_ver    4.10.0

# Do we need to tweak sysctl.d? In newer versions of the Linux
# Kernel the default ancillary buffer size is set high enough.
# TODO: Adapt this when the patch for net/core/sock.c is merged.
%if %{lua:print(rpm.vercmp('99.0.0', posix.uname('%r')));} >= 0
%global with_sysctl_tweak 1
%else
%global with_sysctl_tweak 0
%endif

%if %{with_sysctl_tweak}
# Priority for the sysctl.d preset.
%global sysctl_prio       50

# Value used for the sysctl.d preset.
%global sysctl_optmem_max 81920

# Extension for the README.distro file.
%global distroname_ext    %{?fedora:fedora}%{?rhel:redhat}
%endif

# Lowest limit to run the testsuite.  If we cannot obtain this
# value, we asume the testsuite cannot be run.
%global test_optmem_max   %(%{__cat} /proc/sys/net/core/optmem_max || echo 0)

# For picking patches from upstream commits or pull requests.
%global giturl            https://github.com/smuellerDD/%{name}

# Do we replace some coreutils?
%if %{with replace_coreutils}
# TODO: Adapt this when replacing some coreutils initially.
%global coreutils_evr     8.29-1%{?dist}
%endif

# Do we replace fipscheck?
%if %{with replace_fipscheck}
%global fipscheck_evr     1.5.0-9
%endif

# Do we replace hmaccalc?
%if %{with replace_hmaccalc}
%global hmaccalc_evr      0.9.14-10%{?dist}
%endif

%global apps_hmaccalc sha1hmac sha224hmac sha256hmac sha384hmac sha512hmac
%global apps_fipscheck sha1sum sha224sum sha256sum sha384sum sha512sum md5sum fipscheck fipshmac

# On old kernels use mock hashers implemented via openssl
%if %{lua:print(rpm.vercmp(posix.uname('%r'), '3.19'));} >= 0
%global sha512hmac bin/kcapi-hasher -n sha512hmac
%global fipshmac   bin/kcapi-hasher -n fipshmac
%else
%global sha512hmac bash %{_sourcedir}/sha512hmac-openssl.sh
%global fipshmac   bash %{_sourcedir}/fipshmac-openssl.sh
%endif

# Add generation of HMAC checksums of the final stripped
# binaries.  %%define with lazy globbing is used here
# intentionally, because using %%global does not work.
%define __spec_install_post                                      \
%{?__debug_package:%{__debug_install_post}}                      \
%{__arch_install_post}                                           \
%{__os_install_post}                                             \
bin_path=%{buildroot}%{_bindir}                                  \
lib_path=%{buildroot}/%{_lib}                                    \
for app in %{apps_hmaccalc}; do                                  \
  test -e "$bin_path"/$app || continue                           \
  { %sha512hmac "$bin_path"/$app || exit 1; }                    \\\
    | cut -f 1 -d ' ' >"$lib_path"/hmaccalc/$app.hmac            \
done                                                             \
for app in %{apps_fipscheck}; do                                 \
  test -e "$bin_path"/$app || continue                           \
  %fipshmac -d "$lib_path"/fipscheck "$bin_path"/$app || exit 1  \
done                                                             \
%{_sbindir}/hardlink -cfv %{buildroot}%{_bindir}                 \
%fipshmac -d "$lib_path"/fipscheck                               \\\
  "$lib_path"/libkcapi.so.%{version} || exit 1                   \
%{__ln_s} libkcapi.so.%{version}.hmac                            \\\
  "$lib_path"/fipscheck/libkcapi.so.%{vmajor}.hmac               \
%{nil}


Name:           libkcapi
Version:        %{vmajor}.%{vminor}.%{vpatch}
Release:        2%{?dist}
Summary:        User space interface to the Linux Kernel Crypto API

License:        BSD or GPLv2
URL:            http://www.chronox.de/%{name}.html
Source0:        http://www.chronox.de/%{name}/%{name}-%{version}.tar.xz
Source1:        http://www.chronox.de/%{name}/%{name}-%{version}.tar.xz.asc
Source2:        sha512hmac-openssl.sh
Source3:        fipshmac-openssl.sh

Patch100:       100-fix-double-free-hasher.patch

BuildRequires:  bash
BuildRequires:  clang
BuildRequires:  coreutils
BuildRequires:  cppcheck
BuildRequires:  docbook-utils-pdf
BuildRequires:  gcc
BuildRequires:  git
BuildRequires:  hardlink
BuildRequires:  kernel-headers >= %{min_kernel_ver}
BuildRequires:  libtool
BuildRequires:  openssl
BuildRequires:  perl
BuildRequires:  systemd
BuildRequires:  xmlto

# For ownership of %%{_sysctldir}.
Requires:       systemd

Obsoletes:      %{name}-replacements <= %{version}-%{release}

%description
libkcapi allows user-space to access the Linux kernel crypto API.

This library uses the netlink interface and exports easy to use APIs
so that a developer does not need to consider the low-level netlink
interface handling.

The library does not implement any cipher algorithms.  All consumer
requests are sent to the kernel for processing.  Results from the
kernel crypto API are returned to the consumer via the library API.

The kernel interface and therefore this library can be used by
unprivileged processes.


%package        devel
Summary:        Development files for the %{name} package
Requires:       %{name}%{?_isa} == %{version}-%{release}

%description    devel
Header files for applications that use %{name}.


%package        doc
Summary:        User documentation for the %{name} package
Requires:       %{name}%{?_isa} == %{version}-%{release}

%description    doc
User documentation for %{name}.


%if %{with replace_coreutils}
%package        checksum
Summary:        Drop-in replacement for *sum utils provided by the %{name} package
Requires:       %{name}%{?_isa}    == %{version}-%{release}

Requires:       coreutils%{?_isa}  >= %{coreutils_evr}

Conflicts:      coreutils          < %{coreutils_evr}
Conflicts:      coreutils-single

%description    checksum
Provides drop-in replacements for sha*sum tools (from package
coreutils) using %{name}.
%endif


%if %{with replace_fipscheck}
%package        fipscheck
Summary:        Drop-in replacements for fipscheck/fipshmac provided by the %{name} package
Requires:       %{name}%{?_isa}   == %{version}-%{release}

Obsoletes:      fipscheck         <= %{fipscheck_evr}

Provides:       fipscheck         == %{fipscheck_evr}.1
Provides:       fipscheck%{?_isa} == %{fipscheck_evr}.1

%description    fipscheck
Provides drop-in replacements for fipscheck and fipshmac tools (from
package fipscheck) using %{name}.
%endif


%if %{with replace_hmaccalc}
%package        hmaccalc
Summary:        Drop-in replacements for hmaccalc provided by the %{name} package
Requires:       %{name}%{?_isa}   == %{version}-%{release}

Obsoletes:      hmaccalc          <= %{hmaccalc_evr}

Provides:       hmaccalc          == %{hmaccalc_evr}.1
Provides:       hmaccalc%{?_isa}  == %{hmaccalc_evr}.1

%description    hmaccalc
Provides drop-in replacements for sha*hmac tools (from package
hmaccalc) using %{name}.
%endif


%package        static
Summary:        Static library for -static linking with %{name}
Requires:       %{name}-devel%{?_isa} == %{version}-%{release}

%description    static
This package contains the %{name} static libraries for -static
linking.  You don't need this, unless you link statically, which
is highly discouraged.


%package        tools
Summary:        Utility applications for the %{name} package
Requires:       %{name}%{?_isa} == %{version}-%{release}

%description    tools
Utility applications that are provided with %{name}.  This includes
tools to use message digests, symmetric ciphers and random number
generators implemented in the Linux kernel from command line.


%if %{with test_package}
%package        tests
Summary:        Testing scripts for the %{name} package
Requires:       %{name}%{?_isa}       == %{version}-%{release}
Requires:       %{name}-tools%{?_isa} == %{version}-%{release}
%if %{with replace_hmaccalc}
Requires:       %{name}-hmaccalc%{?_isa} == %{version}-%{release}
%endif
%if %{with replace_coreutils}
Requires:       %{name}-checksum%{?_isa} == %{version}-%{release}
%endif
Requires:       coreutils
Requires:       openssl
Requires:       perl

%description    tests
Auxiliary scripts for testing %{name}.
%endif


%prep
%autosetup -p 1 -S git

%if %{with_sysctl_tweak}
%{__cat} << EOF > README.%{distroname_ext}
This package increases the default limit of the ancillary buffer size
per kernel socket defined in \`net.core.optmem_max\` to %{sysctl_optmem_max} bytes.

For this preset to become active it requires a reboot after the
installation of this package.  You can also manually increase this
limit by invocing \`sysctl net.core.optmem_max=%{sysctl_optmem_max}\` as the
super-user, e.g. using \`su\` or \`sudo\` on the terminal.

This is done to provide consumers of the new Linux Kernel Crypto API
User Space Interface a well sufficient and reasonable maximum limit
by default, especially when using AIO with a larger amount of IOVECs.

For further information about the AF_ALG kernel socket and AIO, see
the discussion at the kernel-crypto mailing-list:
https://www.mail-archive.com/linux-crypto@vger.kernel.org/msg30417.html

See the instructions given in '%{_sysctldir}/50-default.conf',
if you need or want to override the preset made by this package.
EOF

%{__cat} << EOF > %{sysctl_prio}-%{name}-optmem_max.conf
# See the 'README.%{distroname_ext}' file shipped in %%doc
# with the %{name} package.
#
# See '%{_sysctldir}/50-default.conf',
# if you need or want to override this preset.

# Increase the ancillary buffer size per socket.
net.core.optmem_max = %{sysctl_optmem_max}
EOF
%endif

%{_bindir}/autoreconf -fiv


%build
%configure               \
  --libdir=/%{_lib}      \
  --disable-silent-rules \
  --enable-kcapi-encapp  \
  --enable-kcapi-dgstapp \
  --enable-kcapi-hasher  \
  --enable-kcapi-rngapp  \
  --enable-kcapi-speed   \
  --enable-kcapi-test    \
  --enable-shared        \
  --enable-static        \
  --enable-sum-prefix=   \
  --enable-sum-dir=/%{_lib} \
  --with-pkgconfigdir=%{_libdir}/pkgconfig
%make_build all doc


%install
%make_install

# Install sysctl.d preset.
%{__mkdir_p} %{buildroot}%{_sysctldir}
%{__install} -Dpm 0644 -t %{buildroot}%{_sysctldir} \
  %{sysctl_prio}-%{name}-optmem_max.conf

# Install into proper location for inclusion by %%doc.
%{__mkdir_p} %{buildroot}%{_pkgdocdir}
%{__install} -Dpm 0644 -t %{buildroot}%{_pkgdocdir} \
%if %{with_sysctl_tweak}
  README.%{distroname_ext}                          \
%endif
  README.md CHANGES.md TODO doc/%{name}.p{df,s}
%{__cp} -pr lib/doc/html %{buildroot}%{_pkgdocdir}

# Install replacement tools, if enabled.
%if !%{with replace_coreutils}
%{__rm} -f                            \
  %{buildroot}%{_bindir}/md5sum       \
  %{buildroot}%{_bindir}/sha*sum
%endif

%if !%{with replace_fipscheck}
%{__rm} -f %{buildroot}%{_bindir}/fips*
%endif

%if !%{with replace_hmaccalc}
%{__rm} -f %{buildroot}%{_bindir}/sha*hmac
%endif

# We don't ship autocrap dumplings.
%{_bindir}/find %{buildroot} -type f -name '*.la' -print -delete

# HMAC checksums are generated during __spec_install_post.
%{_bindir}/find %{buildroot} -type f -name '*.hmac' -print -delete

# Remove 0-size files.
%{_bindir}/find %{buildroot} -type f -size 0 -print -delete

# Make sure all docs have non-exec permissions, except for the dirs.
%{_bindir}/find %{buildroot}%{_pkgdocdir} -type f -print | \
  %{_bindir}/xargs %{__chmod} -c 0644
%{_bindir}/find %{buildroot}%{_pkgdocdir} -type d -print | \
  %{_bindir}/xargs %{__chmod} -c 0755

# Possibly save some space by hardlinking.
for d in %{_mandir} %{_pkgdocdir}; do
  %{_sbindir}/hardlink -cfv %{buildroot}$d
done


%check
# Some basic sanity checks.
for t in cppcheck scan; do
  %make_build $t
done

# On some arches `/proc/sys/net/core/optmem_max` is lower than 20480,
# which is the lowest limit needed to run the testsuite.  If that limit
# is not met, we do not run it.
%if %{test_optmem_max} >= 20480
# Skip the testsuite on old kernels.
%if %{lua:print(rpm.vercmp(posix.uname('%r'), '5.1'));} >= 0
# Real testsuite.
pushd test
# Ignore test result since the CI will do better testing anyway
NO_32BIT_TEST=1    \
  ./test-invocation.sh || true
popd
%endif
%endif


%ldconfig_scriptlets


%files
%license COPYING*
%doc %dir %{_pkgdocdir}
%doc %{_pkgdocdir}/README.md
/%{_lib}/%{name}.so.%{vmajor}
/%{_lib}/%{name}.so.%{version}
/%{_lib}/fipscheck/%{name}.so.%{vmajor}.hmac
/%{_lib}/fipscheck/%{name}.so.%{version}.hmac
%if %{with_sysctl_tweak}
%doc %{_pkgdocdir}/README.%{distroname_ext}
%{_sysctldir}/%{sysctl_prio}-%{name}-optmem_max.conf
%endif


%files          devel
%doc %{_pkgdocdir}/CHANGES.md
%doc %{_pkgdocdir}/TODO
%{_includedir}/kcapi.h
%{_mandir}/man3/kcapi_*.3.*
/%{_lib}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc


%files          doc
%doc %{_pkgdocdir}


%if %{with replace_coreutils}
%files          checksum
%{_bindir}/md5sum
%{_bindir}/sha*sum
/%{_lib}/fipscheck/md5sum.hmac
/%{_lib}/fipscheck/sha*sum.hmac
%endif

%if %{with replace_fipscheck}
%files          fipscheck
%{_bindir}/fips*
/%{_lib}/fipscheck/fips*.hmac
%endif

%if %{with replace_hmaccalc}
%files          hmaccalc
%{_bindir}/sha*hmac
/%{_lib}/hmaccalc/sha*hmac.hmac
%endif


%files          static
/%{_lib}/%{name}.a


%files          tools
%{_bindir}/kcapi*
%{_mandir}/man1/kcapi*.1.*


%if %{with test_package}
%files          tests
%{_libexecdir}/%{name}/*
%endif


%changelog
* Tue May 26 2020 Sahana Prasad <sahana@redhat.com> - 1.2.0-2
- Fix double free issue in hasher()

* Mon May 25 2020 Sahana Prasad <sahana@redhat.com> - 1.2.0-1
- [RHEL] Update to upstream version 1.2.0

* Thu Apr 30 2020 Sahana Prasad <sahana@redhat.com> - 1.1.5-3
- Enables building on old kernels [sync fix in Fedora from omosnance].
- This is required for covscans as they run on RHEL7 machines.

* Wed Apr 29 2020 Sahana Prasad <sahana@redhat.com> - 1.1.5-2
- Drop the license from the doc subpackage to avoid conflicts

* Mon Apr 27 2020 Sahana Prasad <sahana@redhat.com> - 1.1.5-1
- [RHEL] Update to upstream version 1.1.5
- [RHEL] Sync with Fedora branch

* Thu Aug 09 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-16_1
- [RHEL] Apply 'Add missing dependencies to the tests package'
- [RHEL] Apply 'Update patch from upstream'

* Thu Aug 09 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-16
- Add missing dependencies to the tests package
- Update patch from upstream

* Thu Aug 09 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-15_1
- [RHEL] Apply 'Build and tests require perl'

* Thu Aug 09 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-15
- Build and tests require perl

* Thu Aug 09 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-14_2
- [RHEL] Re-enable AEAD tests and ignore test result
- [RHEL] Drop the ppc64 ignore-failures workaround

* Thu Aug 09 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-14_1
- [RHEL] Apply 'Add missing script to the 'tests' package'

* Thu Aug 09 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-14
- Add missing script to the 'tests' package

* Wed Aug 08 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-13_1
- [RHEL] Sync with the Fedora branch

* Wed Aug 08 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-13
- Add missing requires to the 'tests' subpackage

* Wed Aug 08 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-12_1
- [RHEL] Sync with the Fedora branch

* Tue Aug 07 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-12
- Produce a subpackage with test scripts
- Build the 'tests' subpackage conditionally

* Wed Aug 01 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-11_1
- [RHEL] Sync with the Fedora branch

* Wed Aug 01 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-11
- Add patch to fix unwanted closing of FD 0

* Tue Jul 31 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-10
- Remove the kernel headers workaround

* Mon Jul 30 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-9_1
- [RHEL] Sync with the Fedora branch
- [RHEL] Rebase the disable-AEAD-tests patch

* Fri Jul 27 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.1.1-9
- Rebuild for new binutils

* Fri Jul 27 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-8
- Add more Coverity fixes from upstream
- Add patch to fix AEAD fuzz test for BE arches
- Fixup specfile

* Mon Jul 23 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-7_1
- [RHEL] Sync with the Fedora branch
- [RHEL] Fixup specfile
- [RHEL] Rebase the disable-AEAD-tests patch

* Mon Jul 23 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-7
- Add various fixes from upstream
- Drop the Requires on kernel package

* Wed Jul 18 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-3_2
- [RHEL] Temporarily disable AEAD tests

* Mon Jul 16 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-6
- Put .hmac files into a separate directory

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jul 12 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-4
- Add patch to work around FTBFS on rawhide

* Wed Jul 11 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-3_1
- [RHEL] Sync with the Fedora branch

* Wed Jul 11 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-3
- Fix off-by-one error in checkfile parsing

* Wed Jul 11 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-2_2
- [RHEL] Disable fuzz test

* Wed Jul 11 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-2_1
- [RHEL] Sync with the Fedora branch

* Wed Jul 11 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-2
- Fix command-line parsing in libkcapi-hmaccalc

* Tue Jul 10 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-1_2
- [RHEL] Work around build failure with new kernel headers

* Mon Jun 18 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-1_1
- [RHEL] Skip CLang static analysis
- [RHEL] Remove the dependency on kernel package

* Mon Jun 18 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.1-1
- Update to upstream version 1.1.1

* Wed May 09 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.0-5
- Skip CLang static analysis in RHEL
- Revert "Skip CLang static analysis in RHEL"
- Use own sha512hmac and fipscheck

* Wed May 02 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.0-4
- Fix description lines being too long

* Fri Apr 27 2018 Björn Esser <besser82@fedoraproject.org> - 1.1.0-3
- Fix conditional for hmaccalc replacement

* Mon Apr 16 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.0-2
- Enable hmaccalc replacements in Fedora 28+

* Thu Apr 12 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.1.0-1
- Update to upstream version 1.1.0

* Sat Mar 31 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-10
- Replace single patches with a monolitic one from upstream
- Obsolete replacements subpackage
- Ignore failing tests on %%{power64} temporarily

* Thu Mar 08 2018 Ondrej Mosnáček <omosnace@redhat.com> - 1.0.3-9
- Split up the replacements subpackage

* Mon Feb 26 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-8
- Increase optmem_max preset to 81920

* Mon Feb 26 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-7
- Obsoletes work by package name, not by provides (rhbz#1537225)

* Sun Feb 25 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-6
- Add patch to fix a copy-paste typo

* Sat Feb 17 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-5
- Add patch to fix build with -Werror

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Feb 04 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-3
- Switch to %%ldconfig_scriptlets

* Wed Jan 17 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-2
- Decrease optmem_max preset to 40960
- Let the build fail, if the minimum kernel version cannot be met
- Conditionalize the sysctl.d tweak on version of the kernel
- Conditionalize the name of README.distro on the distro

* Tue Jan 16 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-1
- Initial import (rhbz#1533929)

* Tue Jan 16 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.13
- Increase optmem_max preset to 81920

* Tue Jan 16 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.12
- Add sysctl.d preset and README.fedora

* Mon Jan 15 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.11
- Make the contents of the -replacements package configurable

* Mon Jan 15 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.10
- Fix Obsoletes of the -replacements package

* Sun Jan 14 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.9
- Disable the -replacements package until we have a plan for it

* Sun Jan 14 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.8
- Move the kcapi-hasher binary to -replacements package, since it is
  not of much use without the linked invocation names and saves the
  extra Requires on the -tools package

* Sun Jan 14 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.7
- Fix internal Requires of sub-packages
- Hardlink files in %%{_bindir}

* Sun Jan 14 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.6
- Add patches from upstream

* Sat Jan 13 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.5
- Add patches from upstream

* Sat Jan 13 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.4
- Asume the testsuite cannot be run, if the value of optmem_max cannot
  be obtained

* Sat Jan 13 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.3
- Move libraries to /%%{_lib} instead of %%{_libdir}, which is useful
  during boot when the library might be needed before a potentially
  seperate /usr partition is mounted

* Sat Jan 13 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.2
- Asume optmem_max is at least 20480, if the real value cannot be obtained

* Fri Jan 12 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.3-0.1
- New upstream release

* Wed Jan 10 2018 Björn Esser <besser82@fedoraproject.org> - 1.0.2-0.1
- Initial rpm release (rhbz#1533929)
