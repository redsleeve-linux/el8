# RPM conditionals so as to be able to dynamically produce
# slowdebug/release builds. See:
# http://rpm.org/user_doc/conditional_builds.html
#
# Examples:
#
# Produce release *and* slowdebug builds on x86_64 (default):
# $ rpmbuild -ba java-1.8.0-openjdk.spec
#
# Produce only release builds (no slowdebug builds) on x86_64:
# $ rpmbuild -ba java-1.8.0-openjdk.spec --without slowdebug
#
# Only produce a release build on x86_64:
# $ fedpkg mockbuild --without slowdebug
#
# Only produce a debug build on x86_64:
# $ fedpkg local --without release
#
# Enable slowdebug builds by default on relevant arches.
%bcond_without slowdebug
# Enable release builds by default on relevant arches.
%bcond_without release

# The -g flag says to use strip -g instead of full strip on DSOs or EXEs.
# This fixes detailed NMT and other tools which need minimal debug info.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1520879
%global _find_debuginfo_opts -g

# note: parametrized macros are order-sensitive (unlike not-parametrized) even with normal macros
# also necessary when passing it as parameter to other macros. If not macro, then it is considered a switch
# see the difference between global and define:
# See https://github.com/rpm-software-management/rpm/issues/127 to comments at  "pmatilai commented on Aug 18, 2017"
# (initiated in https://bugzilla.redhat.com/show_bug.cgi?id=1482192)
%global debug_suffix_unquoted -slowdebug
# quoted one for shell operations
%global debug_suffix "%{debug_suffix_unquoted}"
%global normal_suffix ""

# if you want only debug build but providing java build only normal build but set normalbuild_parameter
%global debug_warning This package has full debug on. Install only in need and remove asap.
%global debug_on with full debug on
%global for_debug for packages with debug on

%if %{with release}
%global include_normal_build 1
%else
%global include_normal_build 0
%endif

%if %{include_normal_build}
%global build_loop1 %{normal_suffix}
%else
%global build_loop1 %{nil}
%endif

%global aarch64         aarch64 arm64 armv8
# we need to distinguish between big and little endian PPC64
%global ppc64le         ppc64le
%global ppc64be         ppc64 ppc64p7
%global multilib_arches %{power64} sparc64 x86_64
%global jit_arches      %{ix86} x86_64 sparcv9 sparc64 %{aarch64} %{power64}
%global sa_arches       %{ix86} x86_64 sparcv9 sparc64 %{aarch64}

# By default, we build a debug build during main build on JIT architectures
%if %{with slowdebug}
%ifarch %{jit_arches}
%ifnarch %{arm}
%global include_debug_build 1
%else
%global include_debug_build 0
%endif
%else
%global include_debug_build 0
%endif
%else
%global include_debug_build 0
%endif

# Shenandoah HotSpot used everywhere, but built only on x86_64 and AArch64
%ifarch x86_64 %{aarch64}
%global use_shenandoah_hotspot 1
%else
%global use_shenandoah_hotspot 0
%endif

%if %{include_debug_build}
%global build_loop2 %{debug_suffix}
%else
%global build_loop2 %{nil}
%endif

# if you disable both builds, then the build fails
%global build_loop  %{build_loop1} %{build_loop2}
# note: that order: normal_suffix debug_suffix, in case of both enabled
# is expected in one single case at the end of the build
%global rev_build_loop  %{build_loop2} %{build_loop1}

%ifarch %{jit_arches}
%global bootstrap_build 1
%else
%global bootstrap_build 1
%endif

%if %{bootstrap_build}
%global targets bootcycle-images docs
%else
%global targets all
%endif


# Filter out flags from the optflags macro that cause problems with the OpenJDK build
# We filter out -Wall which will otherwise cause HotSpot to produce hundreds of thousands of warnings (100+mb logs)
# We filter out -O flags so that the optimization of HotSpot is not lowered from O3 to O2
# We replace it with -Wformat (required by -Werror=format-security) and -Wno-cpp to avoid FORTIFY_SOURCE warnings
# We filter out -fexceptions as the HotSpot build explicitly does -fno-exceptions and it's otherwise the default for C++
%global ourflags %(echo %optflags | sed -e 's|-Wall|-Wformat -Wno-cpp|' | sed -r -e 's|-O[0-9]*||')
%global ourcppflags %(echo %ourflags | sed -e 's|-fexceptions||')
%global ourldflags %{__global_ldflags}

# With disabled nss is NSS deactivated, so NSS_LIBDIR can contain the wrong path
# the initialization must be here. Later the pkg-config have buggy behavior
# looks like openjdk RPM specific bug
# Always set this so the nss.cfg file is not broken
%global NSS_LIBDIR %(pkg-config --variable=libdir nss)
%global NSS_LIBS %(pkg-config --libs nss)
%global NSS_CFLAGS %(pkg-config --cflags nss-softokn)
# see https://bugzilla.redhat.com/show_bug.cgi?id=1332456
%global NSSSOFTOKN_BUILDTIME_NUMBER %(pkg-config --modversion nss-softokn || : )
%global NSS_BUILDTIME_NUMBER %(pkg-config --modversion nss || : )
# this is workaround for processing of requires during srpm creation
%global NSSSOFTOKN_BUILDTIME_VERSION %(if [ "x%{NSSSOFTOKN_BUILDTIME_NUMBER}" == "x" ] ; then echo "" ;else echo ">= %{NSSSOFTOKN_BUILDTIME_NUMBER}" ;fi)
%global NSS_BUILDTIME_VERSION %(if [ "x%{NSS_BUILDTIME_NUMBER}" == "x" ] ; then echo "" ;else echo ">= %{NSS_BUILDTIME_NUMBER}" ;fi)


# Fix for https://bugzilla.redhat.com/show_bug.cgi?id=1111349.
# See also https://bugzilla.redhat.com/show_bug.cgi?id=1590796
# as to why some libraries *cannot* be excluded. In particular,
# these are:
# libjsig.so, libjava.so, libjawt.so, libjvm.so and libverify.so
%global _privatelibs libatk-wrapper[.]so.*|libattach[.]so.*|libawt_headless[.]so.*|libawt[.]so.*|libawt_xawt[.]so.*|libdt_socket[.]so.*|libfontmanager[.]so.*|libhprof[.]so.*|libinstrument[.]so.*|libj2gss[.]so.*|libj2pcsc[.]so.*|libj2pkcs11[.]so.*|libjaas_unix[.]so.*|libjava_crw_demo[.]so.*|libjavajpeg[.]so.*|libjdwp[.]so.*|libjli[.]so.*|libjsdt[.]so.*|libjsoundalsa[.]so.*|libjsound[.]so.*|liblcms[.]so.*|libmanagement[.]so.*|libmlib_image[.]so.*|libnet[.]so.*|libnio[.]so.*|libnpt[.]so.*|libsaproc[.]so.*|libsctp[.]so.*|libsplashscreen[.]so.*|libsunec[.]so.*|libunpack[.]so.*|libzip[.]so.*|lib[.]so\\(SUNWprivate_.*

%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$

# In some cases, the arch used by the JDK does
# not match _arch.
# Also, in some cases, the machine name used by SystemTap
# does not match that given by _build_cpu
%ifarch x86_64
%global archinstall amd64
%endif
%ifarch ppc
%global archinstall ppc
%endif
%ifarch %{ppc64be}
%global archinstall ppc64
%endif
%ifarch %{ppc64le}
%global archinstall ppc64le
%endif
%ifarch %{ix86}
%global archinstall i386
%endif
%ifarch ia64
%global archinstall ia64
%endif
%ifarch s390
%global archinstall s390
%endif
%ifarch s390x
%global archinstall s390x
%endif
%ifarch %{arm}
%global archinstall arm
%endif
%ifarch %{aarch64}
%global archinstall aarch64
%endif
# 32 bit sparc, optimized for v9
%ifarch sparcv9
%global archinstall sparc
%endif
# 64 bit sparc
%ifarch sparc64
%global archinstall sparcv9
%endif
%ifnarch %{jit_arches}
%global archinstall %{_arch}
%endif



%ifarch %{jit_arches}
%global with_systemtap 1
%else
%global with_systemtap 0
%endif

# New Version-String scheme-style defines
%global majorver 8

# Standard JPackage naming and versioning defines.
%global origin          openjdk
%global origin_nice     OpenJDK
%global top_level_dir_name   %{origin}
# note, following three variables are sedded from update_sources if used correctly. Hardcode them rather there.
%global shenandoah_project	aarch64-port
%global shenandoah_repo		jdk8u-shenandoah
%global shenandoah_revision    	aarch64-shenandoah-jdk8u201-b09
# Define old aarch64/jdk8u tree variables for compatibility
%global project         %{shenandoah_project}
%global repo            %{shenandoah_repo}
%global revision        %{shenandoah_revision}

# eg # jdk8u60-b27 -> jdk8u60 or # aarch64-jdk8u60-b27 -> aarch64-jdk8u60  (dont forget spec escape % by %%)
%global whole_update    %(VERSION=%{revision}; echo ${VERSION%%-*})
# eg  jdk8u60 -> 60 or aarch64-jdk8u60 -> 60
%global updatever       %(VERSION=%{whole_update}; echo ${VERSION##*u})
# eg jdk8u60-b27 -> b27
%global buildver        %(VERSION=%{revision}; echo ${VERSION##*-})
# priority must be 7 digits in total. The expression is workarounding tip
%global priority        %(TIP=1800%{updatever};  echo ${TIP/tip/999})

%global javaver         1.%{majorver}.0

# parametrized macros are order-sensitive
%global compatiblename  %{name}
%global fullversion     %{compatiblename}-%{version}-%{release}
# images stub
%global jdkimage       j2sdk-image
# output dir stub
%define buildoutputdir() %{expand:%{top_level_dir_name}/build/jdk8.build%{?1}}
# we can copy the javadoc to not arched dir, or make it not noarch
%define uniquejavadocdir()    %{expand:%{fullversion}%{?1}}
# main id and dir of this jdk
%define uniquesuffix()        %{expand:%{fullversion}.%{_arch}%{?1}}

%global etcjavasubdir     %{_sysconfdir}/java/java-%{javaver}-%{origin}
%define etcjavadir()      %{expand:%{etcjavasubdir}/%{uniquesuffix -- %{?1}}}
# Standard JPackage directories and symbolic links.
%define sdkdir()        %{expand:%{uniquesuffix -- %{?1}}}
%define jrelnk()        %{expand:jre-%{javaver}-%{origin}-%{version}-%{release}.%{_arch}%{?1}}

%define jredir()        %{expand:%{sdkdir -- %{?1}}/jre}
%define sdkbindir()     %{expand:%{_jvmdir}/%{sdkdir -- %{?1}}/bin}
%define jrebindir()     %{expand:%{_jvmdir}/%{jredir -- %{?1}}/bin}

%global rpm_state_dir %{_localstatedir}/lib/rpm-state/

%if %{with_systemtap}
# Where to install systemtap tapset (links)
# We would like these to be in a package specific sub-dir,
# but currently systemtap doesn't support that, so we have to
# use the root tapset dir for now. To distinguish between 64
# and 32 bit architectures we place the tapsets under the arch
# specific dir (note that systemtap will only pickup the tapset
# for the primary arch for now). Systemtap uses the machine name
# aka build_cpu as architecture specific directory name.
%global tapsetroot /usr/share/systemtap
%global tapsetdirttapset %{tapsetroot}/tapset/
%global tapsetdir %{tapsetdirttapset}/%{_build_cpu}
%endif

# not-duplicated scriptlets for normal/debug packages
%global update_desktop_icons /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%define post_script() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
exit 0
}


%define post_headless() %{expand:
%ifarch %{jit_arches}
# MetaspaceShared::generate_vtable_methods not implemented for PPC JIT
%ifnarch %{power64}
# see https://bugzilla.redhat.com/show_bug.cgi?id=513605
%{jrebindir -- %{?1}}/java -Xshare:dump >/dev/null 2>/dev/null
%endif
%endif

PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

ext=.gz
alternatives \\
  --install %{_bindir}/java java %{jrebindir -- %{?1}}/java $PRIORITY  --family %{name}.%{_arch} \\
  --slave %{_jvmdir}/jre jre %{_jvmdir}/%{jredir -- %{?1}} \\
  --slave %{_bindir}/jjs jjs %{jrebindir -- %{?1}}/jjs \\
  --slave %{_bindir}/keytool keytool %{jrebindir -- %{?1}}/keytool \\
  --slave %{_bindir}/orbd orbd %{jrebindir -- %{?1}}/orbd \\
  --slave %{_bindir}/pack200 pack200 %{jrebindir -- %{?1}}/pack200 \\
  --slave %{_bindir}/rmid rmid %{jrebindir -- %{?1}}/rmid \\
  --slave %{_bindir}/rmiregistry rmiregistry %{jrebindir -- %{?1}}/rmiregistry \\
  --slave %{_bindir}/servertool servertool %{jrebindir -- %{?1}}/servertool \\
  --slave %{_bindir}/tnameserv tnameserv %{jrebindir -- %{?1}}/tnameserv \\
  --slave %{_bindir}/policytool policytool %{jrebindir -- %{?1}}/policytool \\
  --slave %{_bindir}/unpack200 unpack200 %{jrebindir -- %{?1}}/unpack200 \\
  --slave %{_mandir}/man1/java.1$ext java.1$ext \\
  %{_mandir}/man1/java-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jjs.1$ext jjs.1$ext \\
  %{_mandir}/man1/jjs-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/keytool.1$ext keytool.1$ext \\
  %{_mandir}/man1/keytool-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/orbd.1$ext orbd.1$ext \\
  %{_mandir}/man1/orbd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/pack200.1$ext pack200.1$ext \\
  %{_mandir}/man1/pack200-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/rmid.1$ext rmid.1$ext \\
  %{_mandir}/man1/rmid-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/rmiregistry.1$ext rmiregistry.1$ext \\
  %{_mandir}/man1/rmiregistry-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/servertool.1$ext servertool.1$ext \\
  %{_mandir}/man1/servertool-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/tnameserv.1$ext tnameserv.1$ext \\
  %{_mandir}/man1/tnameserv-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/policytool.1$ext policytool.1$ext \\
  %{_mandir}/man1/policytool-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/unpack200.1$ext unpack200.1$ext \\
  %{_mandir}/man1/unpack200-%{uniquesuffix -- %{?1}}.1$ext

for X in %{origin} %{javaver} ; do
  alternatives --install %{_jvmdir}/jre-"$X" jre_"$X" %{_jvmdir}/%{jredir -- %{?1}} $PRIORITY --family %{name}.%{_arch}
done

update-alternatives --install %{_jvmdir}/jre-%{javaver}-%{origin} jre_%{javaver}_%{origin} %{_jvmdir}/%{jrelnk -- %{?1}} $PRIORITY  --family %{name}.%{_arch}


update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

# see pretrans where this file is declared
# also see that pretrans is only for non-debug
if [ ! "%{?1}" == %{debug_suffix} ]; then
  if [ -f %{_libexecdir}/copy_jdk_configs_fixFiles.sh ] ; then
    sh  %{_libexecdir}/copy_jdk_configs_fixFiles.sh %{rpm_state_dir}/%{name}.%{_arch}  %{_jvmdir}/%{sdkdir -- %{?1}}
  fi
fi

exit 0
}

%define postun_script() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{update_desktop_icons}
fi
exit 0
}


%define postun_headless() %{expand:
  alternatives --remove java %{jrebindir -- %{?1}}/java
  alternatives --remove jre_%{origin} %{_jvmdir}/%{jredir -- %{?1}}
  alternatives --remove jre_%{javaver} %{_jvmdir}/%{jredir -- %{?1}}
  alternatives --remove jre_%{javaver}_%{origin} %{_jvmdir}/%{jrelnk -- %{?1}}
}

%define posttrans_script() %{expand:
%{update_desktop_icons}
}

%define post_devel() %{expand:

PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

ext=.gz
alternatives \\
  --install %{_bindir}/javac javac %{sdkbindir -- %{?1}}/javac $PRIORITY  --family %{name}.%{_arch} \\
  --slave %{_jvmdir}/java java_sdk %{_jvmdir}/%{sdkdir -- %{?1}} \\
  --slave %{_bindir}/appletviewer appletviewer %{sdkbindir -- %{?1}}/appletviewer \\
  --slave %{_bindir}/extcheck extcheck %{sdkbindir -- %{?1}}/extcheck \\
  --slave %{_bindir}/idlj idlj %{sdkbindir -- %{?1}}/idlj \\
  --slave %{_bindir}/jar jar %{sdkbindir -- %{?1}}/jar \\
  --slave %{_bindir}/jarsigner jarsigner %{sdkbindir -- %{?1}}/jarsigner \\
  --slave %{_bindir}/javadoc javadoc %{sdkbindir -- %{?1}}/javadoc \\
  --slave %{_bindir}/javah javah %{sdkbindir -- %{?1}}/javah \\
  --slave %{_bindir}/javap javap %{sdkbindir -- %{?1}}/javap \\
  --slave %{_bindir}/jcmd jcmd %{sdkbindir -- %{?1}}/jcmd \\
  --slave %{_bindir}/jconsole jconsole %{sdkbindir -- %{?1}}/jconsole \\
  --slave %{_bindir}/jdb jdb %{sdkbindir -- %{?1}}/jdb \\
  --slave %{_bindir}/jdeps jdeps %{sdkbindir -- %{?1}}/jdeps \\
  --slave %{_bindir}/jhat jhat %{sdkbindir -- %{?1}}/jhat \\
  --slave %{_bindir}/jinfo jinfo %{sdkbindir -- %{?1}}/jinfo \\
  --slave %{_bindir}/jmap jmap %{sdkbindir -- %{?1}}/jmap \\
  --slave %{_bindir}/jps jps %{sdkbindir -- %{?1}}/jps \\
  --slave %{_bindir}/jrunscript jrunscript %{sdkbindir -- %{?1}}/jrunscript \\
  --slave %{_bindir}/jsadebugd jsadebugd %{sdkbindir -- %{?1}}/jsadebugd \\
  --slave %{_bindir}/jstack jstack %{sdkbindir -- %{?1}}/jstack \\
  --slave %{_bindir}/jstat jstat %{sdkbindir -- %{?1}}/jstat \\
  --slave %{_bindir}/jstatd jstatd %{sdkbindir -- %{?1}}/jstatd \\
  --slave %{_bindir}/native2ascii native2ascii %{sdkbindir -- %{?1}}/native2ascii \\
  --slave %{_bindir}/rmic rmic %{sdkbindir -- %{?1}}/rmic \\
  --slave %{_bindir}/schemagen schemagen %{sdkbindir -- %{?1}}/schemagen \\
  --slave %{_bindir}/serialver serialver %{sdkbindir -- %{?1}}/serialver \\
  --slave %{_bindir}/wsgen wsgen %{sdkbindir -- %{?1}}/wsgen \\
  --slave %{_bindir}/wsimport wsimport %{sdkbindir -- %{?1}}/wsimport \\
  --slave %{_bindir}/xjc xjc %{sdkbindir -- %{?1}}/xjc \\
  --slave %{_mandir}/man1/appletviewer.1$ext appletviewer.1$ext \\
  %{_mandir}/man1/appletviewer-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/extcheck.1$ext extcheck.1$ext \\
  %{_mandir}/man1/extcheck-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/idlj.1$ext idlj.1$ext \\
  %{_mandir}/man1/idlj-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jar.1$ext jar.1$ext \\
  %{_mandir}/man1/jar-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jarsigner.1$ext jarsigner.1$ext \\
  %{_mandir}/man1/jarsigner-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javac.1$ext javac.1$ext \\
  %{_mandir}/man1/javac-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javadoc.1$ext javadoc.1$ext \\
  %{_mandir}/man1/javadoc-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javah.1$ext javah.1$ext \\
  %{_mandir}/man1/javah-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javap.1$ext javap.1$ext \\
  %{_mandir}/man1/javap-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jcmd.1$ext jcmd.1$ext \\
  %{_mandir}/man1/jcmd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jconsole.1$ext jconsole.1$ext \\
  %{_mandir}/man1/jconsole-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jdb.1$ext jdb.1$ext \\
  %{_mandir}/man1/jdb-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jdeps.1$ext jdeps.1$ext \\
  %{_mandir}/man1/jdeps-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jhat.1$ext jhat.1$ext \\
  %{_mandir}/man1/jhat-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jinfo.1$ext jinfo.1$ext \\
  %{_mandir}/man1/jinfo-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jmap.1$ext jmap.1$ext \\
  %{_mandir}/man1/jmap-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jps.1$ext jps.1$ext \\
  %{_mandir}/man1/jps-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jrunscript.1$ext jrunscript.1$ext \\
  %{_mandir}/man1/jrunscript-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jsadebugd.1$ext jsadebugd.1$ext \\
  %{_mandir}/man1/jsadebugd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstack.1$ext jstack.1$ext \\
  %{_mandir}/man1/jstack-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstat.1$ext jstat.1$ext \\
  %{_mandir}/man1/jstat-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstatd.1$ext jstatd.1$ext \\
  %{_mandir}/man1/jstatd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/native2ascii.1$ext native2ascii.1$ext \\
  %{_mandir}/man1/native2ascii-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/rmic.1$ext rmic.1$ext \\
  %{_mandir}/man1/rmic-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/schemagen.1$ext schemagen.1$ext \\
  %{_mandir}/man1/schemagen-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/serialver.1$ext serialver.1$ext \\
  %{_mandir}/man1/serialver-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/wsgen.1$ext wsgen.1$ext \\
  %{_mandir}/man1/wsgen-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/wsimport.1$ext wsimport.1$ext \\
  %{_mandir}/man1/wsimport-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/xjc.1$ext xjc.1$ext \\
  %{_mandir}/man1/xjc-%{uniquesuffix -- %{?1}}.1$ext

for X in %{origin} %{javaver} ; do
  alternatives \\
    --install %{_jvmdir}/java-"$X" java_sdk_"$X" %{_jvmdir}/%{sdkdir -- %{?1}} $PRIORITY  --family %{name}.%{_arch}
done

update-alternatives --install %{_jvmdir}/java-%{javaver}-%{origin} java_sdk_%{javaver}_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}} $PRIORITY  --family %{name}.%{_arch}

update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

exit 0
}

%define postun_devel() %{expand:
  alternatives --remove javac %{sdkbindir -- %{?1}}/javac
  alternatives --remove java_sdk_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}}
  alternatives --remove java_sdk_%{javaver} %{_jvmdir}/%{sdkdir -- %{?1}}
  alternatives --remove java_sdk_%{javaver}_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}}

update-desktop-database %{_datadir}/applications &> /dev/null || :

if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{update_desktop_icons}
fi
exit 0
}

%define posttrans_devel() %{expand:
%{update_desktop_icons}
}

%define post_javadoc() %{expand:

PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

alternatives \\
  --install %{_javadocdir}/java javadocdir %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api \\
  $PRIORITY  --family %{name}
exit 0
}

%define postun_javadoc() %{expand:
  alternatives --remove javadocdir %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api
exit 0
}

%define post_javadoc_zip() %{expand:

PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

alternatives \\
  --install %{_javadocdir}/java-zip javadoczip %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip \\
  $PRIORITY  --family %{name}
exit 0
}

%define postun_javadoc_zip() %{expand:
  alternatives --remove javadoczip %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
exit 0
}

%define files_jre() %{expand:
%{_datadir}/icons/hicolor/*x*/apps/java-%{javaver}-%{origin}.png
%{_datadir}/applications/*policytool%{?1}.desktop
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/%{archinstall}/libjsoundalsa.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/%{archinstall}/libsplashscreen.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/%{archinstall}/libawt_xawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/%{archinstall}/libjawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/bin/policytool
}


%define files_jre_headless() %{expand:
%defattr(-,root,root,-)
%dir %{_sysconfdir}/.java/.systemPrefs
%dir %{_sysconfdir}/.java
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/jre/ASSEMBLY_EXCEPTION
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/jre/LICENSE
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/jre/THIRD_PARTY_README
%dir %{_jvmdir}/%{sdkdir -- %{?1}}
%{_jvmdir}/%{jrelnk -- %{?1}}
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/security
%{_jvmdir}/%{jredir -- %{?1}}/lib/security/cacerts
%dir %{_jvmdir}/%{jredir -- %{?1}}
%dir %{_jvmdir}/%{jredir -- %{?1}}/bin
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib
%{_jvmdir}/%{jredir -- %{?1}}/bin/java
%{_jvmdir}/%{jredir -- %{?1}}/bin/jjs
%{_jvmdir}/%{jredir -- %{?1}}/bin/keytool
%{_jvmdir}/%{jredir -- %{?1}}/bin/orbd
%{_jvmdir}/%{jredir -- %{?1}}/bin/pack200
%{_jvmdir}/%{jredir -- %{?1}}/bin/rmid
%{_jvmdir}/%{jredir -- %{?1}}/bin/rmiregistry
%{_jvmdir}/%{jredir -- %{?1}}/bin/servertool
%{_jvmdir}/%{jredir -- %{?1}}/bin/tnameserv
%{_jvmdir}/%{jredir -- %{?1}}/bin/unpack200
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/security/policy/unlimited/
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/security/policy/limited/
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/security/policy/
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/policy/unlimited/US_export_policy.jar
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/policy/unlimited/local_policy.jar
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/policy/limited/US_export_policy.jar
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/policy/limited/local_policy.jar
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/java.policy
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/java.security
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/blacklisted.certs
%config(noreplace) %{etcjavadir -- %{?1}}/lib/logging.properties
%config(noreplace) %{etcjavadir -- %{?1}}/lib/calendars.properties
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/policy/unlimited/US_export_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/policy/unlimited/local_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/policy/limited/US_export_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/policy/limited/local_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/java.policy
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/java.security
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/blacklisted.certs
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/logging.properties
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/calendars.properties
%{_mandir}/man1/java-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jjs-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/keytool-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/orbd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/pack200-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/rmid-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/rmiregistry-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/servertool-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/tnameserv-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/unpack200-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/policytool-%{uniquesuffix -- %{?1}}.1*
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/nss.cfg
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/nss.cfg
%ifarch %{jit_arches}
%ifnarch %{power64}
%attr(444, root, root) %ghost %{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/server/classes.jsa
%attr(444, root, root) %ghost %{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/client/classes.jsa
%endif
%endif
%dir %{etcjavasubdir}
%dir %{etcjavadir -- %{?1}}
%dir %{etcjavadir -- %{?1}}/lib
%dir %{etcjavadir -- %{?1}}/lib/security
%{etcjavadir -- %{?1}}/lib/security/cacerts
%dir %{etcjavadir -- %{?1}}/lib/security/policy
%dir %{etcjavadir -- %{?1}}/lib/security/policy/limited
%dir %{etcjavadir -- %{?1}}/lib/security/policy/unlimited
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/server/
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/client/
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/jli
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/jli/libjli.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/jvm.cfg
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libattach.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libawt.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libawt_headless.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libdt_socket.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libfontmanager.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libhprof.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libinstrument.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libj2gss.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libj2pcsc.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libj2pkcs11.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjaas_unix.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjava.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjava_crw_demo.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjavajpeg.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjdwp.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjsdt.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjsig.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjsound.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/liblcms.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libmanagement.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libmlib_image.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libnet.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libnio.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libnpt.so
%ifarch x86_64  %{ix86} %{aarch64}
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libsaproc.so
%endif
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libsctp.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libsunec.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libunpack.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libverify.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libzip.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/charsets.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/classlist
%{_jvmdir}/%{jredir -- %{?1}}/lib/content-types.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/currency.data
%{_jvmdir}/%{jredir -- %{?1}}/lib/flavormap.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/hijrah-config-umalqura.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/images/cursors/*
%{_jvmdir}/%{jredir -- %{?1}}/lib/jce.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/jexec
%{_jvmdir}/%{jredir -- %{?1}}/lib/jsse.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/jvm.hprof.txt
%{_jvmdir}/%{jredir -- %{?1}}/lib/meta-index
%{_jvmdir}/%{jredir -- %{?1}}/lib/net.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/psfont.properties.ja
%{_jvmdir}/%{jredir -- %{?1}}/lib/psfontj2d.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/resources.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/rt.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/sound.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/tzdb.dat
%{_jvmdir}/%{jredir -- %{?1}}/lib/management-agent.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/management/*
%{_jvmdir}/%{jredir -- %{?1}}/lib/cmm/*
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/cldrdata.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/dnsns.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/jaccess.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/localedata.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/meta-index
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/nashorn.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/sunec.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/sunjce_provider.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/sunpkcs11.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/zipfs.jar

%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/images
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/images/cursors
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/management
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/cmm
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/ext
}

%define files_devel() %{expand:
%defattr(-,root,root,-)
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/ASSEMBLY_EXCEPTION
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/LICENSE
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/THIRD_PARTY_README
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/bin
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/include
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/appletviewer
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/extcheck
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/idlj
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jar
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jarsigner
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/java
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javac
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javadoc
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javah
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javap
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/java-rmi.cgi
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jcmd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jconsole
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdb
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdeps
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jhat
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jinfo
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jjs
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jmap
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jps
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jrunscript
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jsadebugd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstack
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstat
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstatd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/keytool
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/native2ascii
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/orbd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/pack200
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/policytool
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/rmic
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/rmid
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/rmiregistry
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/schemagen
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/serialver
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/servertool
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/tnameserv
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/unpack200
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/wsgen
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/wsimport
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/xjc
%{_jvmdir}/%{sdkdir -- %{?1}}/include/*
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{archinstall}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/ct.sym
%if %{with_systemtap}
%{_jvmdir}/%{sdkdir -- %{?1}}/tapset
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/ir.idl
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jconsole.jar
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/orb.idl
%ifarch %{sa_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/sa-jdi.jar
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/dt.jar
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jexec
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/tools.jar
%{_datadir}/applications/*jconsole%{?1}.desktop
%{_mandir}/man1/appletviewer-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/extcheck-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/idlj-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jar-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jarsigner-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javac-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javadoc-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javah-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javap-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jconsole-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jcmd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdb-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdeps-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jhat-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jinfo-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jmap-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jps-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jrunscript-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jsadebugd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstack-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstat-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstatd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/native2ascii-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/rmic-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/schemagen-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/serialver-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/wsgen-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/wsimport-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/xjc-%{uniquesuffix -- %{?1}}.1*
%if %{with_systemtap}
%dir %{tapsetroot}
%dir %{tapsetdirttapset}
%dir %{tapsetdir}
%{tapsetdir}/*%{_arch}%{?1}.stp
%endif
}

%define files_demo() %{expand:
%defattr(-,root,root,-)
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/jre/LICENSE
}

%define files_src() %{expand:
%defattr(-,root,root,-)
%doc README.md
%{_jvmdir}/%{sdkdir -- %{?1}}/src.zip
}

%define files_javadoc() %{expand:
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{uniquejavadocdir -- %{?1}}
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/jre/LICENSE
}

%define files_javadoc_zip() %{expand:
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
%license %{buildoutputdir -- %{?1}}/images/%{jdkimage}/jre/LICENSE
}

%define files_accessibility() %{expand:
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libatk-wrapper.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/java-atk-wrapper.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/accessibility.properties
}

# not-duplicated requires/provides/obsoletes for normal/debug packages
%define java_rpo() %{expand:
Requires: fontconfig%{?_isa}
Requires: xorg-x11-fonts-Type1
# Require libXcomposite explicitly since it's only dynamically loaded
# at runtime. Fixes screenshot issues. See JDK-8150954.
Requires: libXcomposite%{?_isa}
# Requires rest of java
Requires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# for java-X-openjdk package's desktop binding
Recommends: gtk2%{?_isa}

Provides: java-%{javaver}-%{origin} = %{epoch}:%{version}-%{release}

# Standard JPackage base provides
Provides: jre = %{javaver}%{?1}
Provides: jre-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java%{?1} = %{epoch}:%{javaver}
}

%define java_headless_rpo() %{expand:
# Require /etc/pki/java/cacerts
Requires: ca-certificates
# Require javapackages-filesystem for ownership of /usr/lib/jvm/
Requires: javapackages-filesystem
# Require zone-info data provided by tzdata-java sub-package
Requires: tzdata-java >= 2015d
# libsctp.so.1 is being `dlopen`ed on demand
Requires: lksctp-tools%{?_isa}
# there is a need to depend on the exact version of NSS
Requires: nss%{?_isa} %{NSS_BUILDTIME_VERSION}
Requires: nss-softokn%{?_isa} %{NSSSOFTOKN_BUILDTIME_VERSION}
# tool to copy jdk's configs - should be Recommends only, but then only dnf/yum enforce it,
# not rpm transaction and so no configs are persisted when pure rpm -u is run. It may be
# considered as regression
Requires: copy-jdk-configs >= 3.3
OrderWithRequires: copy-jdk-configs
# for printing support
Requires: cups-libs
# Post requires alternatives to install tool alternatives
Requires(post):   %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(post):   chkconfig >= 1.7
# Postun requires alternatives to uninstall tool alternatives
Requires(postun): %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(postun):   chkconfig >= 1.7
# for optional support of kernel stream control, card reader and printing bindings
Suggests: lksctp-tools%{?_isa}, pcsc-lite-devel%{?_isa}

# Standard JPackage base provides
Provides: jre-headless%{?1} = %{epoch}:%{javaver}
Provides: jre-%{javaver}-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-headless%{?1} = %{epoch}:%{javaver}

# https://bugzilla.redhat.com/show_bug.cgi?id=1312019
Provides: /usr/bin/jjs

}

%define java_devel_rpo() %{expand:
# Requires base package
Requires:         %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install tool alternatives
Requires(post):   %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(post):   chkconfig >= 1.7
# Postun requires alternatives to uninstall tool alternatives
Requires(postun): %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(postun):   chkconfig >= 1.7

# Standard JPackage devel provides
Provides: java-sdk-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}
Provides: java-sdk-%{javaver}%{?1} = %{epoch}:%{version}
Provides: java-sdk-%{origin}%{?1} = %{epoch}:%{version}
Provides: java-sdk%{?1} = %{epoch}:%{javaver}
Provides: java-%{javaver}-devel%{?1} = %{epoch}:%{version}
Provides: java-%{javaver}-%{origin}-devel%{?1} = %{epoch}:%{version}
Provides: java-devel-%{origin}%{?1} = %{epoch}:%{version}
Provides: java-devel%{?1} = %{epoch}:%{javaver}

}


%define java_demo_rpo() %{expand:
Requires: %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

Provides: java-demo%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-demo%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-demo%{?1} = %{epoch}:%{version}-%{release}

}

%define java_javadoc_rpo() %{expand:
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install javadoc alternative
Requires(post):   %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(post):   chkconfig >= 1.7
# Postun requires alternatives to uninstall javadoc alternative
Requires(postun): %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(postun):   chkconfig >= 1.7

# Standard JPackage javadoc provides
Provides: java-javadoc%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-javadoc%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-javadoc%{?1} = %{epoch}:%{version}-%{release}
}

%define java_src_rpo() %{expand:
Requires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

# Standard JPackage sources provides
Provides: java-src%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-src%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-src%{?1} = %{epoch}:%{version}-%{release}
}

%define java_accessibility_rpo() %{expand:
Requires: java-atk-wrapper%{?_isa}
Requires: %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

Provides: java-accessibility = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-accessibility = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-accessibility = %{epoch}:%{version}-%{release}

}

# Prevent brp-java-repack-jars from being run
%global __jar_repack 0

Name:    java-%{javaver}-%{origin}
Version: %{javaver}.%{updatever}.%{buildver}
Release: 2%{?dist}
# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons
# and this change was brought into RHEL-4. java-1.5.0-ibm packages
# also included the epoch in their virtual provides. This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0". In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0. So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages. Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".

Epoch:   1
Summary: %{origin_nice} Runtime Environment %{majorver}
Group:   Development/Languages

# HotSpot code is licensed under GPLv2
# JDK library code is licensed under GPLv2 with the Classpath exception
# The Apache license is used in code taken from Apache projects (primarily JAXP & JAXWS)
# DOM levels 2 & 3 and the XML digital signature schemas are licensed under the W3C Software License
# The JSR166 concurrency code is in the public domain
# The BSD and MIT licenses are used for a number of third-party libraries (see THIRD_PARTY_README)
# The OpenJDK source tree includes the JPEG library (IJG), zlib & libpng (zlib), giflib and LCMS (MIT)
# The test code includes copies of NSS under the Mozilla Public License v2.0
# The PCSClite headers are under a BSD with advertising license
# The elliptic curve cryptography (ECC) source code is licensed under the LGPLv2.1 or any later version
License:  ASL 1.1 and ASL 2.0 and BSD and BSD with advertising and GPL+ and GPLv2 and GPLv2 with exceptions and IJG and LGPLv2+ and MIT and MPLv2.0 and Public Domain and W3C and zlib
URL:      http://openjdk.java.net/

# Shenandoah HotSpot
# aarch64-port/jdk8u-shenandoah contains an integration forest of
# OpenJDK 8u, the aarch64 port and Shenandoah
# To regenerate, use:
# VERSION=%%{shenandoah_revision}
# FILE_NAME_ROOT=%%{shenandoah_project}-%%{shenandoah_repo}-${VERSION}
# REPO_ROOT=<path to checked-out repository> generate_source_tarball.sh
# where the source is obtained from http://hg.openjdk.java.net/%%{project}/%%{repo}
Source0: %{shenandoah_project}-%{shenandoah_repo}-%{shenandoah_revision}.tar.xz

# Custom README for -src subpackage
Source2:  README.md


# run update_systemtap.sh to regenerate or update systemtap sources
# update_package.sh contains hard-coded repos, revisions, tags, and projects to regenerate the source archives
Source8: systemtap_3.2_tapsets_hg-icedtea8-9d464368e06d.tar.xz

# Desktop files. Adapted from IcedTea
Source9: jconsole.desktop.in
Source10: policytool.desktop.in

# nss configuration file
Source11: nss.cfg.in

# Removed libraries that we link instead
Source12: %{name}-remove-intree-libraries.sh

# Ensure we aren't using the limited crypto policy
Source13: TestCryptoLevel.java

# Ensure ECDSA is working
Source14: TestECDSA.java

Source20: repackReproduciblePolycies.sh

# New versions of config files with aarch64 support. This is not upstream yet.
Source100: config.guess
Source101: config.sub

############################################
#
# RPM/distribution specific patches
#
# This section includes patches specific to
# Fedora/RHEL which can not be upstreamed
# either in their current form or at all.
############################################

# Accessibility patches
# Ignore AWTError when assistive technologies are loaded 
Patch1:   rh1648242-accessible_toolkit_crash_do_not_break_jvm.patch
# Restrict access to java-atk-wrapper classes
Patch3:   rh1648644-java_access_bridge_privileged_security.patch
# PR1834, RH1022017: Reduce curves reported by SSL to those in NSS
# Not currently suitable to go upstream as it disables curves
# for all providers unconditionally
Patch525: pr1834-rh1022017-reduce_ellipticcurvesextension_to_provide_only_three_nss_supported_nist_curves_23_24_25.patch
# Turn on AssumeMP by default on RHEL systems
Patch534: rh1648246-always_instruct_vm_to_assume_multiple_processors_are_available.patch

#############################################
#
# Upstreamable patches
#
# This section includes patches which need to
# be reviewed & pushed to the current development
# tree of OpenJDK.
#############################################
# PR2737: Allow multiple initialization of PKCS11 libraries
Patch5: pr2737-allow_multiple_pkcs11_library_initialisation_to_be_a_non_critical_error.patch
# PR2095, RH1163501: 2048-bit DH upper bound too small for Fedora infrastructure (sync with IcedTea 2.x)
Patch504: rh1163501-increase_2048_bit_dh_upper_bound_fedora_infrastructure_in_dhparametergenerator.patch
# Turn off strict overflow on IndicRearrangementProcessor{,2}.cpp following 8140543: Arrange font actions
Patch512: rh1649664-awt2dlibraries_compiled_with_no_strict_overflow.patch
# RH1337583, PR2974: PKCS#10 certificate requests now use CRLF line endings rather than system line endings
Patch523: pr2974-rh1337583-add_systemlineendings_option_to_keytool_and_use_line_separator_instead_of_crlf_in_pkcs10.patch
# PR3083, RH1346460: Regression in SSL debug output without an ECC provider
Patch528: pr3083-rh1346460-for_ssl_debug_return_null_instead_of_exception_when_theres_no_ecc_provider.patch
# RH1566890: CVE-2018-3639
Patch529: rh1566890_speculative_store_bypass_so_added_more_per_task_speculation_control_CVE_2018_3639.patch
# PR3601: Fix additional -Wreturn-type issues introduced by 8061651
Patch530: pr3601-fix_additional_Wreturn_type_issues_introduced_by_8061651_for_prims_jvm_cpp.patch
# Support for building the SunEC provider with the system NSS installation
# PR1983: Support using the system installation of NSS with the SunEC provider
# PR2127: SunEC provider crashes when built using system NSS
# PR2815: Race condition in SunEC provider with system NSS
# PR2899: Don't use WithSeed versions of NSS functions as they don't fully process the seed
# PR2934: SunEC provider throwing KeyException with current NSS
# PR3479, RH1486025: ECC and NSS JVM crash
Patch513: pr1983-rh1565658-support_using_the_system_installation_of_nss_with_the_sunec_provider_jdk8.patch
Patch514: pr1983-rh1565658-support_using_the_system_installation_of_nss_with_the_sunec_provider_root8.patch
Patch515: pr2127-sunec_provider_crashes_when_built_using_system_nss_thus_use_of_nss_memory_management_functions.patch
Patch516: pr2815-race_condition_in_sunec_provider_with_system_nss_fix.patch
Patch517: pr2899-dont_use_withseed_versions_of_nss_functions_as_they_dont_fully_process_the_seed.patch
Patch518: pr2934-sunec_provider_throwing_keyexception_withine.separator_current_nss_thus_initialise_the_random_number_generator_and_feed_the_seed_to_it.patch
Patch519: pr3479-rh1486025-sunec_provider_can_have_multiple_instances_leading_to_premature_nss_shutdown.patch
# PR2888: OpenJDK should check for system cacerts database (e.g. /etc/pki/java/cacerts)
Patch539: pr2888-openjdk_should_check_for_system_cacerts_database_eg_etc_pki_java_cacerts.patch
# PR3575, RH1567204: System cacerts database handling should not affect jssecacerts
Patch540: pr3575-rh1567204-system_cacerts_database_handling_no_longer_affect_jssecacerts.patch
# PR3183, RH1340845: Support Fedora/RHEL8 system crypto policy
Patch300: pr3183-rh1340845-support_fedora_rhel_system_crypto_policy.patch
# PR3655: Allow use of system crypto policy to be disabled by the user
Patch301: pr3655-toggle_system_crypto_policy.patch

#############################################
#
# Arch-specific upstreamable patches
#
# This section includes patches which need to
# be reviewed & pushed upstream and are specific
# to certain architectures. This usually means the
# current OpenJDK development branch, but may also
# include other trees e.g. for the AArch64 port for
# OpenJDK 8u.
#############################################
# s390: PR3593: Use "%z" for size_t on s390 as size_t != intptr_t
Patch103: pr3593-s390_use_z_format_specifier_for_size_t_arguments_as_size_t_not_equals_to_int.patch
# x86: S8199936, PR3533: HotSpot generates code with unaligned stack, crashes on SSE operations (-mstackrealign workaround)
Patch105: jdk8199936-pr3533-enable_mstackrealign_on_x86_linux_as_well_as_x86_mac_os_x.patch
# AArch64: PR3519: Fix further functions with a missing return value (AArch64)
Patch106: pr3519-fix_further_functions_with_a_missing_return_value.patch
# AArch64: JDK-8160748: [AArch64] Inconsistent types for ideal_reg
Patch107: jdk8160748-aarch64_ideal_reg.patch
# AArch64: JDK-8189170: [AArch64] Add option to disable stack overflow checking in primordial thread for use with JNI_CreateJavaJVM
Patch108: jdk8189170-aarch64_primordial_thread.patch

#############################################
#
# Patches which need backporting to 8u
#
# This section includes patches which have
# been pushed upstream to the latest OpenJDK
# development tree, but need to be backported
# to OpenJDK 8u.
#############################################
# S8074839, PR2462: Resolve disabled warnings for libunpack and the unpack200 binary
# This fixes printf warnings that lead to build failure with -Werror=format-security from optflags
Patch502: pr2462-resolve_disabled_warnings_for_libunpack_and_the_unpack200_binary.patch
# S8154313: Generated javadoc scattered all over the place
Patch400: jdk8154313-generated_javadoc_scattered_all_over_the_place.patch
# 8197429, PR3546, RH153662{2,3}: 32 bit java app started via JNI crashes with larger stack sizes
Patch561: jdk8197429-pr3546-rh1536622-increased_stack_guard_causes_segfaults_on_x86_32.patch
# 8171000, PR3542, RH1402819: Robot.createScreenCapture() crashes in wayland mode
Patch563: jdk8171000-pr3542-rh1402819-robot_createScreenCapture_crashes_in_wayland_mode.patch
# 8197546, PR3542, RH1402819: Fix for 8171000 breaks Solaris + Linux builds
Patch564: jdk8197546-pr3542-rh1402819-fix_for_8171000_breaks_solaris_linux_builds.patch
# PR3559: Use ldrexd for atomic reads on ARMv7.
Patch567: pr3559-use_ldrexd_for_atomic_reads_on_armv7_zero.patch
# PR3591: Fix for bug 3533 doesn't add -mstackrealign to JDK code
Patch571: jdk8199936-pr3591-enable_mstackrealign_on_x86_linux_as_well_as_x86_mac_os_x_jdk.patch
# 8184309, PR3596: Build warnings from GCC 7.1 on Fedora 26
Patch572: jdk8184309-pr3596-build_warnings_from_gcc_7_1_on_fedora_26.patch
# 8141570, PR3548: Fix Zero interpreter build for --disable-precompiled-headers
Patch573: jdk8141570-pr3548-fix_zero_interpreter_build_for_disable_precompiled_headers.patch
# 8143245, PR3548: Zero build requires disabled warnings
Patch574: jdk8143245-pr3548-zero_build_requires_disabled_warnings.patch
# 8197981, PR3548: Missing return statement in __sync_val_compare_and_swap_8
Patch575: jdk8197981-pr3548-missing_return_statement_in_sync_val_compare_and_swap_8.patch
# 8064786, PR3599: Fix debug build after 8062808: Turn on the -Wreturn-type warning
Patch576: jdk8064786-pr3599-fix_debug_build_after_8062808_Turn_on_the_wreturn_type_warning.patch
# 8062808, PR3548: Turn on the -Wreturn-type warning
Patch577: jdk8062808-pr3548-turn_on_the_wreturn_type_warning.patch
# s390: JDK-8203030, Type fixing for s390
Patch102: jdk8203030-zero_s390_31_bit_size_t_type_conflicts_in_shared_code.patch
# 8035341: Allow using a system installed libpng
Patch202: jdk8035341-allow_using_system_installed_libpng.patch
# 8042159: Allow using a system-installed lcms2
Patch203: jdk8042159-allow_using_system_installed_lcms2.patch
# 8210761: libjsig is being compiled without optimization
Patch620: jdk8210761-rh1632174-libjsig_is_being_compiled_without_optimization.patch
# 8210647: libsaproc is being compiled without optimization
Patch621: jdk8210647-rh1632174-libsaproc_is_being_compiled_without_optimization.patch
# 8210416: [linux] Poor StrictMath performance due to non-optimized compilation
Patch622: jdk8210416-rh1632174-compile_fdlibm_with_o2_ffp_contract_off_on_gcc_clang_arches.patch
# 8210425: [x86] sharedRuntimeTrig/sharedRuntimeTrans compiled without optimization
#          Upstream 8u part.
Patch623: jdk8210425-rh1632174-01-compile_with_o2_and_ffp_contract_off_as_for_fdlibm.patch
# 8210425: [x86] sharedRuntimeTrig/sharedRuntimeTrans compiled without optimization
#          Aarch64-port 8u local part
Patch624: jdk8210425-rh1632174-02-compile_with_o2_and_ffp_contract_off_as_for_fdlibm_aarch64.patch
# 8210425: [x86] sharedRuntimeTrig/sharedRuntimeTrans compiled without optimization
#          Zero part of the fix for (arm/s390 arches)
Patch625: jdk8210425-rh1632174-03-compile_with_o2_and_ffp_contract_off_as_for_fdlibm_zero.patch

#############################################
#
# Patches appearing in 8u202
#
# This section includes patches which are present
# in the listed OpenJDK 8u release and should be
# able to be removed once that release is out
# and used by this RPM.
#############################################
# 8207057, PR3613: Enable debug information for assembly code files
Patch206: jdk8207057-pr3613-no_debug_info_for_assembler_files_hotspot.patch
Patch207: jdk8207057-pr3613-no_debug_info_for_assembler_files_root.patch
# 8165852, PR3468: (fs) Mount point not found for a file which is present in overlayfs
Patch210: jdk8165852-pr3468-mount_point_not_found_for_a_file_which_is_present_in_overlayfs.patch
# S8073139, RH1191652; fix name of ppc64le architecture
Patch601: jdk8073139-pr1758-rh1191652-ppc64_le_says_its_arch_is_ppc64_not_ppc64le_root.patch
Patch602: jdk8073139-pr1758-rh1191652-ppc64_le_says_its_arch_is_ppc64_not_ppc64le_jdk.patch
Patch603: jdk8073139-pr2236-rh1191652--use_ppc64le_as_the_arch_directory_on_that_platform_and_report_it_in_os_arch_aarch64_forest.patch
# 8044235: src.zip should include all sources
Patch7:   jdk8044235-src_zip_should_include_all_sources.patch
# JDK-8172850, RH1640127: Anti-dependency on membar causes crash in register allocator due to invalid instruction scheduling
Patch583: jdk8172850-rh1640127-01-register_allocator_crash.patch
# JDK-8209639, RH1640127: assert failure in coalesce.cpp: attempted to spill a non-spillable item
Patch584: jdk8209639-rh1640127-02-coalesce_attempted_spill_non_spillable.patch
# JDK-8131048, PR3574, RH1498936: ppc implement CRC32 intrinsic
Patch586: jdk8131048-pr3574-rh1498936-ppc_crc32.patch
# JDK-8164920, PR3574, RH1498936: ppc: enhancement of CRC32 intrinsic
Patch587: jdk8164920-pr3574-rh1498936-ppc_crc32_enhancement.patch

#############################################
#
# Patches appearing in 8u211
#
# This section includes patches which are present
# in the listed OpenJDK 8u release and should be
# able to be removed once that release is out
# and used by this RPM.
#############################################
# JDK-8029661, PR3642, RH1477159: Support TLS v1.2 algorithm in SunPKCS11 provider
Patch585: jdk8029661-pr3642-rh1477159-add_tlsv1_2_support_to_pkcs11_provider.patch
# JDK-8145096, PR3693: Undefined behaviour in HotSpot
Patch588: jdk8145096-pr3693-undefined_behaviour.patch

#############################################
#
# Patches ineligible for 8u
#
# This section includes patches which are present
# upstream, but ineligible for upstream 8u backport.
#############################################
# 8043805: Allow using a system-installed libjpeg
Patch201: jdk8043805-allow_using_system_installed_libjpeg.patch

#############################################
#
# Shenandoah fixes
#
# This section includes patches which are
# specific to the Shenandoah garbage collector
# and should be upstreamed to the appropriate
# trees.
#############################################
# PR3634: Shenandoah still broken on s390 with aarch64-shenandoah-jdk8u181-b16
Patch582: pr3634-fix_shenandoah_for_size_t_on_s390.patch

#############################################
#
# Non-OpenJDK fixes
#
# This section includes patches to code other
# that from OpenJDK.
#############################################
Patch1000: rh1648249-add_commented_out_nss_cfg_provider_to_java_security.patch

#############################################
#
# Dependencies
#
#############################################
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: alsa-lib-devel
BuildRequires: binutils
BuildRequires: cups-devel
BuildRequires: desktop-file-utils
# elfutils only are OK for build without AOT
BuildRequires: elfutils-devel
BuildRequires: fontconfig
BuildRequires: freetype-devel
BuildRequires: giflib-devel
BuildRequires: gcc-c++
BuildRequires: gdb
BuildRequires: gtk2-devel
BuildRequires: lcms2-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: libxslt
BuildRequires: libX11-devel
BuildRequires: libXi-devel
BuildRequires: libXinerama-devel
BuildRequires: libXt-devel
BuildRequires: libXtst-devel
# Requirements for setting up the nss.cfg
BuildRequires: nss-devel
BuildRequires: pkgconfig
BuildRequires: xorg-x11-proto-devel
BuildRequires: zip
BuildRequires: unzip
# Use OpenJDK 7 where available (on RHEL) to avoid
# having to use the rhel-7.x-java-unsafe-candidate hack
%if ! 0%{?fedora} && 0%{?rhel} <= 7
# Require a boot JDK which doesn't fail due to RH1482244
BuildRequires: java-1.7.0-openjdk-devel >= 1.7.0.151-2.6.11.3
%else
BuildRequires: java-1.8.0-openjdk-devel
%endif
# Zero-assembler build requirement
%ifnarch %{jit_arches}
BuildRequires: libffi-devel
%endif
BuildRequires: tzdata-java >= 2015d
# Earlier versions have a bug in tree vectorization on PPC
BuildRequires: gcc >= 4.8.3-8
# Build requirements for SunEC system NSS support
BuildRequires: nss-softokn-freebl-devel >= 3.16.1

%if %{with_systemtap}
BuildRequires: systemtap-sdt-devel
%endif

# this is always built, also during debug-only build
# when it is built in debug-only this package is just placeholder
%{java_rpo %{nil}}

%description
The %{origin_nice} runtime environment %{majorver}.

%if %{include_debug_build}
%package slowdebug
Summary: %{origin_nice} Runtime Environment %{majorver} %{debug_on}
Group:   Development/Languages

%{java_rpo -- %{debug_suffix_unquoted}}
%description slowdebug
The %{origin_nice} runtime environment %{majorver}.
%{debug_warning}
%endif

%if %{include_normal_build}
%package headless
Summary: %{origin_nice} Headless Runtime Environment %{majorver}
Group:   Development/Languages

%{java_headless_rpo %{nil}}

%description headless
The %{origin_nice} runtime environment %{majorver} without audio and video support.
%endif

%if %{include_debug_build}
%package headless-slowdebug
Summary: %{origin_nice} Runtime Environment %{majorver} %{debug_on}
Group:   Development/Languages

%{java_headless_rpo -- %{debug_suffix_unquoted}}

%description headless-slowdebug
The %{origin_nice} runtime environment %{majorver} without audio and video support.
%{debug_warning}
%endif

%if %{include_normal_build}
%package devel
Summary: %{origin_nice} Development Environment %{majorver}
Group:   Development/Tools

%{java_devel_rpo %{nil}}

%description devel
The %{origin_nice} development tools %{majorver}.
%endif

%if %{include_debug_build}
%package devel-slowdebug
Summary: %{origin_nice} Development Environment %{majorver} %{debug_on}
Group:   Development/Tools

%{java_devel_rpo -- %{debug_suffix_unquoted}}

%description devel-slowdebug
The %{origin_nice} development tools %{majorver}.
%{debug_warning}
%endif

%if %{include_normal_build}
%package demo
Summary: %{origin_nice} Demos %{majorver}
Group:   Development/Languages

%{java_demo_rpo %{nil}}

%description demo
The %{origin_nice} demos %{majorver}.
%endif

%if %{include_debug_build}
%package demo-slowdebug
Summary: %{origin_nice} Demos %{majorver} %{debug_on}
Group:   Development/Languages

%{java_demo_rpo -- %{debug_suffix_unquoted}}

%description demo-slowdebug
The %{origin_nice} demos %{majorver}.
%{debug_warning}
%endif

%if %{include_normal_build}
%package src
Summary: %{origin_nice} Source Bundle %{majorver}
Group:   Development/Languages

%{java_src_rpo %{nil}}

%description src
The java-%{origin}-src sub-package contains the complete %{origin_nice} %{majorver}
class library source code for use by IDE indexers and debuggers.
%endif

%if %{include_debug_build}
%package src-slowdebug
Summary: %{origin_nice} Source Bundle %{majorver} %{for_debug}
Group:   Development/Languages

%{java_src_rpo -- %{debug_suffix_unquoted}}

%description src-slowdebug
The java-%{origin}-src-slowdebug sub-package contains the complete %{origin_nice} %{majorver}
 class library source code for use by IDE indexers and debuggers. Debugging %{for_debug}.
%endif

%if %{include_normal_build}
%package javadoc
Summary: %{origin_nice} %{majorver} API documentation
Group:   Documentation
Requires: javapackages-filesystem
BuildArch: noarch

%{java_javadoc_rpo %{nil}}

%description javadoc
The %{origin_nice} %{majorver} API documentation.
%endif

%if %{include_normal_build}
%package javadoc-zip
Summary: %{origin_nice} %{majorver} API documentation compressed in single archive
Group:   Documentation
Requires: javapackages-filesystem
BuildArch: noarch

%{java_javadoc_rpo %{nil}}

%description javadoc-zip
The %{origin_nice} %{majorver} API documentation compressed in single archive.
%endif

%if %{include_debug_build}
%package javadoc-slowdebug
Summary: %{origin_nice} %{majorver} API documentation %{for_debug}
Group:   Documentation
Requires: javapackages-filesystem
BuildArch: noarch

%{java_javadoc_rpo -- %{debug_suffix_unquoted}}

%description javadoc-slowdebug
The %{origin_nice} %{majorver} API documentation %{for_debug}.
%endif

%if %{include_debug_build}
%package javadoc-zip-slowdebug
Summary: %{origin_nice} %{majorver} API documentation compressed in single archive %{for_debug}
Group:   Documentation
Requires: javapackages-filesystem
BuildArch: noarch

%{java_javadoc_rpo -- %{debug_suffix_unquoted}}

%description javadoc-zip-slowdebug
The %{origin_nice} %{majorver} API documentation compressed in single archive %{for_debug}.
%endif


%if %{include_normal_build}
%package accessibility
Summary: %{origin_nice} %{majorver} accessibility connector

%{java_accessibility_rpo %{nil}}

%description accessibility
Enables accessibility support in %{origin_nice} %{majorver} by using java-atk-wrapper. This allows
compatible at-spi2 based accessibility programs to work for AWT and Swing-based
programs.

Please note, the java-atk-wrapper is still in beta, and %{origin_nice} %{majorver} itself is still
being tuned to be working with accessibility features. There are known issues
with accessibility on, so please do not install this package unless you really
need to.
%endif

%if %{include_debug_build}
%package accessibility-slowdebug
Summary: %{origin_nice} %{majorver} accessibility connector %{for_debug}

%{java_accessibility_rpo -- %{debug_suffix_unquoted}}

%description accessibility-slowdebug
See normal java-%{version}-openjdk-accessibility description.
%endif

%prep
if [ %{include_normal_build} -eq 0 -o  %{include_normal_build} -eq 1 ] ; then
  echo "include_normal_build is %{include_normal_build}"
else
  echo "include_normal_build is %{include_normal_build}, thats invalid. Use 1 for yes or 0 for no"
  exit 11
fi
if [ %{include_debug_build} -eq 0 -o  %{include_debug_build} -eq 1 ] ; then
  echo "include_debug_build is %{include_debug_build}"
else
  echo "include_debug_build is %{include_debug_build}, thats invalid. Use 1 for yes or 0 for no"
  exit 12
fi
if [ %{include_debug_build} -eq 0 -a  %{include_normal_build} -eq 0 ] ; then
  echo "You have disabled both include_debug_build and include_normal_build. That is a no go."
  exit 13
fi
%setup -q -c -n %{uniquesuffix ""} -T -a 0
# https://bugzilla.redhat.com/show_bug.cgi?id=1189084
prioritylength=`expr length %{priority}`
if [ $prioritylength -ne 7 ] ; then
 echo "priority must be 7 digits in total, violated"
 exit 14
fi
# For old patches
ln -s %{top_level_dir_name} jdk8

cp %{SOURCE2} .

# replace outdated configure guess script
#
# the configure macro will do this too, but it also passes a few flags not
# supported by openjdk configure script
cp %{SOURCE100} %{top_level_dir_name}/common/autoconf/build-aux/
cp %{SOURCE101} %{top_level_dir_name}/common/autoconf/build-aux/

# OpenJDK patches

# Remove libraries that are linked
sh %{SOURCE12}

# System library fixes
%patch201
%patch202
%patch203

# Debugging fixes
%patch206
%patch207
%patch210

%patch300
%patch301

%patch1
%patch3
%patch5
%patch7

# s390 build fixes
%patch102
%patch103

# AArch64 fixes
%patch106
%patch107
%patch108

# x86 fixes
%patch105

# ppc64le fixes
%patch603
%patch601
%patch602

# Upstreamable fixes
%patch502
%patch504
%patch512
%patch513
%patch514
%patch515
%patch516
%patch517
%patch518
%patch519
%patch400
%patch523
%patch528
%patch529
%patch530
%patch561
%patch563
%patch564
%patch567
%patch571
%patch572
%patch573
%patch574
%patch575
%patch576
%patch577
%patch620
%patch621
%patch622
%patch623
%patch624
%patch625
%patch583
%patch584
%patch585
%patch586
%patch587
%patch588

# RPM-only fixes
%patch525
%patch539
%patch540

# RHEL-only patches
%if ! 0%{?fedora} && 0%{?rhel} <= 7
%patch534
%endif

# Shenandoah patches
%patch582

%patch1000

# Extract systemtap tapsets
%if %{with_systemtap}
tar --strip-components=1 -x -I xz -f %{SOURCE8}
%if %{include_debug_build}
cp -r tapset tapset%{debug_suffix}
%endif


for suffix in %{build_loop} ; do
  for file in "tapset"$suffix/*.in; do
    OUTPUT_FILE=`echo $file | sed -e "s:\.stp\.in$:%{version}-%{release}.%{_arch}.stp:g"`
    sed -e "s:@ABS_SERVER_LIBJVM_SO@:%{_jvmdir}/%{sdkdir -- $suffix}/jre/lib/%{archinstall}/server/libjvm.so:g" $file > $file.1
# TODO find out which architectures other than i686 have a client vm
%ifarch %{ix86}
    sed -e "s:@ABS_CLIENT_LIBJVM_SO@:%{_jvmdir}/%{sdkdir -- $suffix}/jre/lib/%{archinstall}/client/libjvm.so:g" $file.1 > $OUTPUT_FILE
%else
    sed -e "/@ABS_CLIENT_LIBJVM_SO@/d" $file.1 > $OUTPUT_FILE
%endif
    sed -i -e "s:@ABS_JAVA_HOME_DIR@:%{_jvmdir}/%{sdkdir -- $suffix}:g" $OUTPUT_FILE
    sed -i -e "s:@INSTALL_ARCH_DIR@:%{archinstall}:g" $OUTPUT_FILE
    sed -i -e "s:@prefix@:%{_jvmdir}/%{sdkdir -- $suffix}/:g" $OUTPUT_FILE
  done
done
# systemtap tapsets ends
%endif

# Prepare desktop files
for suffix in %{build_loop} ; do
for file in %{SOURCE9} %{SOURCE10} ; do
    FILE=`basename $file | sed -e s:\.in$::g`
    EXT="${FILE##*.}"
    NAME="${FILE%.*}"
    OUTPUT_FILE=$NAME$suffix.$EXT
    sed    -e  "s:@JAVA_HOME@:%{sdkbindir -- $suffix}:g" $file > $OUTPUT_FILE
    sed -i -e  "s:@JRE_HOME@:%{jrebindir -- $suffix}:g" $OUTPUT_FILE
    sed -i -e  "s:@ARCH@:%{version}-%{release}.%{_arch}$suffix:g" $OUTPUT_FILE
    sed -i -e  "s:@JAVA_MAJOR_VERSION@:%{javaver}:g" $OUTPUT_FILE
    sed -i -e  "s:@JAVA_VENDOR@:%{origin}:g" $OUTPUT_FILE
done
done

# Setup nss.cfg
sed -e "s:@NSS_LIBDIR@:%{NSS_LIBDIR}:g" %{SOURCE11} > nss.cfg


%build
# How many CPU's do we have?
export NUM_PROC=%(/usr/bin/getconf _NPROCESSORS_ONLN 2> /dev/null || :)
export NUM_PROC=${NUM_PROC:-1}
%if 0%{?_smp_ncpus_max}
# Honor %%_smp_ncpus_max
[ ${NUM_PROC} -gt %{?_smp_ncpus_max} ] && export NUM_PROC=%{?_smp_ncpus_max}
%endif

%ifarch s390x sparc64 alpha %{power64} %{aarch64}
export ARCH_DATA_MODEL=64
%endif
%ifarch alpha
export CFLAGS="$CFLAGS -mieee"
%endif

# We use ourcppflags because the OpenJDK build seems to
# pass EXTRA_CFLAGS to the HotSpot C++ compiler...
# Explicitly set the C++ standard as the default has changed on GCC >= 6
EXTRA_CFLAGS="%ourcppflags -std=gnu++98 -Wno-error -fno-delete-null-pointer-checks -fno-lifetime-dse"
EXTRA_CPP_FLAGS="%ourcppflags -std=gnu++98 -fno-delete-null-pointer-checks -fno-lifetime-dse"

%ifarch %{power64} ppc
# fix rpmlint warnings
EXTRA_CFLAGS="$EXTRA_CFLAGS -fno-strict-aliasing"
%endif
export EXTRA_CFLAGS

(cd %{top_level_dir_name}/common/autoconf
 bash ./autogen.sh
)

for suffix in %{build_loop} ; do
if [ "x$suffix" = "x" ] ; then
  debugbuild=release
else
  # change --something to something
  debugbuild=`echo $suffix  | sed "s/-//g"`
fi

# Variable used in hs_err hook on build failures
top_dir_abs_path=$(pwd)/%{top_level_dir_name}

mkdir -p %{buildoutputdir -- $suffix}
pushd %{buildoutputdir -- $suffix}

NSS_LIBS="%{NSS_LIBS} -lfreebl" \
NSS_CFLAGS="%{NSS_CFLAGS}" \
bash ../../configure \
%ifnarch %{jit_arches}
    --with-jvm-variants=zero \
%endif
    --with-native-debug-symbols=internal \
    --with-milestone="fcs" \
    --with-update-version=%{updatever} \
    --with-build-number=%{buildver} \
    --with-boot-jdk=/usr/lib/jvm/java-openjdk \
    --with-debug-level=$debugbuild \
    --enable-unlimited-crypto \
    --enable-system-nss \
    --with-zlib=system \
    --with-libjpeg=system \
    --with-giflib=system \
    --with-libpng=system \
    --with-lcms=system \
    --with-stdc++lib=dynamic \
    --with-extra-cxxflags="$EXTRA_CPP_FLAGS" \
    --with-extra-cflags="$EXTRA_CFLAGS" \
    --with-extra-ldflags="%{ourldflags}" \
    --with-num-cores="$NUM_PROC"

cat spec.gmk
cat hotspot-spec.gmk

make \
    JAVAC_FLAGS=-g \
    LOG=trace \
    SCTP_WERROR= \
    %{targets} || ( pwd; find $top_dir_abs_path -name "hs_err_pid*.log" | xargs cat && false )

make zip-docs

# the build (erroneously) removes read permissions from some jars
# this is a regression in OpenJDK 7 (our compiler):
# http://icedtea.classpath.org/bugzilla/show_bug.cgi?id=1437
find images/%{jdkimage} -iname '*.jar' -exec chmod ugo+r {} \;
chmod ugo+r images/%{jdkimage}/lib/ct.sym

# remove redundant *diz and *debuginfo files
find images/%{jdkimage} -iname '*.diz' -exec rm {} \;
find images/%{jdkimage} -iname '*.debuginfo' -exec rm {} \;

# Build screws up permissions on binaries
# https://bugs.openjdk.java.net/browse/JDK-8173610
find images/%{jdkimage} -iname '*.so' -exec chmod +x {} \;
find images/%{jdkimage}/bin/ -exec chmod +x {} \;

popd >& /dev/null

# Install nss.cfg right away as we will be using the JRE above
export JAVA_HOME=$(pwd)/%{buildoutputdir -- $suffix}/images/%{jdkimage}

# Install nss.cfg right away as we will be using the JRE above
install -m 644 nss.cfg $JAVA_HOME/jre/lib/security/

# Use system-wide tzdata
rm $JAVA_HOME/jre/lib/tzdb.dat
ln -s %{_datadir}/javazi-1.8/tzdb.dat $JAVA_HOME/jre/lib/tzdb.dat

# build cycles
done

%check

# We test debug first as it will give better diagnostics on a crash
for suffix in %{rev_build_loop} ; do

export JAVA_HOME=$(pwd)/%{buildoutputdir -- $suffix}/images/%{jdkimage}

# Check unlimited policy has been used
$JAVA_HOME/bin/javac -d . %{SOURCE13}
$JAVA_HOME/bin/java TestCryptoLevel

# Check ECC is working
$JAVA_HOME/bin/javac -d . %{SOURCE14}
$JAVA_HOME/bin/java $(echo $(basename %{SOURCE14})|sed "s|\.java||")

# Check debug symbols are present and can identify code
find "$JAVA_HOME" -iname '*.so' -print0 | while read -d $'\0' lib
do
  if [ -f "$lib" ] ; then
    echo "Testing $lib for debug symbols"
    # All these tests rely on RPM failing the build if the exit code of any set
    # of piped commands is non-zero.

    # Test for .debug_* sections in the shared object. This is the main test
    # Stripped objects will not contain these
    eu-readelf -S "$lib" | grep "] .debug_"
    test $(eu-readelf -S "$lib" | grep -E "\]\ .debug_(info|abbrev)" | wc --lines) == 2

    # Test FILE symbols. These will most likely be removed by anything that
    # manipulates symbol tables because it's generally useless. So a nice test
    # that nothing has messed with symbols
    old_IFS="$IFS"
    IFS=$'\n'
    for line in $(eu-readelf -s "$lib" | grep "00000000      0 FILE    LOCAL  DEFAULT")
    do
     # We expect to see .cpp files, except for architectures like aarch64 and
     # s390 where we expect .o and .oS files
      echo "$line" | grep -E "ABS ((.*/)?[-_a-zA-Z0-9]+\.(c|cc|cpp|cxx|o|oS))?$"
    done
    IFS="$old_IFS"

    # If this is the JVM, look for javaCalls.(cpp|o) in FILEs, for extra sanity checking
    if [ "`basename $lib`" = "libjvm.so" ]; then
      eu-readelf -s "$lib" | \
        grep -E "00000000      0 FILE    LOCAL  DEFAULT      ABS javaCalls.(cpp|o)$"
    fi

    # Test that there are no .gnu_debuglink sections pointing to another
    # debuginfo file. There shouldn't be any debuginfo files, so the link makes
    # no sense either
    eu-readelf -S "$lib" | grep 'gnu'
    if eu-readelf -S "$lib" | grep '] .gnu_debuglink' | grep PROGBITS; then
      echo "bad .gnu_debuglink section."
      eu-readelf -x .gnu_debuglink "$lib"
      false
    fi
  fi
done

# Make sure gdb can do a backtrace based on line numbers on libjvm.so
# javaCalls.cpp:58 should map to:
# http://hg.openjdk.java.net/jdk8u/jdk8u/hotspot/file/ff3b27e6bcc2/src/share/vm/runtime/javaCalls.cpp#l58 
# Using line number 1 might cause build problems. See:
# https://bugzilla.redhat.com/show_bug.cgi?id=1539664
# https://bugzilla.redhat.com/show_bug.cgi?id=1538767
gdb -q "$JAVA_HOME/bin/java" <<EOF | tee gdb.out
handle SIGSEGV pass nostop noprint
handle SIGILL pass nostop noprint
set breakpoint pending on
break javaCalls.cpp:58
commands 1
backtrace
quit
end
run -version
EOF
grep 'JavaCallWrapper::JavaCallWrapper' gdb.out

# Check src.zip has all sources. See RHBZ#1130490
jar -tf $JAVA_HOME/src.zip | grep 'sun.misc.Unsafe'

# Check class files include useful debugging information
$JAVA_HOME/bin/javap -l java.lang.Object | grep "Compiled from"
$JAVA_HOME/bin/javap -l java.lang.Object | grep LineNumberTable
$JAVA_HOME/bin/javap -l java.lang.Object | grep LocalVariableTable

# Check generated class files include useful debugging information
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep "Compiled from"
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep LineNumberTable
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep LocalVariableTable

# build cycles check
done

%install
STRIP_KEEP_SYMTAB=libjvm*

for suffix in %{build_loop} ; do

# Install the jdk
pushd %{buildoutputdir -- $suffix}/images/%{jdkimage}

# Install jsa directories so we can owe them
mkdir -p $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}/server/
mkdir -p $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}/client/

  # Install main files.
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}
  cp -a bin include lib src.zip $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}
  cp -a jre/bin jre/lib $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}

%if %{with_systemtap}
  # Install systemtap support files
  install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset
  # note, that uniquesuffix  is in BUILD dir in this case
  cp -a $RPM_BUILD_DIR/%{uniquesuffix ""}/tapset$suffix/*.stp $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset/
  pushd  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset/
   tapsetFiles=`ls *.stp`
  popd
  install -d -m 755 $RPM_BUILD_ROOT%{tapsetdir}
  for name in $tapsetFiles ; do
    targetName=`echo $name | sed "s/.stp/$suffix.stp/"`
    ln -sf %{_jvmdir}/%{sdkdir -- $suffix}/tapset/$name $RPM_BUILD_ROOT%{tapsetdir}/$targetName
  done
%endif

  # Remove empty cacerts database
  rm -f $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/security/cacerts
  # Install cacerts symlink needed by some apps which hardcode the path
  pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/security
      ln -sf /etc/pki/java/cacerts .
  popd

  # Install versioned symlinks
  pushd $RPM_BUILD_ROOT%{_jvmdir}
    ln -sf %{jredir -- $suffix} %{jrelnk -- $suffix}
  popd

  # Remove javaws man page
  rm -f man/man1/javaws*

  # Install man pages
  install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man1
  for manpage in man/man1/*
  do
    # Convert man pages to UTF8 encoding
    iconv -f ISO_8859-1 -t UTF8 $manpage -o $manpage.tmp
    mv -f $manpage.tmp $manpage
    install -m 644 -p $manpage $RPM_BUILD_ROOT%{_mandir}/man1/$(basename \
      $manpage .1)-%{uniquesuffix -- $suffix}.1
  done

  # Install demos and samples.
  cp -a demo $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}
  mkdir -p sample/rmi
  if [ ! -e sample/rmi/java-rmi.cgi ] ; then 
    # hack to allow --short-circuit on install
    mv bin/java-rmi.cgi sample/rmi
  fi
  cp -a sample $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}

popd


# Install Javadoc documentation
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}
cp -a %{buildoutputdir -- $suffix}/docs $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}
built_doc_archive=`echo "jdk-%{javaver}_%{updatever}$suffix-%{buildver}-docs.zip" | sed  s/slowdebug/debug/`
cp -a %{buildoutputdir -- $suffix}/bundles/$built_doc_archive  $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}.zip

# Install icons and menu entries
for s in 16 24 32 48 ; do
  install -D -p -m 644 \
    %{top_level_dir_name}/jdk/src/solaris/classes/sun/awt/X11/java-icon${s}.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${s}x${s}/apps/java-%{javaver}-%{origin}.png
done

# Install desktop files
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
for e in jconsole$suffix policytool$suffix ; do
    desktop-file-install --vendor=%{uniquesuffix -- $suffix} --mode=644 \
        --dir=$RPM_BUILD_ROOT%{_datadir}/applications $e.desktop
done

# Install /etc/.java/.systemPrefs/ directory
# See https://bugzilla.redhat.com/show_bug.cgi?id=741821
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/.java/.systemPrefs

# FIXME: remove SONAME entries from demo DSOs. See
# https://bugzilla.redhat.com/show_bug.cgi?id=436497

# Find non-documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/sample \
  -type f -o -type l | sort \
  | grep -v README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  >> %{name}-demo.files"$suffix"
# Find documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/sample \
  -type f -o -type l | sort \
  | grep README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  | sed 's|^|%doc |' \
  >> %{name}-demo.files"$suffix"

# Create links which leads to separately installed java-atk-bridge and allow configuration
# links points to java-atk-wrapper - an dependence
  pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}
    ln -s %{_libdir}/java-atk-wrapper/libatk-wrapper.so.0 libatk-wrapper.so
  popd
  pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/ext
     ln -s %{_libdir}/java-atk-wrapper/java-atk-wrapper.jar  java-atk-wrapper.jar
  popd
  pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/
    echo "#Config file to  enable java-atk-wrapper" > accessibility.properties
    echo "" >> accessibility.properties
    echo "assistive_technologies=org.GNOME.Accessibility.AtkWrapper" >> accessibility.properties
    echo "" >> accessibility.properties
  popd


bash %{SOURCE20} $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix} %{javaver}
# https://bugzilla.redhat.com/show_bug.cgi?id=1183793
touch -t 201401010000 $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/security/java.security

# moving config files to /etc
mkdir -p $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}/lib/security/policy/unlimited/
mkdir -p $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}/lib/security/policy/limited/
for file in lib/security/cacerts lib/security/policy/unlimited/US_export_policy.jar lib/security/policy/unlimited/local_policy.jar lib/security/policy/limited/US_export_policy.jar lib/security/policy/limited/local_policy.jar lib/security/java.policy lib/security/java.security lib/security/blacklisted.certs lib/logging.properties lib/calendars.properties lib/security/nss.cfg ; do
  mv      $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/$file   $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}/$file
  ln -sf  %{etcjavadir -- $suffix}/$file                          $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/$file
done

# stabilize permissions
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -name "*.so" -exec chmod 755 {} \; ; 
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -type d -exec chmod 755 {} \; ; 
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -name "ASSEMBLY_EXCEPTION" -exec chmod 644 {} \; ; 
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -name "LICENSE" -exec chmod 644 {} \; ; 
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -name "THIRD_PARTY_README" -exec chmod 644 {} \; ; 

# end, dual install
done

%if %{include_normal_build}
# intentionally only for non-debug
%pretrans headless -p <lua>
-- see https://bugzilla.redhat.com/show_bug.cgi?id=1038092 for whole issue
-- see https://bugzilla.redhat.com/show_bug.cgi?id=1290388 for pretrans over pre
-- if copy-jdk-configs is in transaction, it installs in pretrans to temp
-- if copy_jdk_configs is in temp, then it means that copy-jdk-configs is in transaction  and so is
-- preferred over one in %%{_libexecdir}. If it is not in transaction, then depends
-- whether copy-jdk-configs is installed or not. If so, then configs are copied
-- (copy_jdk_configs from %%{_libexecdir} used) or not copied at all
local posix = require "posix"
local debug = false

SOURCE1 = "%{rpm_state_dir}/copy_jdk_configs.lua"
SOURCE2 = "%{_libexecdir}/copy_jdk_configs.lua"

local stat1 = posix.stat(SOURCE1, "type");
local stat2 = posix.stat(SOURCE2, "type");

  if (stat1 ~= nil) then
  if (debug) then
    print(SOURCE1 .." exists - copy-jdk-configs in transaction, using this one.")
  end;
  package.path = package.path .. ";" .. SOURCE1
else
  if (stat2 ~= nil) then
  if (debug) then
    print(SOURCE2 .." exists - copy-jdk-configs already installed and NOT in transaction. Using.")
  end;
  package.path = package.path .. ";" .. SOURCE2
  else
    if (debug) then
      print(SOURCE1 .." does NOT exists")
      print(SOURCE2 .." does NOT exists")
      print("No config files will be copied")
    end
  return
  end
end
-- run content of included file with fake args
arg = {"--currentjvm", "%{uniquesuffix %{nil}}", "--jvmdir", "%{_jvmdir %{nil}}", "--origname", "%{name}", "--origjavaver", "%{javaver}", "--arch", "%{_arch}", "--temp", "%{rpm_state_dir}/%{name}.%{_arch}"}
require "copy_jdk_configs.lua"

%post
%{post_script %{nil}}

%post headless
%{post_headless %{nil}}

%postun
%{postun_script %{nil}}

%postun headless
%{postun_headless %{nil}}

%posttrans
%{posttrans_script %{nil}}

%post devel
%{post_devel %{nil}}

%postun devel
%{postun_devel %{nil}}

%posttrans  devel
%{posttrans_devel %{nil}}

%post javadoc
%{post_javadoc %{nil}}

%postun javadoc
%{postun_javadoc %{nil}}

%post javadoc-zip
%{post_javadoc_zip %{nil}}

%postun javadoc-zip
%{postun_javadoc_zip %{nil}}
%endif

%if %{include_debug_build}
%post slowdebug
%{post_script -- %{debug_suffix_unquoted}}

%post headless-slowdebug
%{post_headless -- %{debug_suffix_unquoted}}

%postun slowdebug
%{postun_script -- %{debug_suffix_unquoted}}

%postun headless-slowdebug
%{postun_headless -- %{debug_suffix_unquoted}}

%posttrans slowdebug
%{posttrans_script -- %{debug_suffix_unquoted}}

%post devel-slowdebug
%{post_devel -- %{debug_suffix_unquoted}}

%postun devel-slowdebug
%{postun_devel -- %{debug_suffix_unquoted}}

%posttrans  devel-slowdebug
%{posttrans_devel -- %{debug_suffix_unquoted}}

%post javadoc-slowdebug
%{post_javadoc -- %{debug_suffix_unquoted}}

%postun javadoc-slowdebug
%{postun_javadoc -- %{debug_suffix_unquoted}}

%post javadoc-zip-slowdebug
%{post_javadoc_zip -- %{debug_suffix_unquoted}}

%postun javadoc-zip-slowdebug
%{postun_javadoc_zip -- %{debug_suffix_unquoted}}
%endif

%if %{include_normal_build}
%files
# main package builds always
%{files_jre %{nil}}
%else
%files
# placeholder
%endif


%if %{include_normal_build}
%files headless
# important note, see https://bugzilla.redhat.com/show_bug.cgi?id=1038092 for whole issue
# all config/noreplace files (and more) have to be declared in pretrans. See pretrans
%{files_jre_headless %{nil}}

%files devel
%{files_devel %{nil}}

%files demo -f %{name}-demo.files
%{files_demo %{nil}}

%files src
%{files_src %{nil}}

%files javadoc
%{files_javadoc %{nil}}

# this puts huge file to /usr/share
# unluckily ti is really a documentation file
# and unluckily it really is architecture-dependent, as eg. aot and grail are now x86_64 only
# same for debug variant
%files javadoc-zip
%{files_javadoc_zip %{nil}}

%files accessibility
%{files_accessibility %{nil}}
%endif

%if %{include_debug_build}
%files slowdebug
%{files_jre -- %{debug_suffix_unquoted}}

%files headless-slowdebug
%{files_jre_headless -- %{debug_suffix_unquoted}}

%files devel-slowdebug
%{files_devel -- %{debug_suffix_unquoted}}

%files demo-slowdebug -f %{name}-demo.files-slowdebug
%{files_demo -- %{debug_suffix_unquoted}}

%files src-slowdebug
%{files_src -- %{debug_suffix_unquoted}}

%files javadoc-slowdebug
%{files_javadoc -- %{debug_suffix_unquoted}}

%files javadoc-zip-slowdebug
%{files_javadoc_zip -- %{debug_suffix_unquoted}}

%files accessibility-slowdebug
%{files_accessibility -- %{debug_suffix_unquoted}}
%endif

%changelog
* Thu Feb 07 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.201.b09-2
- Fix invalid dates earlier in the ChangeLog.
- Resolves: rhbz#1661577

* Thu Feb 07 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.201.b09-2
- Add PR3655 to allow the system crypto policy to be turned off.
- Resolves: rhbz#1661577

* Wed Feb 06 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:1.8.0.201.b09-1
- Add backport of JDK-8145096 (PR3693) to fix undefined behaviour issues on newer GCCs
- Resolves: rhbz#1661577

* Tue Feb 05 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.201.b09-0
- Update to aarch64-shenandoah-jdk8u201-b09.
- Resolves: rhbz#1661577

* Wed Jan 30 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.192.b12-0
- Update to aarch64-shenandoah-jdk8u192-b12.
- Remove patches included upstream
  - JDK-8031668/PR2842
  - JDK-8148351/PR2842
  - JDK-6260348/PR3066
  - JDK-8061305/PR3335/RH1423421
  - JDK-8188030/PR3459/RH1484079
  - JDK-8205104/PR3539/RH1548475
  - JDK-8185723/PR3553
  - JDK-8186461/PR3557
  - JDK-8201509/PR3579
  - JDK-8075942/PR3602
  - JDK-8203182/PR3603
  - JDK-8206406/PR3610/RH1597825
  - JDK-8206425
  - JDK-8036003
  - JDK-8201495/PR2415
  - JDK-8150954/PR2866/RH1176206
- Re-generate patches (mostly due to upstream build changes)
  - JDK-8073139/PR1758/RH1191652
  - JDK-8143245/PR3548 (due to JDK-8202600)
  - JDK-8197429/PR3546/RH1536622 (due to JDK-8189170)
  - JDK-8199936/PR3533
  - JDK-8199936/PR3591
  - JDK-8207057/PR3613
  - JDK-8210761/RH1632174 (due to JDK-8207402)
  - PR3559 (due to JDK-8185723/JDK-8186461/JDK-8201509)
  - PR3593 (due to JDK-8081202)
  - RH1566890/CVE-2018-3639 (due to JDK-8189170)
  - RH1649664 (due to JDK-8196516)
- Add 8160748 for AArch64 which is missing from upstream 8u version.
- Add port of 8189170 to AArch64 which is missing from upstream 8u version.
- Resolves: rhbz#1661577

* Mon Jan 28 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b14-1
- Add 8131048 & 8164920 (PR3574/RH1498936) to provide a CRC32 intrinsic for PPC64.
- Resolves: rhbz#1661577

* Thu Jan 24 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b14-0
- Introduce sa_arches for architectures with sa-jdi.jar and include aarch64
- Resolves: rhbz#1661577

* Thu Jan 10 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b14-0
- Update to aarch64-shenandoah-jdk8u191-b14.
- Adjust JDK-8073139/PR1758/RH1191652 to apply following 8155627 backport.
- Resolves: rhbz#1661577

* Wed Jan 09 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b13-0
- Update to aarch64-shenandoah-jdk8u191-b13.
- Update tarball generation script in preparation for PR3667/RH1656676 SunEC changes.
- Use remove-intree-libraries.sh to remove the remaining SunEC code for now.
- Resolves: rhbz#1661577

* Sat Dec 22 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b12-12
- Add backport of JDK-8029661 which adds TLSv1.2 support to the PKCS11 provider.
- Resolves: rhbz#1661577

* Sat Dec 22 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b12-11
- Revise Shenandoah PR3634 patch following upstream discussion.
- Resolves: rhbz#1661577

* Wed Dec 19 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.191.b12-11
- Refactor _find_debuginfo_opts -g (global over define)
- Resolves: rhbz#1661577

* Wed Nov 07 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.191.b12-9
- headfull suggests of cups, replaced by Requires of cups-libs in headless
- Resolves: rhbz#1661577

* Wed Nov 07 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b12-9
- Note why PR1834/RH1022017 is not suitable to go upstream in its current form.
- Resolves: rhbz#1661577

* Mon Nov 05 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b12-9
- Document patch sections.
- Resolves: rhbz#1661577

* Mon Nov 05 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b12-9
- Fix patch organisation in the spec file:
-   * Move ECC patches back to upstreamable section
-   * Move system cacerts & crypto policy patches to upstreamable section
-   * Merge "Local fixes" and "RPM fixes" which amount to the same thing
-   * Move system libpng & lcms patches back to 8u upstreamable section
- Resolves: rhbz#1661577

* Fri Oct 26 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.191.b12-8
- added Patch583 jdk8172850-rh1640127-01-register_allocator_crash.patch
- added Patch584 jdk8209639-rh1640127-02-coalesce_attempted_spill_non_spillable.patch
- Resolves: rhbz#1661577

* Tue Oct 23 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.191.b12-2
- cups moved to headful package
- Resolves: rhbz#1633817

* Tue Oct 23 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.191.b12-1
- updated to aarch64-shenandoah-jdk8u191-b12
- deleted 8146115-pr3508-rh1463098.patch, pr3619.patch, pr3620.patch - should be upstreamed
- create pr3634-fix_shenandoah_for_size_t_on_s390.patch to fix build failure on s390
- Resolves: rhbz#1633817

* Fri Oct 12 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.181.b15-7
- Add patch jdk8210425-rh1632174-03-compile_with_o2_and_ffp_contract_off_as_for_fdlibm_zero.patch:
  - Annother fix for optimization gaps (annocheck issues)
  - Zero 8u version fix was missing. Hence, only shows up on Zero arches.
- Resolves: rhbz#1633817

* Tue Oct 09 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b12-0
- Update to aarch64-shenandoah-jdk8u191-b12.
- Resolves: rhbz#1633817

* Mon Oct 08 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.181.b15-6
- Refreshed upstreamed patches (from 8u202):
  - jdk8044235-src_zip_should_include_all_sources.patch: src.zip should include all sources.
  - jdk8073139-pr2236-rh1191652--use_ppc64le_as_the_arch_directory_on_that_platform_and_report_it_in_os_arch_aarch64_forest.patch,
    jdk8073139-pr1758-rh1191652-ppc64_le_says_its_arch_is_ppc64_not_ppc64le_jdk.patch,
    jdk8073139-pr1758-rh1191652-ppc64_le_says_its_arch_is_ppc64_not_ppc64le_root.patch: PPC64LE JVM reporting issues.
- Moved both patch series to 8u202 sections.
- Resolves: rhbz#1633817

* Tue Oct 02 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.191.b10-0
- Update to aarch64-shenandoah-jdk8u191-b10.
- Drop 8146115/PR3508/RH1463098 applied upstream.
- Resolves: rhbz#1633817

* Mon Oct 01 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b16-0
- Add new Shenandoah patch PR3634 as upstream still fails on s390.
- Resolves: rhbz#1633817

* Mon Oct 01 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b16-0
- Update to aarch64-shenandoah-jdk8u181-b16.
- Drop PR3619 & PR3620 Shenandoah patches which should now be fixed upstream.
- Resolves: rhbz#1633817

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b15-0
- Move to single OpenJDK tarball build, based on aarch64/shenandoah-jdk8u.
- Update to aarch64-shenandoah-jdk8u181-b15.
- Drop 8165489-pr3589.patch which was only applied to aarch64/jdk8u builds.
- Split ppc64 Shenandoah fix into separate patch file with its own bug ID (PR3620).
- Update pr3539-rh1548475.patch to apply after 8187045.
- Resolves: rhbz#1633817

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b13-10
- Remove unneeded functions from ppc shenandoahBarrierSet.
- Resolves: rhbz#1640188

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b13-10
- Add missing shenandoahBarrierSet implementation for ppc64{be,le}.
- Resolves: rhbz#1640188

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b13-10
- Fix wrong format specifiers in Shenandoah code.
- Resolves: rhbz#1640188

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b13-10
- Avoid changing variable types to fix size_t, at least for now.
- Resolves: rhbz#1640188

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b13-10
- More size_t fixes for Shenandoah.
- Resolves: rhbz#1640188

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b13-10
- Add additional s390 size_t case for Shenandoah.
- Resolves: rhbz#1640188

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b13-10
- Attempt to fix Shenandoah build issues on s390.
- Resolves: rhbz#1640188

* Mon Oct 1 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181.b13-10
- Use the Shenandoah HotSpot on all architectures.
- Resolves: rhbz#1640188

* Mon Oct 01 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.181.b15-5
- Add explicit requirement for libXcomposite which is used when performing
  screenshots from Java.
- Add explicit BR unzip required for building OpenJDK.
- Resolves: rhbz#1633817

* Thu Sep 27 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.181.b15-4
- Add fixes for optimization gaps (annocheck issues):
  - 8210761: libjsig is being compiled without optimization
  - 8210647: libsaproc is being compiled without optimization
  - 8210416: [linux] Poor StrictMath performance due to non-optimized compilation
  - 8210425: [x86] sharedRuntimeTrig/sharedRuntimeTrans compiled without optimization
             8u upstream and aarch64/jdk8u upstream versions.
- Resolves: rhbz#1633817

* Wed Sep 26 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.181.b15-3
- Renamed more patches for clarity:
  include-all-srcs.patch => jdk8044235-src_zip_should_include_all_sources.patch
  java-1.8.0-openjdk-rh1191652-hotspot-aarch64.patch => jdk8073139-pr2236-rh1191652--use_ppc64le_as_the_arch_directory_on_that_platform_and_report_it_in_os_arch_aarch64_forest.patch
  java-1.8.0-openjdk-rh1191652-jdk.patch => jdk8073139-pr1758-rh1191652-ppc64_le_says_its_arch_is_ppc64_not_ppc64le_jdk.patch
  java-1.8.0-openjdk-rh1191652-root.patch => jdk8073139-pr1758-rh1191652-ppc64_le_says_its_arch_is_ppc64_not_ppc64le_root.patch
- Resolves: rhbz#1633817

* Tue Sep 18 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.181.b15-2
- Update(s) from upstreamed patches:
  - 8036003-dont-add-unnecessary-debug-links.patch =>
    jdk8036003-add_with_native_debug_symbols_configure_flag.patch
  - rh1176206-jdk.patch =>
    jdk8150954-pr2866-rh1176206-screenshot_xcomposite_jdk.patch =>
    Deleted rh1176206-root.patch as thats no longer needed with
    upstream 8150954.
  - Refreshed jdk8165852-pr3468-mount_point_not_found_for_a_file_which_is_present_in_overlayfs.patch from upstream.
  - Refreshed jdk8201495-zero_reduce_limits_of_max_heap_size_for_boot_JDK_on_s390.patch from upstream.
  - 8207057-pr3613-hotspot-assembler-debuginfo.patch =>
    jdk8207057-pr3613-no_debug_info_for_assembler_files_hotspot.patch and
    jdk8207057-pr3613-no_debug_info_for_assembler_files_root.patch. From JDK 8u
    review.
- Renamed pr2842-02.patch => jdk8148351-pr2842-02-only_display_resolved_symlink_for_compiler_do_not_change_path.patch.
- Renamed spec-only patch:
  pr3183.patch => pr3183-rh1340845-support_fedora_rhel_system_crypto_policy.patch
- Renamed java-1.8.0-openjdk-size_t.patch =>
  jdk8201495-zero_reduce_limits_of_max_heap_size_for_boot_JDK_on_s390.patch
- Moved SunEC provider via system NSS to RPM specific patches section.
- Moved upstream 8u patches to appropriate sections (8u192/8u202).
- Removed rh1214835.patch since it's invalid. See:
  https://icedtea.classpath.org/bugzilla/show_bug.cgi?id=2304#c3
- Use --with-native-debug-symbols=internal which JDK-8036003 adds.
- Resolves: rhbz#1633817

* Tue Sep 11 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.181.b15-1
- fixed unexpanded arch in policy tool desktop file
- fixed versions (8->1.8.0) of images used in desktop files
- Resolves: rhbz#1633817

* Mon Aug 27 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.181.b13-9
- Adjust system jpeg patch, jdk8043805-allow_using_system_installed_libjpeg.patch, so as to filter
  -Wl,--as-needed. Resolves RHBZ#1622186.
- Resolves: rhbz#1633817

* Mon Aug 27 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.181.b13-8
- Adjust system NSS patch, pr1983-rh1565658-support_using_the_system_installation_of_nss_with_the_sunec_provider_jdk8.patch, so as to filter
  -Wl,--as-needed. Resolves RHBZ#1622186.
- Resolves: rhbz#1633817

* Wed Aug 01 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.181.b13-7
- build number moved from release to version

* Mon Jul 23 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-7.b13
- Remove duplicate -mstackrealign workaround.

* Mon Jul 23 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-6.b13
- Bump release for previous changeset.

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-6.b13
- Update to aarch64-jdk8u181-b13 and aarch64-shenandoah-jdk8u181-b13.
- Remove 8187577/PR3578 now applied upstream.

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-5.b04
- Update bug status and add missing bug IDs

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-5.b04
- Add "8146115, PR3508, RH1463098: Improve docker container detection and resource configuration usage"

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-4.b04
- Add "8206406, PR3610, RH1597825: StubCodeDesc constructor publishes partially-constructed objects on StubCodeDesc::_list"

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-4.b04
- Mark bugs now backported to OpenJDK 8u upstream

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-3.b04
- Backport "8203182, PR3603: Release session if initialization of SunPKCS11 Signature fails"

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-2.b04
- Backport "8075942, PR3602: ArrayIndexOutOfBoundsException in sun.java2d.pisces.Dasher.goTo"

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-1.b04
- Add missing bug identifiers for patches unique to RHEL 8 and move to correct sections.

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-1.b04
- Mark bugs that have been pushed to 8u upstream and are scheduled for a release.

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-1.b04
- Update to aarch64-jdk8u181-b04 and aarch64-shenandoah-jdk8u181-b04.

* Mon Jul 23 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.181-0.b03
- Update to aarch64-jdk8u181-b03 and aarch64-shenandoah-jdk8u181-b03.
- Remove AArch64 patch for PR3458/RH1540242 as applied upstream.

* Sun Jul 22 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.172-17.b11
- Fix bad output file name substitution for SystemTap files.

* Wed Jul 18 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.172-17.b11
- Update Shenandoah tarball to fix TCK overflow failure.

* Tue Jul 17 2018 Jiri Vanek <jvanek@redhat.com> - 11:1.8.0.172-16.b11
- added Recommends gtk2 for main package
- added Suggests lksctp-tools, pcsc-lite-devel, cups for headless package
- see RHBZ1598152

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.8.0.172-15.b11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jul 10 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.172-14.b11
- Fix hook to show hs_err*.log files on failures.

* Mon Jul 02 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.172-13.b11
- Fix requires/provides filters for internal libs. See
  RHBZ#1590796

* Mon Jun 25 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.172-12.b11
- Add hook to show hs_err*.log files on failures.

* Wed Jun 20 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.172-11.b11
- Expose release/slowdebug builds being produced via conditionals.

* Wed Jun 20 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.172-11.b11
- Add additional fix (PR3601) to fix -Wreturn-type failures introduced by 8061651
- Backport 8064786 (PR3601) to fix -Wreturn-type failure on debug builds.
- Bring in PR3519 from IcedTea 3.7.0 to fix remaining -Wreturn-type failure on AArch64.
- Sync with IcedTea 3.8.0 patches to use -Wreturn-type.
- Add backports of 8141570, 8143245, 8197981 & 8062808.
- Drop pr3458-rh1540242-zero.patch which is covered by 8143245.

* Wed Jun 20 2018 Jiri Vanek <jvanek@redhat.com> - 11:1.8.0.172-10.b11
- jsa files changed to 444 to pass rpm verification

* Mon Jun 18 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.172-9.b11
- Filter private provides/requires: 'lib.so(SUNWprivate_.*'

* Thu Jun 14 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.172-8.b11
- Add provides/requires for libjvm.so back. See RHBZ#1591215.

* Wed Jun 13 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.172-7.b11
- Fix reg-ex for filtering private libraries' provides/requires.

* Wed Jun 13 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.172-6.b11
- Remove build flags exemption for aarch64 now the platform is more mature and can bootstrap OpenJDK with these flags.
- Remove duplicate -fstack-protector-strong; it is provided by the RHEL cflags.
- Add missing changelog credits

* Mon Jun 11 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.172-5.b11
- Merge changes from RHEL 7

* Mon Jun 11 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.172-5.b11
- Read jssecacerts file prior to trying either cacerts file (system or local) (PR3575)

* Mon Jun 11 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.172-5.b11
- Fix a number of bad bug identifiers (PR3546 should be PR3578, PR3456 should be PR3546)

* Thu Jun 07 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.172-5.b11
- Update Shenandoah tarball to include 2018-05-15 merge.
- Split PR3458/RH1540242 fix into AArch64 & Zero sections, so former can be skipped on Shenandoah builds.
- Drop PR3573 patch applied upstream.
- Restrict 8187577 fix to non-Shenandoah builds, as it's included in the new tarball.

* Thu Jun 07 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.172-5.b11
- Sync with IcedTea 3.8.0.
- Label architecture-specific fixes with architecture concerned
- x86: S8199936, PR3533: HotSpot generates code with unaligned stack, crashes on SSE operations (-mstackrealign workaround)
- PR3539, RH1548475: Pass EXTRA_LDFLAGS to HotSpot build
- 8171000, PR3542, RH1402819: Robot.createScreenCapture() crashes in wayland mode
- 8197546, PR3542, RH1402819: Fix for 8171000 breaks Solaris + Linux builds
- 8185723, PR3553: Zero: segfaults on Power PC 32-bit
- 8186461, PR3557: Zero's atomic_copy64() should use SPE instructions on linux-powerpcspe
- PR3559: Use ldrexd for atomic reads on ARMv7.
- 8187577, PR3578: JVM crash during gc doing concurrent marking
- 8201509, PR3579: Zero: S390 31bit atomic_copy64 inline assembler is wrong
- 8165489, PR3589: Missing G1 barrier in Unsafe_GetObjectVolatile
- PR3591: Fix for bug 3533 doesn't add -mstackrealign to JDK code
- 8184309, PR3596: Build warnings from GCC 7.1 on Fedora 26

* Wed Jun 06 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.172-1.b11
- updated to u172-b11
- removed patches:
- patch207 8200556-pr3566.patch
- patch104 pr3458-rh1540242.patch
- patch209 8035496-hotspot.patch
- patch700 pr3573-fix_TCK_crash_with_shenandoah_in_shenandoahsupport_cpp_in_case_of_dead_brnach_in_is_independent.patch
- fixed issue with atkwrapper wrongly palced broken symlink
- fixed libjvm path for system tap
- returned patch104 pr3458-rh1540242.patch

* Mon Jun 04 2018 Jiri Vanek <jvanek@redhat.com> - 1:10.0.1.10-7
- quoted sed expressions, changed possibly confussing # by @
- added vendor(origin) into icons
- removed last trace of relative symlinks
- added BuildRequires of javapackages-tools to fix build failure after Requires change to javapackages-filesystem

* Fri Jun 01 2018 Jiri Vanek <jvanek@redhat.com>  - 1:1.8.0.171-6.b10
- aligning with java-openjdk in fedora:
- removed fx binding
- config files to etc
- slowdebug instead simply debug subpackage
- purged provides
- many macros renamed
- typos correction
- bumped jstack (may be wrong)

* Wed May 09 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.171-5.b10
- Compile i686 JDK with -mstackrealign.

* Wed Apr 25 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.171-4.b10
- Enable hardened build unconditionally (also for Zero).
  Resolves RHBZ#1290936.

* Tue Apr 24 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.171-3.b10
- Enable hardened build for Aarch64.

* Tue Apr 24 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.171-2.b10
- Update rhbz1548475-LDFLAGSusage.patch to also set linker
  flags for libsaproc.so and libjsig.so.

* Wed Apr 18 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.171-1.b10
- Update to aarch64-jdk8u171-b10 and aarch64-shenandoah-jdk8u171-b10.
- Fix jconsole.desktop.in subcategory, replacing "Monitor" with "Profiling" (PR3550) (gnu_andrew)
- Fix invalid license 'LGPL+' (should be LGPLv2+ for ECC code) and add misisng ones (gnu_andrew)

* Wed Apr 18 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.162-7.b12
- added ownership of policy dir and subdirs
- removed ignored attributes for classes.jsa

* Tue Apr 10 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.162-6.b12
- Use correct patch for RHBZ#1538767 (JDK-8196516)

* Mon Apr 02 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.162-5.b12
- Cleanup from previous commit.
- Remove unused upstream patch 8167200.hotspotAarch64.patch.

* Thu Mar 29 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.162-3.b12
- returned patch562 rhbz_1540242.patch
- added Patch563 rhbz_1536622-JDK8197429-jdk8.patch

* Mon Mar 26 2018 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.162-2.b12
- Added  patch 540 rhbz1548475-LDFLAGSusage.patch to honor build flags fully

* Wed Mar 21 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.162-1.b12
- Update to aarch64-jdk8u162-b12 and aarch64-shenandoah-jdk8u162-b12.
- Remove upstreamed patches for 8181055/PR3394/RH1448880,
-  8181419/PR3413/RH1463144, 8145913/PR3466/RH1498309,
-  8168318/PR3466/RH1498320, 8170328/PR3466/RR1498321 and
-  8181810/PR3466/RH1498319.

* Wed Mar 07 2018 Adam Williamson <awilliam@redhat.com> - 1:1.8.0.161-9.b14
- Rebuild to fix GCC 8 mis-compilation
  See https://da.gd/YJVwk ("GCC 8 ABI change on x86_64")

* Sun Feb 11 2018 Sandro Mani <manisandro@gmail.com> - 1:1.8.0.161-8.b14
- Rebuild (giflib)

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1:1.8.0.161-7.b14
- Escape macros in %%changelog

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.8.0.161-6.b14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 31 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.161-5.b14
- Additional fix needed for FTBFS bug on aarch64.
  Resolves RHBZ#1540242.

* Wed Jan 31 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.161-4.b14
- Add fix for FTBFS on aarch64 and armv7hl.
  Resolves RHBZ#1540242.

* Tue Jan 30 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.161-3.b14
- Include Aarch64 build fixes post January 2018 CPU.

* Mon Jan 29 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.161-2.b14
- Work around ppc64le gdb backtrace problem in %%check.
  See RHBZ#1539664

* Wed Jan 24 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.161-1.b14
- Fix FTBFS due to link failure in libfontmanager.so
- See RHBZ#1538767

* Wed Jan 24 2018 jvanek <jvanek@redhat.com> - 1:1.8.0.161-0.b14
- updated to u161, rmeoved upstreamed patches
- removed patch555 8164293-pr3412-rh1459641.patch
- removed patch550 8175813-pr3394-rh1448880.patch
- removed patch547 8173941-pr3326.patch
- removed patch532 8162384-pr3122-rh1358661.patch
- removed patch535 8153711-pr3313-rh1284948.patch
- removed patch561 8075484-pr3473-rh1490713.patch
- removed patch554 8175887-pr3415.patch

* Mon Nov 13 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.151-1.b12
- added ownership of etc dirs
- sysconfdir/.java/.systemPrefs
- sysconfdir/.java

* Wed Oct 25 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.151-1.b12
- updated to aarch64-jdk8u151-b12 (from aarch64-port/jdk8u)
- updated to aarch64-shenandoah-jdk8u151-b12 (from aarch64-port/jdk8u-shenandoah) of hotspot
- used aarch64-port-jdk8u-aarch64-jdk8u151-b12.tar.xz as new sources
- used aarch64-port-jdk8u-shenandoah-aarch64-shenandoah-jdk8u151-b12.tar.xz as new sources for hotspot
- tapset updated to 3.6pre02
- policies adapted to new limited/unlimited schmea
- above acomapnied by c-j-c 3.3
- alligned patches and added PPC ones (thanx to gnu_andrew)
- added patch209: 8035496-hotspot.patch
- added patch210: suse_linuxfilestore.patch

* Wed Oct 04 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.144-7.b01
- updated to aarch64-shenandoah-jdk8u144-b02-shenandoah-merge-2017-10-02 (from aarch64-port/jdk8u-shenandoah) of hotspot
- used aarch64-port-jdk8u-shenandoah-aarch64-shenandoah-jdk8u144-b02-shenandoah-merge-2017-10-02.tar.xz as new sources for hotspot

* Fri Sep 15 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.144-6.b01
- added patch540, bug1484079.patch

* Fri Sep 08 2017 Troy Dawson <tdawson@redhat.com> - 1:1.8.0.144-6.b01
- Cleanup spec file conditionals

* Fri Aug 25 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.144-4.b01
- added ownership of diretories which were oonly listing files

* Fri Aug 25 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.144-3.b01
- added (experiment) "--" delimiter also to $suffix in expanding macros

* Wed Aug 23 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.144-1.b01
- Update to aarch64-jdk8u144-b01 and aarch64-shenandoah-jdk8u144-b01.
- Exclude 8175887 from Shenandoah builds as it has been included in that repo.
- Added 8164293-pr3412-rh1459641.patch backport from 8u development tree
- get rid of bin/* and lib/*, fixed rhbz1480777
- adapted to rpm 4.14: all expanding macros changed to define, all %1 and %%1 replaced by %%{?1}, all expandable macros parameter preffixed by --
- get rid of generated filelists all except javafx and demos

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.8.0.141-5.b16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Sun Jul 30 2017 Florian Weimer <fweimer@redhat.com> - 1:1.8.0.141-4.b16
- Rebuild with binutils fix for ppc64le (#1475636)

* Wed Jul 26 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.141-3.b16
- added patch208, aarch64BuildFailure.patch to fix condition found during jdk9 build

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.8.0.141-2.b16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 21 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.141-1.b16
- updated to security u141.b16
- sync patches with rhel7
- removed no longer defined jvmjardir

* Sat Jun 17 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.131-7.b12
- adapted to no longer noarch openjfx-devel

* Wed Jun 07 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.131-6.b12
- added virtualprovides for javafx

* Wed Jun 07 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.131-5.b12
- fixed target of to fxrt.jar link
- fixedname of libglass

* Tue Jun 06 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.131-3.b12
- source999 moved to source1
- added two pathces 8181055-pr3394-rh1448880.patch and 8175813/PR3394/RH1448880
- enabled (commented out) system NSS via patch1000, rh1648249-add_commented_out_nss_cfg_provider_to_java_security.patch

* Tue May 09 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.131-1.b12
- added javafx binding subpackages

* Thu Apr 20 2017 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.131-1.b12
- updated to aarch64-jdk8u131-b12 (from aarch64-port/jdk8u)
- updated to aarch64-shenandoah-jdk8u131-b12-shenandoah-merge-2017-04-20 (from aarch64-port/jdk8u-shenandoah) of hotspot
- used aarch64-port-jdk8u-aarch64-jdk8u131-b12.tar.xz as new sources
- used aarch64-port-jdk8u-shenandoah-aarch64-shenandoah-jdk8u131-b12-shenandoah-merge-2017-04-20.tar.xz as new sources for hotspot

* Sun Mar 19 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-12.b14
- minor tweaks, egrep replaced by grep -E, added provides for some subpackages

* Mon Mar 13 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-11.b14
- sync from rhel, reordered patches, enabled shenanoah on aarch64
- Patch OpenJDK to check the system cacerts database directly
- Remove unneeded symlink to the system cacerts database
- Drop outdated openssl dependency from when the RPM built the cacerts database
- udpated to latest stable shenandoah hotspot

* Mon Mar 13 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-10.b14
- rhbz#1423751 - removed -fno-split-loops worakround as building against newer GCC7

* Tue Feb 28 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-9.b14
- updated to latest stable shenandoah hotspot
- updated to properly tagged upstream forest (no update, just rename)
- fixed update package to verify PR2126 patch and work with sha512

* Tue Feb 28 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-8.b14
- rebuild because of NSS

* Tue Feb 21 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-7.b14
- fixed the config(noreplace) issue with various left files lke java.security (rhbz#1183793)
- by calling new c-j-c hooks
- removed self-tail-bitting check check_sum_presented_in_spec
- release 6+7 to verify update path

* Mon Feb 20 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-5.b14
- patch 536 reordered to 537
- added patch 536 - Backport "8170888: [linux] Experimental support for cgroup memory limits in container (ie Docker) environments"
- added patch 538 - 1423421: Javadoc crashes when method name ends with "Property"
- rhbz#1423751 - added -fno-split-loops worakround sigsew when building with GCC7 (probably bug in jdk's JIT )

* Fri Feb 17 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-4.b14
- added Patch535 and 526
- tweeked debugsymbols check for sigill

* Wed Jan 25 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-2.b14
- revertrd patch535, excludeECDHE-1415137.patch and related changes
- issue casued by nss, see rhbz#1415137 c#35

* Tue Jan 24 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-2.b14
- added patch535, excludeECDHE-1415137.patch to tmp-worakround crash with nss

* Tue Jan 24 2017 jvanek <jvanek@redhat.com> - 1:1.8.0.121-1.b14
- updated to aarch64-jdk8u121-b14 (from openjdk8-forests/latest-aarch64)
- updated to aarch64-shenandoah-jdk8u121-b14 (from openjdk8-forests/latest-shenandoah) of hotspot
- used openjdk8-forests-latest-aarch64-aarch64-jdk8u121-b14.tar.xz as new sources
- used openjdk8-forests-latest-shenandoah-aarch64-shenandoah-jdk8u121-b14.tar.xz as new sources for hotspot
- deleted:    8044762-pr2960.patch 8049226-pr2960.patch 8154210.patch 8158260-pr2991-rh1341258.patch 8159244-pr3074.patch
- adapted java-1.8.0-openjdk-size_t.patch pr1834-rh1022017-reduce_ellipticcurvesextension_to_provide_only_three_nss_supported_nist_curves_23_24_25.patch rh1163501-increase_2048_bit_dh_upper_bound_fedora_infrastructure_in_dhparametergenerator.patch
- updated from internal (rhel) repo  OPENJDK_URL_DEFAULT=ssh://t...redhat.com//...ty/
- with custom PR2126=/.../pr2126.patch (removed newly added brainpool curves)
- withspecial values of PROJECT_NAME="openjdk8-forests", REPO_NAME="latest-aarch64"
- with correct tag VERSION="aarch64-jdk8u121-b14"
- and for shenandoah hotspot used custom repo REPO_NAME=latest-shenandoah
- with correct tag VERSION="aarch64-shenandoah-jdk8u121-b14"
- complete changes to  generate_source_tarball.sh  update_package.sh NOT commited (willbe regenerated from official repos soon)

* Mon Jan 09 2017 jvanek <jvanek@redhat.com - 1:1.8.0.111-5.b16
- Added arched dependencies to headless/main package

* Thu Nov 03 2016 jvanek <jvanek@redhat.com - 1:1.8.0.111-3.b16
- added patch207 - PR3183.patch
- java SSL/TLS implementation: should follow the policies of system-wide crypto policy 

* Fri Oct 21 2016 Omair Majid <omajid@redhat.com> - 1:1.8.0.111-2.b16
- added dont-add-unnecessary-debug-links.patch
- added hotspot-assembler-debuginfo.patch
- returned accidentally removed  hotspot-remove-debuglink.patch
- eu-readelfs on libraries improved, added gdb call

* Wed Oct 19 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.111-1.b16
- updated to aarch64-jdk8u111-b16 (from aarch64-port/jdk8u)
- updated to aarch64-shenandoah-jdk8u111-b16 (from aarch64-port/jdk8u-shenandoah) of hotspot
- used aarch64-port-jdk8u-aarch64-jdk8u111-b16.tar.xz as new sources
- used aarch64-port-jdk8u-shenandoah-aarch64-shenandoah-jdk8u111-b16.tar.xz as new sources for hotspot
- adapted patches

* Wed Oct 5 2016  Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.102-3.b14
- debug subpackages allowed on aarch64 and ppc64le
- fontconfig and nss restricted by isa

* Wed Aug 31 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.102-2.b14
- declared check_sum_presented_in_spec and used in prep and check
- it is checking that latest packed java.security is mentioned in listing
- @prefix@ in tapsetfiles substitued by prefix as necessary to work with systemtap3 (rhbz1371005)

* Thu Aug 25 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.102-1.b14
- updated to aarch64-jdk8u102-b14 (from aarch64-port/jdk8u)
- updated to aarch64-shenandoah-jdk8u102-b14 (from aarch64-port/jdk8u-shenandoah) of hotspot
- used aarch64-port-jdk8u-aarch64-jdk8u102-b14.tar.xz as new sources
- used aarch64-port-jdk8u-shenandoah-aarch64-shenandoah-jdk8u102-b14.tar.xz as new sources for hotspot
- removed upstreamed patches 519, 520 and 605
- updated to systemtap 3, removed related patches 300 and 301
- jjs provides moved to headless

* Mon Aug 01 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.101-3.b14
- Replace patch for S8162384 with upstream version. Document correctly along with SystemTap RH1204159 patch.
- Resolves: rhbz#1358661
- Replace patch for S8157306 with upstream version, documented & applied on all archs with conditional in patch
- Resolves: rhbz#1360863

* Mon Jul 25 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.101-2.b14
- added patch532 hotspot-1358661.patch - to fix performance of bimorphic inlining may be bypassed by type speculation
- added patch301 bz1204159_java8.patch - to fix systemtap on multiple jdks

* Mon Jul 25 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.101-1.b14
- updated to aarch64-jdk8u101-b14 (from aarch64-port/jdk8u)
- updated to aarch64-shenandoah-jdk8u101-b14-shenandoah-merge-2016-07-25 (from aarch64-port/jdk8u-shenandoah) of hotspot
- used aarch64-port-jdk8u-aarch64-jdk8u101-b14.tar.xz as new sources
- used aarch64-port-jdk8u-shenandoah-aarch64-shenandoah-jdk8u101-b14-shenandoah-merge-2016-07-25.tar.xz as new sources for hotspot
- priority lowered for ine zero digit, tip moved to 999
- added jdk6260348-pr3066-gtk_laf_jtextcomponent_not_respecting_desktop_caret_blink_rate.patch, pr3083-rh1346460-for_ssl_debug_return_null_instead_of_exception_when_theres_no_ecc_provider.patch, 8159244-pr3074.patch, corba_typo_fix.patch
renamed: jdk8-archivedJavadoc.patch -> jdk8154313-generated_javadoc_scattered_all_over_the_place.patch, pr2991-rh1341258.patch -> 8158260-pr2991-rh1341258.patch
- not added 8147771-additional_hunk.patch, already in b14

* Tue Jul 12 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.92-5.b14
- added Provides: /usr/bin/jjs

* Tue Jun 21 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.92-2.b14
- family restricted by arch

* Tue Jun 07 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.92-1.b14
- updated to u92
- removed upstreamed patches 8132051-aarch64.patch, 8143855.patch, criticalShenandoahFix.patch, rhbz1206656_fix_current_stack_pointer.patch
- 8132051-zero.patch, remove_aarch64_template_for_gcc6.patch
- jdwpCrash.abrt.patch renamed to 8044762-pr2960.patch
- httpsFix1329342.patch renamed to pr2934-sunec_provider_throwing_keyexception_withine.separator_current_nss_thus_initialise_the_random_number_generator_and_feed_the_seed_to_it.patch
- added known regresisonos fixes for u92 scheduled for next u (519-525)

* Thu May 19 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.91-7.b14
- added patch519, jdwpCrash.abrt.patch to fix trasnportation error

* Fri May 13 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.91-6.b14
- Enable weak reference discovery in ShenandoahMarkCompact. Otherwise we never process any weak references in full-gc. 

* Tue May 03 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.91-5.b14
- Restricted to depend on exactly same version of nss as used for build
- Resolves: rhbz#1332456

* Tue May 03 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.91-4.b14
- updated to aarch64-shenandoah-jdk8u71-b15-beta02 (from aarch64-port/jdk8u-shenandoah) of hotspot
- used aarch64-port-jdk8u-shenandoah-aarch64-shenandoah-jdk8u71-b15-beta02.tar.xz as new sources for hotspot
- reverted  nss version fix

* Mon Apr 25 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.91-4.b14
- Restricted to depend on exactly same version of nss as use dfor build
- Resolves: rhbz#1332456

* Mon Apr 25 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.91-3.b14
- included shenandoah support in 64b intel

* Sun Apr 24 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.91-2.b14
- added patch518 httpsFix1329342.patch
- test based on SOURCE14 enabled
- Resolves: rhbz#1329342

* Tue Apr 12 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Roll back release number as release 1 never succeeded, even with tests disabled.
- Resolves: rhbz#1325423

* Tue Apr 12 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Add additional fix to Zero patch to properly handle result on 64-bit big-endian
- Revert debugging options (aarch64 back to JIT, product build, no -Wno-error)
- Enable full bootstrap on all architectures to check we are good to go.
- Resolves: rhbz#1325423

* Tue Apr 12 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Turn tests back on or build will not fail.
- Resolves: rhbz#1325423

* Tue Apr 12 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Temporarily remove power64 from JIT arches to see if endian issue appears on Zero.
- Resolves: rhbz#1325423

* Tue Apr 12 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Turn off Java-based checks in a vain attempt to get a complete build.
- Resolves: rhbz#1325423

* Tue Apr 12 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Turn off -Werror so s390 can build in slowdebug mode.
- Add fix for formatting issue found by previous s390 build.
- Resolves: rhbz#1325423

* Tue Apr 12 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Revert settings to production defaults so we can at least get a build.
- Switch to a slowdebug build to try and unearth remaining issue on s390x.
- Resolves: rhbz#1325423

* Mon Apr 11 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Disable ECDSA test for now until failure on RHEL 7 is fixed.
- Resolves: rhbz#1325423

* Mon Apr 11 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Add 8132051 port to Zero.
- Turn on bootstrap build for all to ensure we are now good to go.
- Resolves: rhbz#1325423

* Mon Apr 11 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Add 8132051 port to AArch64.
- Resolves: rhbz#1325423

* Mon Apr 11 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Enable a full bootstrap on JIT archs. Full build held back by Zero archs anyway.
- Resolves: rhbz#1325423

* Sun Apr 10 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Use basename of test file to avoid misinterpretation of full path as a package
- Resolves: rhbz#1325423

* Sun Apr 10 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.91-1.b14
- Update to u91b14.
- Resolves: rhbz#1325423

* Mon Apr 04 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.77-2.b03
- added patch400  jdk8-archivedJavadoc.patch
- added javadoc-zip(-debug) subpackage with compressed javadoc

* Thu Mar 31 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.77-3.b03
- Fix typo in test invocation.
- Resolves: rhbz#1245810

* Thu Mar 31 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.77-3.b03
- Add ECDSA test to ensure ECC is working.
- Resolves: rhbz#1245810

* Wed Mar 30 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.77-2.b03
- Avoid WithSeed versions of NSS functions as they do not fully process the seed
- List current java.security md5sum so that java.security is replaced and ECC gets enabled.
- Resolves: rhbz#1245810

* Wed Mar 23 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.77-1.b03
- Update to u77b03.

* Thu Mar 03 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.72-13.b16
- When using a compositing WM, the overlay window should be used, not the root window.

* Mon Feb 29 2016 Omair Majid <omajid@redhat.com> - 1:1.8.0.72-12.b15
- Use a simple backport for PR2462/8074839.
- Don't backport the crc check for pack.gz. It's not tested well upstream.

* Mon Feb 29 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.72-5.b16
- Fix regression introduced on s390 by large code cache change.
- Update to u72b16.
- Drop 8147805 and jvm.cfg fix which are applied upstream.

* Wed Feb 24 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.72-11.b15
- Add patches to allow the SunEC provider to be built with the system NSS install.
- Re-generate source tarball so it includes ecc_impl.h.
- Adjust tarball generation script to allow ecc_impl.h to be included.
- Bring over NSS changes from java-1.7.0-openjdk spec file (NSS_CFLAGS/NSS_LIBS)
- Remove patch which disables the SunEC provider as it is now usable.
- Correct spelling mistakes in tarball generation script.
- Move completely unrelated AArch64 gcc 6 patch into separate file.
- Resolves: rhbz#1019554 (fedora bug)

* Tue Feb 23 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.72-10.b15
- returning accidentlay removed hunk from renamed and so wrongly merged remove_aarch64_jvm.cfg_divergence.patch

* Mon Feb 22 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.72-9.b15
- sync from rhel

* Tue Feb 16 2016 Dan Horák <dan[at]danny.cz> - 1:1.8.0.72-8.b15
- Refresh s390-java-opts patch

* Tue Feb 16 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.72-7.b15
- Use -fno-lifetime-dse over -fno-guess-branch-probability.
  See RHBZ#1306558.

* Mon Feb 15 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.72-6.b15
- Add aarch64_FTBFS_rhbz_1307224.patch so as to resolve RHBZ#1307224.

* Fri Feb 12 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.72-5.b15
- Add -fno-delete-null-pointer-checks -fno-guess-branch-probability flags to resolve x86/x86_64 crash.

* Mon Feb 08 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.72-5.b15
- Explicitly set the C++ standard to use, as the default has changed to C++ 2014 in GCC 6.
- Turn off -Werror due to format warnings in HotSpot and -std usage warnings in SCTP.
- Run tests under the check stage and use the debug build first.

* Fri Feb 05 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.71-4.b15
- Backport S8148351: Only display resolved symlink for compiler, do not change path

* Wed Feb 03 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.72-3.b15
* touch -t 201401010000 java.security to try to worakround md5sums

* Wed Jan 27 2016 jvanek <jvanek@redhat.com> - 1:1.8.0.72-1.b15
- updated to aarch64-jdk8u72-b15 (from aarch64-port/jdk8u)
- used aarch64-port-jdk8u-aarch64-jdk8u72-b15.tar.xz as new sources
- removed already upstreamed patch501 8146566.patch

* Wed Jan 20 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.71-1.b15
- sync with rhel7
- security update to CPU 19.1.2016 to u71b15

* Tue Dec 15 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-14.b17
- pretrans moved back to lua nd now includes file from copy-jdk-configs instead of call it

* Tue Dec 15 2015 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.65-13.b17
- Disable hardened build on non-JIT arches.
  Workaround for RHBZ#1290936.

* Thu Dec 10 2015 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.65-12.b17
-removed patch4 java-1.8.0-openjdk-PStack-808293.patch
-removed patch13 libjpeg-turbo-1.4-compat.patch

* Thu Dec 10 2015 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.65-11.b17
- Define our own optimisation flags based on the optflags macro and pass to OpenJDK build cflags/cxxflags.
- Remove -fno-devirtualize as we are now on GCC 5 where the GCC bug it worked around is fixed.
- Pass __global_ldflags to --with-extra-ldflags so Fedora linker flags are used in the build.
- Also Pass ourcppflags to the OpenJDK build cflags as it wrongly uses them for the HotSpot C++ build.
- Add PR2428, PR2462 & S8143855 patches to fix build issues that arise.
- Resolves: rhbz#1283949
- Resolves: rhbz#1120792

* Thu Dec 10 2015 Andrew Hughes <gnu.andrew@redhat.com> - 1:1.8.0.65-10.b17
- Add patch to honour %%{_smp_ncpus_max} from Tuomo Soini
- Resolves: rhbz#1152896

* Wed Dec 09 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-9.b17
- extracted lua scripts moved from pre where they don't work to pretrans
- requirement on copy-jdk-configs made Week.

* Tue Dec 08 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-8.b17
- used extracted lua scripts.
- now depnding on copy-jdk-configs
- config files persisting in pre instead of %%pretrans

* Tue Dec 08 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-7.b17
- changed way of generating the sources. As result:
- "updated" to aarch64-jdk8u65-b17 (from aarch64-port/jdk8u60)
- used aarch64-port-jdk8u60-aarch64-jdk8u65-b17.tar.xz as new sources

* Fri Nov 27 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-5.b17
- added missing md5sums
- moved to bundeld lcms

* Wed Nov 25 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-4.b17
- debug packages priority lowered by 1

* Wed Nov 25 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-3.b17
- depends on chkconfig >1.7 - added --family support

* Fri Nov 13 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-2.b17
- added and applied patch605 soundFontPatch.patch as repalcement for removed sound font links
- removed hardcoded soundfont links

* Thu Nov 12 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.65-1.b17
- updated to u65b17

* Mon Nov 09 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-17.b28
- policytool  manpage followed the binary from devel to jre

* Mon Nov 02 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-16.b28
added and applied patch604: aarch64-ifdefbugfix.patch to fix rhbz1276959

* Thu Oct 15 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-15.b28
- moved to single source integration forest
- removed patch patch9999 enableArm64.patch
- removed patch patch600  %%{name}-rh1191652-hotspot.patch

* Thu Aug 27 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-14.b24
- updated aarch64 tarball to contain whole forest of latest jdk8-aarch64-jdk8u60-b24.2.tar.xz
- using this forest instead of only hotspot
- generate_source_tarball.sh - temporarily excluded repos="hotspot" compression of download
- not only openjdk/hotspot is replaced, by wholeopenjdk
- ln -s openjdk jdk8 done after replacing of openjdk
- patches 9999 601 and 602 exclded for aarch64

* Wed Aug 26 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-13.b24
- updated aarch64 hotpost to latest jdk8-aarch64-jdk8u60-b24.2.tar.xz

* Wed Aug 19 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-12.b24
- updated to freshly released jdk8u60-jdk8u60-b27

* Thu Aug 13 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-11.b24
- another touching attempt to polycies...

* Mon Aug 03 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-10.b24
- arch64 updated to u60-b24 with hope to fix rhbz1249037

* Fri Jul 17 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-3.b24
- added one more md5sum test (thanx to Severin!)
 - I guess one more missing
- doubled slash in md5sum test in post

* Thu Jul 16 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-2.b24
- updated to security u60-b24
- moved to openjdk instead of jdk8 topdir in sources
- removed upstreamed patch99 java-1.8.0-openjdk-linux-4.x.patch
- removed upstreamed patch503 pr2444.patch
- removed upstreamed patch505 1208369_memory_leak_gcc5.patch
- removed upstreamed patch506: gif4.1.patch
 - note: usptream version is suspicious
  GIFLIB_MAJOR >= 5 SplashStreamGifInputFunc, NULL
  ELSE SplashStreamGifInputFunc
 - but the condition seems to be viceversa


* Mon Jun 22 2015 Omair Majid <omajid@redhat.com> - 1:1.8.0.60-7.b16
- Require javapackages-tools instead of jpackage-utils.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.0.60-6.b16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun 09 2015 Dan Horák <dan[at]danny.cz> - 1:1.8.0.60-5.b16
- allow build on Linux 4.x kernel
- refresh s390 size_t patch

* Fri Jun 05 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-4.b16
- added requires lksctp-tools for headless subpackage to make sun.nio.ch.sctp work

* Mon May 25 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-2.b16
- Patch503 d318d83c4e74.patch, patch505 1208369_memory_leak_gcc5.patch (and patch506 gif4.1.patch)
   moved out of "if with_systemtap" block

* Mon May 25 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.60-1.b16
- updated to u60b16
- deleted upstreamed patches:
   patch501 1182011_JavaPrintApiDoesNotPrintUmlautCharsWithPostscriptOutputCorrectly.patch
   patch502 1182694_javaApplicationMenuMisbehave.patch
   patch504 1210739_dns_naming_ipv6_addresses.patch
   patch402 atomic_linux_zero.inline.hpp.patch
   patch401 fix_ZERO_ARCHDEF_ppc.patch
   patch400 ppc_stack_overflow_fix.patch
   patch204 zero-interpreter-fix.patch
- added Patch506 gif4.1.patch to allow build agaisnt giflib > 4.1

* Wed May 13 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.45-38.b14
- updated to 8u45-b14 with hope to fix rhbz#1123870

* Wed May 13 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.45-37.b13
- added runtime requires for tzdata
- Remove reference to tz.properties which is no longer used (by gnu.andrew)

* Wed Apr 29 2015 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.45-36.b13
- Patch hotspot to not use undefined code rather than passing
  -fno-tree-vrp via CFLAGS.
  Resolves: RHBZ#1208369
- Add upstream patch for DNS nameserver issue with IPv6 addresses.
  Resolves: RHBZ#1210739

* Wed Apr 29 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.45-35.b13
- Omit jsa files from power64 file list as well, as they are never generated
- moved to boot build by openjdk8
- Use the template interpreter on ppc64le

* Fri Apr 10 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.45-31.b13
- repacked sources

* Tue Apr 07 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.45-30.b13
- updated to security u45
- removed patch6: disable-doclint-by-default.patch
- added patch d318d83c4e74.patch
- added  rhbz1206656_fix_current_stack_pointer.patch
- renamed PStack-808293.patch -> java-1.8.0-openjdk-PStack-808293.patch
- renamed remove-intree-libraries.sh -> java-1.8.0-openjdk-remove-intree-libraries.sh
- renamed to preven conflix with jdk7

* Fri Apr 03 2015 Omair Majid <omajid@redhat.com> - 1:1.8.0.40-27.b25
- Add -fno-tree-vrp to flags to prevent hotspot miscompilation.
- Resolves: RHBZ#1208369

* Thu Apr 02 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-27.b25
- bumped release. Needed rebuild by itself on arm

* Tue Mar 31 2015 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.40-26.b25
- Make Zero build-able on ARM32.
  Resolves: RHBZ#1206656

* Fri Mar 27 2015 Dan Horák <dan[at]danny.cz> - 1:1.8.0.40-25.b25
- refresh s390 patches

* Fri Mar 27 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-24.b25
- added patch501 1182011_JavaPrintApiDoesNotPrintUmlautCharsWithPostscriptOutputCorrectly.patch
- added patch502 1182694_javaApplicationMenuMisbehave.patch
- both upstreamed, will be gone with u60

* Wed Mar 25 2015 Omair Majid <omajid@redhat.com> - 1:1.8.0.40-23.b25
- Disable various EC algorithms in configuration

* Mon Mar 23 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-22.b25
- sytemtap made working for dual package

* Tue Mar 03 2015 Severin Gehwolf <sgehwolf@redhat.com> - 1:1.8.0.40-21.b25
- Added compiler no-warn-

* Fri Feb 20 2015 Omair Majid <omajid@redhat.com> - 1:1.8.0.40-21.b25
- Fix zero interpreter build.

* Thu Feb 12 2015 Omair Majid <omajid@redhat.com> - 1:1.8.0.40-21.b25
- Fix building with gcc 5 by ignoring return-local-addr warning
- Include additional debugging info for java class files and test that they are
  present

* Thu Feb 12 2015 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-20.b25
- bumped to b25
- removed upstreamed patch11 hotspot-build-j-directive.patch
- policies repacked to stop spamming yum update
- added and used source20 repackReproduciblePolycies.sh
- added mehanism to force priority size

* Fri Jan 09 2015 Dan Horák <dan[at]danny.cz> - 1:1.8.0.40-19.b12
- refresh s390 patches

* Fri Nov 07 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-18.b12
- updated arm64 tarball to jdk8-jdk8u40-b12-aarch64-1263.tar.xz

* Fri Nov 07 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-17.b12
- obsoleted gcj and sindoc. rh1149674 and rh1149675
- removed backup/restore on images and docs in favor of reconfigure in different directory

* Mon Nov 03 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-16.b12
- updated both noral and aarch64 tarballs to u40b12

* Mon Nov 03 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-15.b02
- enabled debug packages
- removed all provides duplicating package name
- comments about files moved inside files section (to prevent different javadoc postuns)
 - see (RH1160693)

* Fri Oct 31 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.40-13.b02
- Build against libjpeg-turbo-1.4

* Fri Oct 24 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-13.b02
- preparing for parallel debug+normal build
- files and scripelts moved to extendable macros as first step to dual build
- install and build may be done in loop for both release and slowdebug
- debugbuild off untill its completed

* Fri Oct 24 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-12.b02
- added patch12,removeSunEcProvider-RH1154143
- xdump excluded from ppc64le (rh1156151)
- Add check for src.zip completeness. See RH1130490 (by sgehwolf@redhat.com)
- Resolves: rhbz#1125260

* Thu Sep 25 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-11.b02
- fixing flags usages (thanx to jerboaa!)

* Thu Sep 25 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.20-10.b26
- sync with rhel7

* Wed Sep 17 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.20-9.b26
- Remove LIBDIR and funny definition of _libdir.
- Fix rpmlint warnings about macros in comments.

* Thu Sep 11 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.20-8.b26
- fixed headless to become headless again
 - jre/bin/policytool added to not headless exclude list

* Wed Sep 10 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.20-7.b26
- Update aarch64 hotspot to latest upstream version

* Fri Sep 05 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.40-6.b26
- Use %%{power64} instead of %%{ppc64}.

* Thu Sep 04 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-5.b26
- Update aarch64 hotspot to jdk7u40-b02 to match the rest of the JDK
- commented out patch2 (obsolated by 666)
- all ppc64 added to jitarches

* Thu Sep 04 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.20-4.b26
- Use the cpp interpreter on ppc64le.

* Wed Sep 03 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.20-3.b26
- fixed RH1136544, orriginal issue, state of pc64le jit remians mistery

* Wed Aug 27 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.20-2.b26
- requirement Requires: javazi-1.8/tzdb.dat changed to tzdata-java >= 2014f-1
- see RH1130800#c5

* Wed Aug 27 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-1.b02
- adapted aarch64 patch
- removed upstreamed patch  0001-PPC64LE-arch-support-in-openjdk-1.8.patch

* Wed Aug 27 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-1.b02
- updated to u40-b02
- adapted aarch64 patches

* Wed Aug 27 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.40-1.b01
- updated to u40-b01
- adapted  rh1648242-accessible_toolkit_crash_do_not_break_jvm.patch
- adapted  jdk8042159-allow_using_system_installed_lcms2.patch
- removed patch8 set-active-window.patch
- removed patch9 javadoc-error-jdk-8029145.patch
- removed patch10 javadoc-error-jdk-8037484.patch
- removed patch99 applet-hole.patch - itw 1.5.1 is able to ive without it

* Tue Aug 19 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-19.b12
- fixed desktop icons
- Icon set to java-1.8.0
- Development removed from policy tool

* Mon Aug 18 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-18.b12
- fixed jstack

* Mon Aug 18 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-17.b12
- added build requires and requires for headles  _datadir/javazi-1.8/tzdb.dat
- restriction of tzdata provider, so we will be aware of another possible failure

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Aug 14 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-15.b12
- fixed provides/obsolates

* Tue Aug 12 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-14.b12
- forced to build in fully versioned dir

* Tue Aug 12 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-13.b12
- fixing tapset to support multipleinstalls
- added more config/norepalce
- policitool moved to jre

* Tue Aug 12 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-12.b12
- bumped release to build by previous release.
- forcing rebuild by jdk8
- uncommenting forgotten comment on tzdb link

* Tue Aug 12 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-11.b12
- backporting old fixes:
- get rid of jre-abrt, uniquesuffix, parallel install, jsa files,
  config(norepalce) bug, -fstack-protector-strong, OrderWithRequires,
  nss config, multilib arches, provides/requires excludes
- some additional cosmetic changes

* Tue Jul 22 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.11-8.b12
- Modify aarch64-specific jvm.cfg to list server vm first

* Mon Jul 21 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-7.b12
- removed legacy aarch64 switches
 - --with-jvm-variants=client and  --disable-precompiled-headers

* Tue Jul 15 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-6.b12
- added patch patch9999 enableArm64.patch to enable new hotspot

* Tue Jul 15 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-5.b12
- Attempt to update aarch64 *jdk* to u11b12, by resticting aarch64 sources to hotpot only

* Tue Jul 15 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.11-1.b12
- updated to security u11b12

* Tue Jun 24 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-13.b13
- Obsolete java-1.7.0-openjdk

* Wed Jun 18 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-12.b13
- Use system tzdata from tzdata-java

* Thu Jun 12 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-11.b13
- Add patch from IcedTea to handle -j and -I correctly

* Wed Jun 11 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-11.b13
- Backport javadoc fixes from upstream
- Related: rhbz#1107273

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.0.5-10.b13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Jun 02 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-9.b13
- Build with OpenJDK 8

* Wed May 28 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-8.b13
- Backport fix for JDK-8012224

* Wed May 28 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-7.b13
- Require fontconfig and minimal fonts (xorg-x11-fonts-Type1) explicitly
- Resolves rhbz#1101394

* Fri May 23 2014 Dan Horák <dan[at]danny.cz> - 1:1.8.0.5-6.b13
- Enable build on s390/s390x

* Tue May 20 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-5.b13
- Only check for debug symbols in libjvm if it exists.

* Fri May 16 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-4.b13
- Include all sources in src.zip

* Mon Apr 28 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-4.b13
- Check for debug symbols in libjvm.so

* Thu Apr 24 2014 Brent Baude <baude@us.ibm.com> - 1:1.8.0.5-3.b13
- Add ppc64le support, bz# 1088344

* Wed Apr 23 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-2.b13
- Build with -fno-devirtualize
- Don't strip debuginfo from files

* Wed Apr 16 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-1.b13
- Instrument build with various sanitizers.

* Tue Apr 15 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.5-1.b13
- Update to the latest security release: OpenJDK8 u5 b13

* Fri Mar 28 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-2.b132
- Include version information in desktop files
- Move desktop files from tarball to top level source

* Tue Mar 25 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-1.0.b132
- Switch from java8- style provides to java- style
- Bump priority to reflect java version

* Fri Mar 21 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.35.b132
- Disable doclint for compatiblity
- Patch contributed by Andrew John Hughes

* Tue Mar 11 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.34.b132
- Include jdeps and jjs for aarch64. These are present in b128.

* Mon Mar 10 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.33.b132
- Update aarch64 tarball to the latest upstream release

* Fri Mar 07 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.32.b132
- Fix `java -version` output

* Fri Mar 07 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.31.b132
- updated to rc4 aarch64 tarball
- outdated removed: patch2031 system-lcmsAARCH64.patch patch2011 system-libjpeg-aarch64.patch
  patch2021 system-libpng-aarch64.patch

* Thu Mar 06 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.30.b132
- Update to b132

* Thu Mar 06 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.29.b129
- Fix typo in STRIP_POLICY

* Mon Mar 03 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.28.b129
- Remove redundant debuginfo files
- Generate complete debug information for libjvm

* Tue Feb 25 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.27.b129
- Fix non-headless libraries

* Tue Feb 25 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.26.b129
- Fix incorrect Requires

* Thu Feb 13 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.26.b129
- Add -headless subpackage based on java-1.7.0-openjdk
- Add abrt connector support
- Add -accessibility subpackage

* Thu Feb 13 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.26.b129
- Update to b129.

* Fri Feb 07 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.25.b126
- Update to candidate Reference Implementation release.

* Fri Jan 31 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.24.b123
- Forward port more patches from java-1.7.0-openjdk

* Mon Jan 20 2014 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.23.b123
- Update to jdk8-b123

* Thu Nov 14 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.22.b115
- Update to jdk8-b115

* Wed Oct 30 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.21.b106
- added jre/lib/security/blacklisted.certs for aarch64
- updated to preview_rc2 aarch64 tarball

* Sun Oct 06 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.20.b106
- Fix paths in tapsets to work on non-x86_64
- Use system libjpeg

* Thu Sep 05 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.19.b106
- Fix with_systemtap conditionals

* Thu Sep 05 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.18.b106
- Update to jdk8-b106

* Tue Aug 13 2013 Deepak Bhole <dbhole@redhat.com> - 1:1.8.0.0-0.17.b89x
- Updated aarch64 to latest head
- Dropped upstreamed patches

* Wed Aug 07 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.16.b89x
- The zero fix only applies on b89 tarball

* Tue Aug 06 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.16.b89x
- Add patch to fix zero on 32-bit build

* Mon Aug 05 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.16.b89x
- Added additional build fixes for aarch64

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.8.0.0-0.16.b89x
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Aug 02 2013 Deepak Bhole <dbhole@redhat.com> - 1:1.8.0.0-0.15.b89
- Added a missing includes patch (#302/%%{name}-arm64-missing-includes.patch)
- Added --disable-precompiled-headers for arm64 build

* Mon Jul 29 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.14.b89
- added patch 301 - removeMswitchesFromx11.patch

* Fri Jul 26 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.13.b89
- added new aarch64 tarball

* Thu Jul 25 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.12.b89
- ifarchaarch64 then --with-jvm-variants=client

* Tue Jul 23 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.11.b89
- prelink dependence excluded also for aaech64
- arm64 added to jitarches
- added source100 config.guess to repalce the outdated one in-tree
- added source101 config.sub  to repalce the outdated one in-tree
- added patch2011 system-libjpegAARCH64.patch (as aarch64-port is little bit diferent)
- added patch2031 system-lcmsAARCH64.patch (as aarch64-port is little bit diferent)
- added gcc-c++ build depndece so builddep will  result to better situation

* Tue Jul 23 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.10.b89
- moved to latest working osurces

* Tue Jul 23 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.10.b89
- Moved  to hg clone for generating sources.

* Sun Jul 21 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.0-0.9.b89
- added aarch 64 tarball, proposed usage of clone instead of tarballs

* Mon Jul 15 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.9.b89
- Switch to xz for compression
- Fixes RHBZ#979823

* Mon Jul 15 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.9.b89
- Priority should be 0 until openjdk8 is released by upstream
- Fixes RHBZ#964409

* Mon Jun 3 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.8.b89
- Fix incorrect permissions on ct.sym

* Mon May 20 2013 Omair Majid <omajid@redhat.com> - 1:1.8.0.0-0.7.b89
- Fix incorrect permissions on jars

* Fri May 10 2013 Adam Williamson <awilliam@redhat.com>
- update scriptlets to follow current guidelines for updating icon cache

* Tue Apr 30 2013 Omair Majid <omajid@redhat.com> 1:1.8.0.0-0.5.b87
- Update to b87
- Remove all rhino support; use nashorn instead
- Remove upstreamed/unapplied patches

* Tue Apr 23 2013 Karsten Hopp <karsten@redhat.com> 1:1.8.0.0-0.4.b79
- update java-1.8.0-openjdk-ppc-zero-hotspot patch
- use power64 macro

* Thu Mar 28 2013 Omair Majid <omajid@redhat.com> 1:1.8.0.0-0.3.b79
- Add build fix for zero
- Drop gstabs fixes; enable full debug info instead

* Wed Mar 13 2013 Omair Majid <omajid@redhat.com> 1:1.8.0.0-0.2.b79
- Fix alternatives priority

* Tue Mar 12 2013 Omair Majid <omajid@redhat.com> 1:1.8.0.0-0.1.b79.f19
- Update to jdk8-b79
- Initial version for Fedora 19

* Tue Sep 04 2012 Andrew John Hughes <gnu.andrew@redhat.com> - 1:1.8.0.0-b53.1
- Initial build from java-1.7.0-openjdk RPM