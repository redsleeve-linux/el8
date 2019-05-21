## NOTE: Lots of files in various subdirectories have the same name (such as
## "LICENSE") so this short macro allows us to distinguish them by using their
## directory names (from the source tree) as prefixes for the files.
%global add_to_license_files() \
        mkdir -p _license_files ; \
        cp -p %1 _license_files/$(echo '%1' | sed -e 's!/!.!g')

Name:           webkit2gtk3
Version:        2.22.6
Release:        1%{?dist}
Summary:        GTK+ Web content engine library

License:        LGPLv2
URL:            http://www.webkitgtk.org/
Source0:        http://webkitgtk.org/releases/webkitgtk-%{version}.tar.xz

# https://bugs.webkit.org/show_bug.cgi?id=132333
Patch0:        webkit-cloop_big_endians.patch
# Explicitly specify python2 over python
Patch1:        webkit-python2.patch
Patch2:        webkit-aarch64_page_size.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1591638
Patch3:        webkit-atk_crash.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1503624
Patch4:        webkit-atk_continuation_crash.patch

BuildRequires:  at-spi2-core-devel
BuildRequires:  bison
BuildRequires:  cairo-devel
BuildRequires:  cmake
BuildRequires:  enchant-devel
BuildRequires:  flex
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  git
BuildRequires:  geoclue2-devel
BuildRequires:  gettext
BuildRequires:  glib2-devel
BuildRequires:  gnutls-devel
BuildRequires:  gobject-introspection-devel
BuildRequires:  gperf
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  gstreamer1-plugins-bad-free-devel
BuildRequires:  gtk2-devel
BuildRequires:  gtk3-devel
BuildRequires:  gtk-doc
BuildRequires:  harfbuzz-devel
BuildRequires:  hyphen-devel
BuildRequires:  libicu-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libnotify-devel
BuildRequires:  libpng-devel
BuildRequires:  libsecret-devel
BuildRequires:  libsoup-devel
BuildRequires:  libwebp-devel
BuildRequires:  libxslt-devel
BuildRequires:  libXt-devel
BuildRequires:  libwayland-client-devel
BuildRequires:  libwayland-egl-devel
BuildRequires:  libwayland-server-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  pcre-devel
BuildRequires:  perl-File-Copy-Recursive
BuildRequires:  perl-JSON-PP
BuildRequires:  perl-Switch
BuildRequires:  python2
BuildRequires:  ruby
BuildRequires:  rubygems
BuildRequires:  sqlite-devel
BuildRequires:  upower-devel
BuildRequires:  woff2-devel

Requires:       geoclue2

# Obsolete libwebkit2gtk from the webkitgtk3 package
Obsoletes:      libwebkit2gtk < 2.5.0
Provides:       libwebkit2gtk = %{version}-%{release}

# This package was renamed, so obsolete the old webkitgtk4 package
Obsoletes:      webkitgtk4 < %{version}-%{release}
Provides:       webkitgtk4 = %{version}-%{release}

# We're supposed to specify versions here, but these crap Google libs don't do
# normal releases. Accordingly, they're not suitable to be system libs.
Provides:       bundled(angle)

# Require the jsc subpackage
Requires:       %{name}-jsc%{?_isa} = %{version}-%{release}

# Recommend the support for the GTK+ 2 based NPAPI plugins
Recommends:     %{name}-plugin-process-gtk2%{?_isa} = %{version}-%{release}

# Filter out provides for private libraries
%global __provides_exclude_from ^%{_libdir}/webkit2gtk-4\\.0/.*\\.so$

%description
WebKitGTK+ is the port of the portable web rendering engine WebKit to the
GTK+ platform.

This package contains WebKit2 based WebKitGTK+ for GTK+ 3.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-jsc%{?_isa} = %{version}-%{release}
Requires:       %{name}-jsc-devel%{?_isa} = %{version}-%{release}
Obsoletes:      webkitgtk4-devel < %{version}-%{release}
Provides:       webkitgtk4-devel = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries, build data, and header
files for developing applications that use %{name}.

%package        doc
Summary:        Documentation files for %{name}
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Obsoletes:      webkitgtk4-doc < %{version}-%{release}
Provides:       webkitgtk4-doc = %{version}-%{release}

%description    doc
This package contains developer documentation for %{name}.

%package        jsc
Summary:        JavaScript engine from %{name}
Obsoletes:      webkitgtk4-jsc < %{version}-%{release}
Provides:       webkitgtk4-jsc = %{version}-%{release}

%description    jsc
This package contains JavaScript engine from %{name}.

%package        jsc-devel
Summary:        Development files for JavaScript engine from %{name}
Requires:       %{name}-jsc%{?_isa} = %{version}-%{release}
Obsoletes:      webkitgtk4-jsc-devel < %{version}-%{release}
Provides:       webkitgtk4-jsc-devel = %{version}-%{release}

%description    jsc-devel
The %{name}-jsc-devel package contains libraries, build data, and header
files for developing applications that use JavaScript engine from %{name}.

%package        plugin-process-gtk2
Summary:        GTK+ 2 based NPAPI plugins support for %{name}
Requires:       %{name}-jsc%{?_isa} = %{version}-%{release}
Obsoletes:      %{name} < 2.12.0-3
Obsoletes:      webkitgtk4-plugin-process-gtk2 < %{version}-%{release}
Provides:       webkitgtk4-plugin-process-gtk2 = %{version}-%{release}

%description    plugin-process-gtk2
Support for the GTK+ 2 based NPAPI plugins (such as Adobe Flash) for %{name}.

%prep
%autosetup -p1 -n webkitgtk-%{version} -S git

# Remove bundled libraries
rm -rf Source/ThirdParty/gtest/
rm -rf Source/ThirdParty/qunit/

%build
export RHEL_ALLOW_PYTHON2_FOR_BUILD=1
# Increase the DIE limit so our debuginfo packages could be size optimized.
# Decreases the size for x86_64 from ~5G to ~1.1G.
# https://bugzilla.redhat.com/show_bug.cgi?id=1456261
%global _dwz_max_die_limit 250000000
# The _dwz_max_die_limit is being overridden by the arch specific ones from the
# redhat-rpm-config so we need to set the arch specific ones as well - now it
# is only needed for x86_64.
%global _dwz_max_die_limit_x86_64 250000000

# Decrease debuginfo even on ix86 because of:
# https://bugs.webkit.org/show_bug.cgi?id=140176
%ifarch s390x %{arm} %{ix86} %{power64} %{mips}
# Decrease debuginfo verbosity to reduce memory consumption even more
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

# BMalloc and JIT are disabled on aarch64, because of the non-standard page size
# that's causing problems there (it's enabled on Fedora)
mkdir -p %{_target_platform}
pushd %{_target_platform}
%cmake \
  -DPORT=GTK \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_GTKDOC=ON \
  -DENABLE_MINIBROWSER=ON \
%ifarch s390x %{power64} aarch64
  -DENABLE_JIT=OFF \
  -DUSE_SYSTEM_MALLOC=ON \
%endif
  ..
popd

# Remove the static amount of jobs once
# https://projects.engineering.redhat.com/browse/BREW-2146 is resolved
# make %{?_smp_mflags} -C %{_target_platform}
make -j6 -C %{_target_platform}

%install
%make_install -C %{_target_platform}

%find_lang WebKit2GTK-4.0

# Finally, copy over and rename various files for %%license inclusion
%add_to_license_files Source/JavaScriptCore/COPYING.LIB
%add_to_license_files Source/JavaScriptCore/icu/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/common/third_party/smhasher/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/third_party/compiler/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/third_party/libXNVCtrl/LICENSE
%add_to_license_files Source/WebCore/icu/LICENSE
%add_to_license_files Source/WebCore/LICENSE-APPLE
%add_to_license_files Source/WebCore/LICENSE-LGPL-2
%add_to_license_files Source/WebCore/LICENSE-LGPL-2.1
%add_to_license_files Source/WebInspectorUI/UserInterface/External/CodeMirror/LICENSE
%add_to_license_files Source/WebInspectorUI/UserInterface/External/ESLint/LICENSE
%add_to_license_files Source/WebInspectorUI/UserInterface/External/Esprima/LICENSE
%add_to_license_files Source/WebInspectorUI/UserInterface/External/three.js/LICENSE
%add_to_license_files Source/WTF/icu/LICENSE
%add_to_license_files Source/WTF/wtf/dtoa/COPYING
%add_to_license_files Source/WTF/wtf/dtoa/LICENSE

%files -f WebKit2GTK-4.0.lang
%license _license_files/*ThirdParty*
%license _license_files/*WebCore*
%license _license_files/*WebInspectorUI*
%license _license_files/*WTF*
%{_libdir}/libwebkit2gtk-4.0.so.*
%dir %{_libdir}/girepository-1.0
%{_libdir}/girepository-1.0/WebKit2-4.0.typelib
%{_libdir}/girepository-1.0/WebKit2WebExtension-4.0.typelib
%{_libdir}/webkit2gtk-4.0/
%{_libexecdir}/webkit2gtk-4.0/
%exclude %{_libexecdir}/webkit2gtk-4.0/MiniBrowser
%exclude %{_libexecdir}/webkit2gtk-4.0/WebKitPluginProcess2
%{_bindir}/WebKitWebDriver

%files devel
%{_libexecdir}/webkit2gtk-4.0/MiniBrowser
%{_includedir}/webkitgtk-4.0/
%exclude %{_includedir}/webkitgtk-4.0/JavaScriptCore
%{_libdir}/libwebkit2gtk-4.0.so
%{_libdir}/pkgconfig/webkit2gtk-4.0.pc
%{_libdir}/pkgconfig/webkit2gtk-web-extension-4.0.pc
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/WebKit2-4.0.gir
%{_datadir}/gir-1.0/WebKit2WebExtension-4.0.gir

%files jsc
%license _license_files/*JavaScriptCore*
%{_libdir}/libjavascriptcoregtk-4.0.so.*
%dir %{_libdir}/girepository-1.0
%{_libdir}/girepository-1.0/JavaScriptCore-4.0.typelib

%files jsc-devel
%{_libexecdir}/webkit2gtk-4.0/jsc
%dir %{_includedir}/webkitgtk-4.0
%{_includedir}/webkitgtk-4.0/JavaScriptCore/
%{_libdir}/libjavascriptcoregtk-4.0.so
%{_libdir}/pkgconfig/javascriptcoregtk-4.0.pc
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/JavaScriptCore-4.0.gir

%files plugin-process-gtk2
%{_libexecdir}/webkit2gtk-4.0/WebKitPluginProcess2

%files doc
%dir %{_datadir}/gtk-doc
%dir %{_datadir}/gtk-doc/html
%{_datadir}/gtk-doc/html/jsc-glib-4.0/
%{_datadir}/gtk-doc/html/webkit2gtk-4.0/
%{_datadir}/gtk-doc/html/webkitdomgtk-4.0/

%changelog
* Tue Feb 12 2019 Eike Rathke <erack@redhat.com> - 2.22.6-1
- Resolves: rhbz#1676489 Update to 2.22.6

* Fri Jan 25 2019 Eike Rathke <erack@redhat.com> - 2.22.5-2
- Resolves: rhbz#1666984 Fix gigacage

* Tue Dec 18 2018 Eike Rathke <erack@redhat.com> - 2.22.5-1
- Update to 2.22.5

* Tue Oct 30 2018 Tomas Popela <tpopela@redhat.com> - 2.22.3-1
- Update to 2.22.3
- Resolves: rhbz#1641009

* Mon Sep 24 2018 Tomas Popela <tpopela@redhat.com> - 2.22.2-1
- Update to 2.22.2
- Resolves: rhbz#1625602

* Thu Sep 20 2018 Tomas Popela <tpopela@redhat.com> - 2.22.1-1
- Update to 2.22.1
- Resolves: rhbz#1625602

* Tue Sep 11 2018 Tomas Popela <tpopela@redhat.com> - 2.22.0-2
- Backport patches from RHEL 7
- Resolves: rhbz#1625602

* Wed Sep 05 2018 Tomas Popela <tpopela@redhat.com> - 2.22.0-1
- Update to 2.22.0
- Resolves: rhbz#1625602

* Tue Jul 17 2018 Tomas Popela <tpopela@redhat.com> - 2.20.3-3
- Update the python2 patch

* Mon Jun 18 2018 Tomas Popela <tpopela@redhat.com> - 2.20.3-3
- Export the python2 env variable
- Resolves: rhbz#1592264

* Mon Jun 11 2018 Tomas Popela <tpopela@redhat.com> - 2.20.3-1
- Update to 2.20.3

* Thu May 24 2018 Tomas Popela <tpopela@redhat.com> - 2.20.2-4
- Explicitly specify python2 over python and add python2 to BR

* Tue May 22 2018 Tomas Popela <tpopela@redhat.com> - 2.20.2-3
- aarch64 on RHEL 8 does have a 64kb page size
- Resolves: rhbz#1578576

* Tue May 22 2018 Tomas Popela <tpopela@redhat.com> - 2.20.2-2
- Temporary disable JIT and BMalloc on aarch64 due to Gigacage problems
- Resolves: rhbz#1578576

* Tue May 15 2018 Tomas Popela <tpopela@redhat.com> - 2.20.2-1
- Update to 2.20.2
- Resolves: rhbz#1577388

* Tue Apr 10 2018 Tomas Popela <tpopela@redhat.com> - 2.20.1-1
- Update to 2.20.1

* Mon Mar 12 2018 Kalev Lember <klember@redhat.com> - 2.20.0-2
- Bump webkitgtk4 obsoletes versions

* Mon Mar 12 2018 Tomas Popela <tpopela@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Tue Mar 06 2018 Tomas Popela <tpopela@redhat.com> - 2.19.92-1
- Update to 2.19.92

* Wed Feb 21 2018 Tomas Popela <tpopela@redhat.com> - 2.19.91-1
- Update to 2.19.91

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.19.90-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Feb 05 2018 Tomas Popela <tpopela@redhat.com> - 2.19.90-1
- Update to 2.19.90

* Tue Jan 30 2018 Tomas Popela <tpopela@redhat.com> - 2.19.6-3
- Remove obsoleted ldconfig scriptlets

* Wed Jan 17 2018 Tomas Popela <tpopela@redhat.com> - 2.19.6-1
- Update to 2.19.6

* Thu Jan 11 2018 Tomas Popela <tpopela@redhat.com> - 2.19.5-2
- This package was formerly named webkitgtk4
