%define contentdir %{_datadir}/httpd
%define docroot /var/www
%define suexec_caller apache
%define mmn 20120211
%define mmnisa %{mmn}%{__isa_name}%{__isa_bits}
%define vstring %(source /etc/os-release; echo ${REDHAT_SUPPORT_PRODUCT})
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
%global mpm event
%else
%global mpm prefork
%endif

Summary: Apache HTTP Server
Name: httpd
Version: 2.4.37
Release: 21%{?dist}
URL: https://httpd.apache.org/
Source0: https://www.apache.org/dist/httpd/httpd-%{version}.tar.bz2
Source1: centos-noindex-8.0.tar.gz
Source2: httpd.logrotate
Source3: instance.conf
Source4: httpd-ssl-pass-dialog
Source5: httpd.tmpfiles
Source6: httpd.service
Source7: action-graceful.sh
Source8: action-configtest.sh
Source10: httpd.conf
Source11: 00-base.conf
Source12: 00-mpm.conf
Source13: 00-lua.conf
Source14: 01-cgi.conf
Source15: 00-dav.conf
Source16: 00-proxy.conf
Source17: 00-ssl.conf
Source18: 01-ldap.conf
Source19: 00-proxyhtml.conf
Source20: userdir.conf
Source21: ssl.conf
Source22: welcome.conf
Source23: manual.conf
Source24: 00-systemd.conf
Source25: 01-session.conf
Source26: 10-listen443.conf
Source27: httpd.socket
Source28: 00-optional.conf
# Documentation
Source30: README.confd
Source31: README.confmod
Source32: httpd.service.xml
Source33: htcacheclean.service.xml
Source34: httpd.conf.xml
Source40: htcacheclean.service
Source41: htcacheclean.sysconf
Source42: httpd-init.service
Source43: httpd-ssl-gencerts
Source44: httpd@.service
Source45: config.layout

# build/scripts patches
# http://bugzilla.redhat.com/show_bug.cgi?id=1231924
# http://bugzilla.redhat.com/show_bug.cgi?id=842736
# http://bugzilla.redhat.com/show_bug.cgi?id=1214401
Patch1: httpd-2.4.35-apachectl.patch
Patch2: httpd-2.4.28-apxs.patch
Patch3: httpd-2.4.35-deplibs.patch

# Needed for socket activation and mod_systemd patch
Patch19: httpd-2.4.35-detect-systemd.patch

# Features/functional changes
Patch20: httpd-2.4.32-export.patch
Patch21: httpd-2.4.35-corelimit.patch
Patch22: httpd-2.4.35-selinux.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1170215
Patch23: httpd-2.4.28-icons.patch
Patch24: httpd-2.4.35-systemd.patch
Patch25: httpd-2.4.35-cachehardmax.patch
Patch26: httpd-2.4.28-socket-activation.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1109119
Patch27: httpd-2.4.35-sslciphdefault.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1332242
Patch28: httpd-2.4.28-statements-comment.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=811714
Patch29: httpd-2.4.35-full-release.patch
Patch30: httpd-2.4.35-freebind.patch
Patch31: httpd-2.4.35-r1830819+.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1638738
Patch32: httpd-2.4.37-sslprotdefault.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1747898
Patch33: httpd-2.4.37-mod-md-mod-ssl-hooks.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1725031
Patch34: httpd-2.4.37-r1861793+.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1704317ě
Patch35: httpd-2.4.37-sslkeylogfile-support.patch

# Bug fixes
# https://bugzilla.redhat.com/show_bug.cgi?id=1397243
Patch61: httpd-2.4.35-r1738878.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1170206
Patch62: httpd-2.4.35-r1633085.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1448892
Patch63: httpd-2.4.28-r1811831.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1602548
Patch65: httpd-2.4.35-r1842888.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1653009
# https://bugzilla.redhat.com/show_bug.cgi?id=1672977
# https://bugzilla.redhat.com/show_bug.cgi?id=1673022
Patch66: httpd-2.4.37-r1842929+.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1630432
Patch67: httpd-2.4.35-r1825120.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1670716
Patch68: httpd-2.4.37-fips-segfault.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1669221
Patch70: httpd-2.4.37-r1840554.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1673022
Patch71: httpd-2.4.37-mod-md-perms.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1724549
Patch72: httpd-2.4.37-mod-mime-magic-strdup.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1724034
Patch73: httpd-2.4.35-ocsp-wrong-ctx.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1633224
Patch74: httpd-2.4.37-r1828172+.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1775158
Patch75: httpd-2.4.37-r1870095+.patch

# Security fixes
Patch200: httpd-2.4.37-r1851471.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1694980
Patch201: httpd-2.4.37-CVE-2019-0211.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1695025
Patch202: httpd-2.4.37-CVE-2019-0215.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1696141
Patch203: httpd-2.4.37-CVE-2019-0217.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1696097
Patch204: httpd-2.4.37-CVE-2019-0220.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1741860
# https://bugzilla.redhat.com/show_bug.cgi?id=1741864
# https://bugzilla.redhat.com/show_bug.cgi?id=1741868
Patch205: httpd-2.4.34-CVE-2019-9511-and-9516-and-9517.patch

License: ASL 2.0
Group: System Environment/Daemons
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: autoconf, perl-interpreter, perl-generators, pkgconfig, findutils, xmlto
BuildRequires: zlib-devel, libselinux-devel, lua-devel,  brotli-devel
BuildRequires: apr-devel >= 1.5.0, apr-util-devel >= 1.5.0, pcre-devel >= 5.0
BuildRequires: systemd-devel
Requires: /etc/mime.types, system-logos-httpd
Obsoletes: httpd-suexec
Provides: webserver
Provides: mod_dav = %{version}-%{release}, httpd-suexec = %{version}-%{release}
Provides: httpd-mmn = %{mmn}, httpd-mmn = %{mmnisa}
Requires: httpd-tools = %{version}-%{release}
Requires: httpd-filesystem = %{version}-%{release}
Requires: mod_http2
Requires(pre): httpd-filesystem
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires(post): systemd-units
Conflicts: apr < 1.5.0-1

%description
The Apache HTTP Server is a powerful, efficient, and extensible
web server.

%package devel
Group: Development/Libraries
Summary: Development interfaces for the Apache HTTP server
Requires: apr-devel, apr-util-devel, pkgconfig
Requires: httpd = %{version}-%{release}

%description devel
The httpd-devel package contains the APXS binary and other files
that you need to build Dynamic Shared Objects (DSOs) for the
Apache HTTP Server.

If you are installing the Apache HTTP server and you want to be
able to compile or develop additional modules for Apache, you need
to install this package.

%package manual
Group: Documentation
Summary: Documentation for the Apache HTTP server
Requires: httpd = %{version}-%{release}
Obsoletes: secureweb-manual, apache-manual
BuildArch: noarch

%description manual
The httpd-manual package contains the complete manual and
reference guide for the Apache HTTP server. The information can
also be found at http://httpd.apache.org/docs/2.2/.

%package filesystem
Group: System Environment/Daemons
Summary: The basic directory layout for the Apache HTTP server
BuildArch: noarch
Requires(pre): /usr/sbin/useradd

%description filesystem
The httpd-filesystem package contains the basic directory layout
for the Apache HTTP server including the correct permissions
for the directories.

%package tools
Group: System Environment/Daemons
Summary: Tools for use with the Apache HTTP Server

%description tools
The httpd-tools package contains tools which can be used with 
the Apache HTTP Server.

%package -n mod_ssl
Group: System Environment/Daemons
Summary: SSL/TLS module for the Apache HTTP Server
Epoch: 1
BuildRequires: openssl-devel
Requires(pre): httpd-filesystem
Requires: httpd = 0:%{version}-%{release}, httpd-mmn = %{mmnisa}
Requires: sscg >= 2.2.0
Obsoletes: stronghold-mod_ssl
# Require an OpenSSL which supports PROFILE=SYSTEM
Conflicts: openssl-libs < 1:1.0.1h-4

%description -n mod_ssl
The mod_ssl module provides strong cryptography for the Apache Web
server via the Secure Sockets Layer (SSL) and Transport Layer
Security (TLS) protocols.

%package -n mod_proxy_html
Group: System Environment/Daemons
Summary: HTML and XML content filters for the Apache HTTP Server
Requires: httpd = 0:%{version}-%{release}, httpd-mmn = %{mmnisa}
BuildRequires: libxml2-devel
Epoch: 1
Obsoletes: mod_proxy_html < 1:2.4.1-2

%description -n mod_proxy_html
The mod_proxy_html and mod_xml2enc modules provide filters which can
transform and modify HTML and XML content.

%package -n mod_ldap
Group: System Environment/Daemons
Summary: LDAP authentication modules for the Apache HTTP Server
Requires: httpd = 0:%{version}-%{release}, httpd-mmn = %{mmnisa}
Requires: apr-util-ldap

%description -n mod_ldap
The mod_ldap and mod_authnz_ldap modules add support for LDAP
authentication to the Apache HTTP Server.

%package -n mod_session
Group: System Environment/Daemons
Summary: Session interface for the Apache HTTP Server
Requires: httpd = 0:%{version}-%{release}, httpd-mmn = %{mmnisa}

%description -n mod_session
The mod_session module and associated backends provide an abstract
interface for storing and accessing per-user session data.

%prep
%setup -q
%patch1 -p1 -b .apctl
%patch2 -p1 -b .apxs
%patch3 -p1 -b .deplibs

%patch19 -p1 -b .detectsystemd
%patch20 -p1 -b .export
%patch21 -p1 -b .corelimit
%patch22 -p1 -b .selinux
%patch23 -p1 -b .icons
%patch24 -p1 -b .systemd
%patch25 -p1 -b .cachehardmax
%patch26 -p1 -b .socketactivation
%patch27 -p1 -b .sslciphdefault
%patch28 -p1 -b .statementscomment
%patch29 -p1 -b .fullrelease
%patch30 -p1 -b .freebind
%patch31 -p1 -b .r1830819+
%patch32 -p1 -b .sslprotdefault
%patch33 -p1 -b .mod-md-mod-ssl-hooks
%patch34 -p1 -b .r1861793+
%patch35 -p1 -b .sslkeylogfile-support

%patch61 -p1 -b .r1738878
%patch62 -p1 -b .r1633085
%patch63 -p1 -b .r1811831
%patch65 -p1 -b .r1842888
%patch66 -p1 -b .r1842929+
%patch67 -p1 -b .r1825120
%patch68 -p1 -b .fipscore
%patch70 -p1 -b .r1840554
%patch71 -p1 -b .modmdperms
%patch72 -p1 -b .mimemagic
%patch73 -p1 -b .ocspwrongctx
%patch74 -p1 -b .r1828172+
%patch75 -p1 -b .r1870095+

%patch200 -p1 -b .r1851471
%patch201 -p1 -b .CVE-2019-0211
%patch202 -p1 -b .CVE-2019-0215
%patch203 -p1 -b .CVE-2019-0217
%patch204 -p1 -b .CVE-2019-0220
%patch205 -p1 -b .CVE-2019-9511-and-9516-and-9517

# Patch in the vendor string
sed -i '/^#define PLATFORM/s/Unix/%{vstring}/' os/unix/os.h
sed -i 's/@RELEASE@/%{release}/' server/core.c

# Prevent use of setcap in "install-suexec-caps" target.
sed -i '/suexec/s,setcap ,echo Skipping setcap for ,' Makefile.in

# Example conf for instances
cp $RPM_SOURCE_DIR/instance.conf .
sed < $RPM_SOURCE_DIR/httpd.conf >> instance.conf '
0,/^ServerRoot/d;
/# Supplemental configuration/,$d
/^ *CustomLog .logs/s,logs/,logs/${HTTPD_INSTANCE}_,
/^ *ErrorLog .logs/s,logs/,logs/${HTTPD_INSTANCE}_,
'
touch -r $RPM_SOURCE_DIR/instance.conf instance.conf

# Safety check: prevent build if defined MMN does not equal upstream MMN.
vmmn=`echo MODULE_MAGIC_NUMBER_MAJOR | cpp -include include/ap_mmn.h | sed -n '/^2/p'`
if test "x${vmmn}" != "x%{mmn}"; then
   : Error: Upstream MMN is now ${vmmn}, packaged MMN is %{mmn}
   : Update the mmn macro and rebuild.
   exit 1
fi

# Provide default layout
cp $RPM_SOURCE_DIR/config.layout .

sed '
s,@MPM@,%{mpm},g
s,@DOCROOT@,%{docroot},g
s,@LOGDIR@,%{_localstatedir}/log/httpd,g
' < $RPM_SOURCE_DIR/httpd.conf.xml \
    > httpd.conf.xml

xmlto man ./httpd.conf.xml
xmlto man $RPM_SOURCE_DIR/htcacheclean.service.xml
xmlto man $RPM_SOURCE_DIR/httpd.service.xml

: Building with MMN %{mmn}, MMN-ISA %{mmnisa}
: Default MPM is %{mpm}, vendor string is '%{vstring}'

%build
# forcibly prevent use of bundled apr, apr-util, pcre
rm -rf srclib/{apr,apr-util,pcre}

# regenerate configure scripts
autoheader && autoconf || exit 1

# Before configure; fix location of build dir in generated apxs
%{__perl} -pi -e "s:\@exp_installbuilddir\@:%{_libdir}/httpd/build:g" \
        support/apxs.in

export CFLAGS=$RPM_OPT_FLAGS
export LDFLAGS="-Wl,-z,relro,-z,now"

# Hard-code path to links to avoid unnecessary builddep
export LYNX_PATH=/usr/bin/links

# Build the daemon
./configure \
        --prefix=%{_sysconfdir}/httpd \
        --exec-prefix=%{_prefix} \
        --bindir=%{_bindir} \
        --sbindir=%{_sbindir} \
        --mandir=%{_mandir} \
        --libdir=%{_libdir} \
        --sysconfdir=%{_sysconfdir}/httpd/conf \
        --includedir=%{_includedir}/httpd \
        --libexecdir=%{_libdir}/httpd/modules \
        --datadir=%{contentdir} \
        --enable-layout=Fedora \
        --with-installbuilddir=%{_libdir}/httpd/build \
        --enable-mpms-shared=all \
        --with-apr=%{_prefix} --with-apr-util=%{_prefix} \
        --enable-suexec --with-suexec \
        --enable-suexec-capabilities \
        --with-suexec-caller=%{suexec_caller} \
        --with-suexec-docroot=%{docroot} \
        --without-suexec-logfile \
        --with-suexec-syslog \
        --with-suexec-bin=%{_sbindir}/suexec \
        --with-suexec-uidmin=1000 --with-suexec-gidmin=1000 \
        --with-brotli \
        --enable-pie \
        --with-pcre \
        --enable-mods-shared=all \
        --enable-ssl --with-ssl --disable-distcache \
        --enable-proxy --enable-proxy-fdpass \
        --enable-cache \
        --enable-disk-cache \
        --enable-ldap --enable-authnz-ldap \
        --enable-cgid --enable-cgi \
        --enable-cgid-fdpassing \
        --enable-authn-anon --enable-authn-alias \
        --disable-imagemap --disable-file-cache \
        --disable-http2 \
        --disable-md \
        $*
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install

# Install systemd service files
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
for s in httpd.service htcacheclean.service httpd.socket \
         httpd@.service httpd-init.service; do
  install -p -m 644 $RPM_SOURCE_DIR/${s} \
                    $RPM_BUILD_ROOT%{_unitdir}/${s}
done

# install conf file/directory
mkdir $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d \
      $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.modules.d
install -m 644 $RPM_SOURCE_DIR/README.confd \
    $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/README
install -m 644 $RPM_SOURCE_DIR/README.confmod \
    $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.modules.d/README
for f in 00-base.conf 00-mpm.conf 00-lua.conf 01-cgi.conf 00-dav.conf \
         00-proxy.conf 00-ssl.conf 01-ldap.conf 00-proxyhtml.conf \
         01-ldap.conf 00-systemd.conf 01-session.conf 00-optional.conf; do
  install -m 644 -p $RPM_SOURCE_DIR/$f \
        $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.modules.d/$f
done

sed -i '/^#LoadModule mpm_%{mpm}_module /s/^#//' \
     $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.modules.d/00-mpm.conf
touch -r $RPM_SOURCE_DIR/00-mpm.conf \
     $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.modules.d/00-mpm.conf

# install systemd override drop directory
# Web application packages can drop snippets into this location if
# they need ExecStart[pre|post].
mkdir $RPM_BUILD_ROOT%{_unitdir}/httpd.service.d
mkdir $RPM_BUILD_ROOT%{_unitdir}/httpd.socket.d

install -m 644 -p $RPM_SOURCE_DIR/10-listen443.conf \
      $RPM_BUILD_ROOT%{_unitdir}/httpd.socket.d/10-listen443.conf

for f in welcome.conf ssl.conf manual.conf userdir.conf; do
  install -m 644 -p $RPM_SOURCE_DIR/$f \
        $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/$f
done

# Split-out extra config shipped as default in conf.d:
for f in autoindex; do
  install -m 644 docs/conf/extra/httpd-${f}.conf \
        $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/${f}.conf
done

# Extra config trimmed:
rm -v docs/conf/extra/httpd-{ssl,userdir}.conf

rm $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf/*.conf
install -m 644 -p $RPM_SOURCE_DIR/httpd.conf \
   $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf/httpd.conf

mkdir $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 -p $RPM_SOURCE_DIR/htcacheclean.sysconf \
   $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/htcacheclean

# tmpfiles.d configuration
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d 
install -m 644 -p $RPM_SOURCE_DIR/httpd.tmpfiles \
   $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d/httpd.conf

# Other directories
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/dav \
         $RPM_BUILD_ROOT%{_localstatedir}/lib/httpd \
         $RPM_BUILD_ROOT/run/httpd/htcacheclean

# Substitute in defaults which are usually done (badly) by "make install"
sed -i \
   "s,@@ServerRoot@@/var,%{_localstatedir}/lib/dav,;
    s,@@ServerRoot@@/user.passwd,/etc/httpd/conf/user.passwd,;
    s,@@ServerRoot@@/docs,%{docroot},;
    s,@@ServerRoot@@,%{docroot},;
    s,@@Port@@,80,;" \
    docs/conf/extra/*.conf

# Create cache directory
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/cache/httpd \
         $RPM_BUILD_ROOT%{_localstatedir}/cache/httpd/proxy \
         $RPM_BUILD_ROOT%{_localstatedir}/cache/httpd/ssl

# Make the MMN accessible to module packages
echo %{mmnisa} > $RPM_BUILD_ROOT%{_includedir}/httpd/.mmn
mkdir -p $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d
cat > $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/macros.httpd <<EOF
%%_httpd_mmn %{mmnisa}
%%_httpd_apxs %%{_bindir}/apxs
%%_httpd_modconfdir %%{_sysconfdir}/httpd/conf.modules.d
%%_httpd_confdir %%{_sysconfdir}/httpd/conf.d
%%_httpd_contentdir %{contentdir}
%%_httpd_moddir %%{_libdir}/httpd/modules
EOF

# Handle contentdir
mkdir $RPM_BUILD_ROOT%{contentdir}/noindex
tar xzf %{SOURCE1} -C $RPM_BUILD_ROOT%{contentdir}/noindex/ --strip-components=1
rm -rf %{contentdir}/htdocs

# remove manual sources
find $RPM_BUILD_ROOT%{contentdir}/manual \( \
    -name \*.xml -o -name \*.xml.* -o -name \*.ent -o -name \*.xsl -o -name \*.dtd \
    \) -print0 | xargs -0 rm -f

# Strip the manual down just to English and replace the typemaps with flat files:
set +x
for f in `find $RPM_BUILD_ROOT%{contentdir}/manual -name \*.html -type f`; do
   if test -f ${f}.en; then
      cp ${f}.en ${f}
      rm ${f}.*
   fi
done
set -x

# Clean Document Root
rm -v $RPM_BUILD_ROOT%{docroot}/html/*.html \
      $RPM_BUILD_ROOT%{docroot}/cgi-bin/*

# Symlink for the powered-by-$DISTRO image:
ln -s ../../pixmaps/poweredby.png \
        $RPM_BUILD_ROOT%{contentdir}/icons/poweredby.png

# symlinks for /etc/httpd
rmdir $RPM_BUILD_ROOT/etc/httpd/{state,run}
ln -s ../..%{_localstatedir}/log/httpd $RPM_BUILD_ROOT/etc/httpd/logs
ln -s ../..%{_localstatedir}/lib/httpd $RPM_BUILD_ROOT/etc/httpd/state
ln -s /run/httpd $RPM_BUILD_ROOT/etc/httpd/run
ln -s ../..%{_libdir}/httpd/modules $RPM_BUILD_ROOT/etc/httpd/modules

# install http-ssl-pass-dialog
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}
install -m755 $RPM_SOURCE_DIR/httpd-ssl-pass-dialog \
        $RPM_BUILD_ROOT%{_libexecdir}/httpd-ssl-pass-dialog

# install http-ssl-gencerts
install -m755 $RPM_SOURCE_DIR/httpd-ssl-gencerts \
        $RPM_BUILD_ROOT%{_libexecdir}/httpd-ssl-gencerts

# Install action scripts
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/httpd
for f in graceful configtest; do
    install -p -m 755 $RPM_SOURCE_DIR/action-${f}.sh \
            $RPM_BUILD_ROOT%{_libexecdir}/initscripts/legacy-actions/httpd/${f}
done

# Install logrotate config
mkdir -p $RPM_BUILD_ROOT/etc/logrotate.d
install -m 644 -p $RPM_SOURCE_DIR/httpd.logrotate \
        $RPM_BUILD_ROOT/etc/logrotate.d/httpd

# Install man pages
install -d $RPM_BUILD_ROOT%{_mandir}/man8 $RPM_BUILD_ROOT%{_mandir}/man5
install -m 644 -p httpd.service.8 httpd-init.service.8 httpd.socket.8 \
        httpd@.service.8  htcacheclean.service.8 \
        $RPM_BUILD_ROOT%{_mandir}/man8
install -m 644 -p httpd.conf.5 \
        $RPM_BUILD_ROOT%{_mandir}/man5

# fix man page paths
sed -e "s|/usr/local/apache2/conf/httpd.conf|/etc/httpd/conf/httpd.conf|" \
    -e "s|/usr/local/apache2/conf/mime.types|/etc/mime.types|" \
    -e "s|/usr/local/apache2/conf/magic|/etc/httpd/conf/magic|" \
    -e "s|/usr/local/apache2/logs/error_log|/var/log/httpd/error_log|" \
    -e "s|/usr/local/apache2/logs/access_log|/var/log/httpd/access_log|" \
    -e "s|/usr/local/apache2/logs/httpd.pid|/run/httpd/httpd.pid|" \
    -e "s|/usr/local/apache2|/etc/httpd|" < docs/man/httpd.8 \
  > $RPM_BUILD_ROOT%{_mandir}/man8/httpd.8

# Make ap_config_layout.h libdir-agnostic
sed -i '/.*DEFAULT_..._LIBEXECDIR/d;/DEFAULT_..._INSTALLBUILDDIR/d' \
    $RPM_BUILD_ROOT%{_includedir}/httpd/ap_config_layout.h

# Fix path to instdso in special.mk
sed -i '/instdso/s,top_srcdir,top_builddir,' \
    $RPM_BUILD_ROOT%{_libdir}/httpd/build/special.mk

# Remove unpackaged files
rm -vf \
      $RPM_BUILD_ROOT%{_libdir}/*.exp \
      $RPM_BUILD_ROOT/etc/httpd/conf/mime.types \
      $RPM_BUILD_ROOT%{_libdir}/httpd/modules/*.exp \
      $RPM_BUILD_ROOT%{_libdir}/httpd/build/config.nice \
      $RPM_BUILD_ROOT%{_bindir}/{ap?-config,dbmmanage} \
      $RPM_BUILD_ROOT%{_sbindir}/{checkgid,envvars*} \
      $RPM_BUILD_ROOT%{contentdir}/htdocs/* \
      $RPM_BUILD_ROOT%{_mandir}/man1/dbmmanage.* \
      $RPM_BUILD_ROOT%{contentdir}/cgi-bin/*

rm -rf $RPM_BUILD_ROOT/etc/httpd/conf/{original,extra}

%pre filesystem
getent group apache >/dev/null || groupadd -g 48 -r apache
getent passwd apache >/dev/null || \
  useradd -r -u 48 -g apache -s /sbin/nologin \
    -d %{contentdir} -c "Apache" apache
exit 0

%post
%systemd_post httpd.service htcacheclean.service httpd.socket

%preun
%systemd_preun httpd.service htcacheclean.service httpd.socket

%postun
%systemd_postun

# Trigger for conversion from SysV, per guidelines at:
# https://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Systemd
%triggerun -- httpd < 2.2.21-5
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save httpd.service >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del httpd >/dev/null 2>&1 || :

%posttrans
test -f /etc/sysconfig/httpd-disable-posttrans || \
  /bin/systemctl try-restart --no-block httpd.service htcacheclean.service >/dev/null 2>&1 || :

%check
# Check the built modules are all PIC
if readelf -d $RPM_BUILD_ROOT%{_libdir}/httpd/modules/*.so | grep TEXTREL; then
   : modules contain non-relocatable code
   exit 1
fi
set +x
rv=0
# Ensure every mod_* that's built is loaded.
for f in $RPM_BUILD_ROOT%{_libdir}/httpd/modules/*.so; do
  m=${f##*/}
  if ! grep -q $m $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.modules.d/*.conf; then
    echo ERROR: Module $m not configured.  Disable it, or load it.
    rv=1
  fi
done
# Ensure every loaded mod_* is actually built
mods=`grep -h ^LoadModule $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.modules.d/*.conf | sed 's,.*modules/,,'`
for m in $mods; do
  f=$RPM_BUILD_ROOT%{_libdir}/httpd/modules/${m}
  if ! test -x $f; then
    echo ERROR: Module $m is configured but not built.
    rv=1
  fi
done
set -x
exit $rv

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%doc ABOUT_APACHE README CHANGES LICENSE VERSIONING NOTICE
%doc docs/conf/extra/*.conf
%doc instance.conf

%{_sysconfdir}/httpd/modules
%{_sysconfdir}/httpd/logs
%{_sysconfdir}/httpd/state
%{_sysconfdir}/httpd/run
%dir %{_sysconfdir}/httpd/conf
%config(noreplace) %{_sysconfdir}/httpd/conf/httpd.conf
%config(noreplace) %{_sysconfdir}/httpd/conf/magic

%config(noreplace) %{_sysconfdir}/logrotate.d/httpd

%config(noreplace) %{_sysconfdir}/httpd/conf.d/*.conf
%exclude %{_sysconfdir}/httpd/conf.d/ssl.conf
%exclude %{_sysconfdir}/httpd/conf.d/manual.conf

%dir %{_sysconfdir}/httpd/conf.modules.d
%{_sysconfdir}/httpd/conf.modules.d/README
%config(noreplace) %{_sysconfdir}/httpd/conf.modules.d/*.conf
%exclude %{_sysconfdir}/httpd/conf.modules.d/00-ssl.conf
%exclude %{_sysconfdir}/httpd/conf.modules.d/00-proxyhtml.conf
%exclude %{_sysconfdir}/httpd/conf.modules.d/01-ldap.conf
%exclude %{_sysconfdir}/httpd/conf.modules.d/01-session.conf

%config(noreplace) %{_sysconfdir}/sysconfig/htcacheclean
%{_prefix}/lib/tmpfiles.d/httpd.conf

%dir %{_libexecdir}/initscripts/legacy-actions/httpd
%{_libexecdir}/initscripts/legacy-actions/httpd/*

%{_sbindir}/ht*
%{_sbindir}/fcgistarter
%{_sbindir}/apachectl
%{_sbindir}/rotatelogs
%caps(cap_setuid,cap_setgid+pe) %attr(510,root,%{suexec_caller}) %{_sbindir}/suexec

%dir %{_libdir}/httpd
%dir %{_libdir}/httpd/modules
%{_libdir}/httpd/modules/mod*.so
%exclude %{_libdir}/httpd/modules/mod_auth_form.so
%exclude %{_libdir}/httpd/modules/mod_ssl.so
%exclude %{_libdir}/httpd/modules/mod_*ldap.so
%exclude %{_libdir}/httpd/modules/mod_proxy_html.so
%exclude %{_libdir}/httpd/modules/mod_xml2enc.so
%exclude %{_libdir}/httpd/modules/mod_session*.so

%dir %{contentdir}/error
%dir %{contentdir}/error/include
%dir %{contentdir}/noindex
%{contentdir}/icons/*
%{contentdir}/error/README
%{contentdir}/error/*.var
%{contentdir}/error/include/*.html
%{contentdir}/noindex/*

%attr(0710,root,apache) %dir /run/httpd
%attr(0700,apache,apache) %dir /run/httpd/htcacheclean
%attr(0700,root,root) %dir %{_localstatedir}/log/httpd
%attr(0700,apache,apache) %dir %{_localstatedir}/lib/dav
%attr(0700,apache,apache) %dir %{_localstatedir}/lib/httpd
%attr(0700,apache,apache) %dir %{_localstatedir}/cache/httpd
%attr(0700,apache,apache) %dir %{_localstatedir}/cache/httpd/proxy

%{_mandir}/man8/*
%{_mandir}/man5/*
%exclude %{_mandir}/man8/httpd-init.*

%{_unitdir}/httpd.service
%{_unitdir}/httpd@.service
%{_unitdir}/htcacheclean.service
%{_unitdir}/*.socket

%files filesystem
%dir %{_sysconfdir}/httpd
%dir %{_sysconfdir}/httpd/conf.d
%{_sysconfdir}/httpd/conf.d/README
%dir %{docroot}
%dir %{docroot}/cgi-bin
%dir %{docroot}/html
%dir %{contentdir}
%dir %{contentdir}/icons
%attr(755,root,root) %dir %{_unitdir}/httpd.service.d
%attr(755,root,root) %dir %{_unitdir}/httpd.socket.d

%files tools
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*
%doc LICENSE NOTICE
%exclude %{_bindir}/apxs
%exclude %{_mandir}/man1/apxs.1*

%files manual
%defattr(-,root,root)
%{contentdir}/manual
%config(noreplace) %{_sysconfdir}/httpd/conf.d/manual.conf

%files -n mod_ssl
%defattr(-,root,root)
%{_libdir}/httpd/modules/mod_ssl.so
%config(noreplace) %{_sysconfdir}/httpd/conf.modules.d/00-ssl.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/ssl.conf
%attr(0700,apache,root) %dir %{_localstatedir}/cache/httpd/ssl
%{_unitdir}/httpd-init.service
%{_libexecdir}/httpd-ssl-pass-dialog
%{_libexecdir}/httpd-ssl-gencerts
%{_unitdir}/httpd.socket.d/10-listen443.conf
%{_mandir}/man8/httpd-init.*

%files -n mod_proxy_html
%defattr(-,root,root)
%{_libdir}/httpd/modules/mod_proxy_html.so
%{_libdir}/httpd/modules/mod_xml2enc.so
%config(noreplace) %{_sysconfdir}/httpd/conf.modules.d/00-proxyhtml.conf

%files -n mod_ldap
%defattr(-,root,root)
%{_libdir}/httpd/modules/mod_*ldap.so
%config(noreplace) %{_sysconfdir}/httpd/conf.modules.d/01-ldap.conf

%files -n mod_session
%defattr(-,root,root)
%{_libdir}/httpd/modules/mod_session*.so
%{_libdir}/httpd/modules/mod_auth_form.so
%config(noreplace) %{_sysconfdir}/httpd/conf.modules.d/01-session.conf

%files devel
%defattr(-,root,root)
%{_includedir}/httpd
%{_bindir}/apxs
%{_mandir}/man1/apxs.1*
%dir %{_libdir}/httpd/build
%{_libdir}/httpd/build/*.mk
%{_libdir}/httpd/build/*.sh
%{_rpmconfigdir}/macros.d/macros.httpd

%changelog
* Tue Apr 28 2020 CentOS Sources <bugs@centos.org> - 2.4.37-21.el8.centos
- Apply debranding changes

* Mon Dec 02 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-21
- Resolves: #1775158 - POST request with TLS 1.3 PHA client auth fails:
  Re-negotiation handshake failed: Client certificate missing

* Sun Dec 01 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-20
- Resolves: #1704317 - Add support for SSLKEYLOGFILE

* Thu Nov 28 2019 Joe Orton <jorton@redhat.com> - 2.4.37-19
- mod_cgid: enable fd passing (#1633224)

* Mon Nov 18 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-18
- Resolves: #1744121 - Unexpected OCSP in proxy SSL connection
- Resolves: #1725031 - htpasswd: support SHA-x passwords for FIPS compatibility
- Resolves: #1633224 - mod_cgid logging issues

* Wed Oct 02 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-17
- remove bundled mod_md module
- Related: #1747898 - add mod_md package

* Thu Aug 29 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-16
- Resolves: #1744999 - CVE-2019-9511 httpd:2.4/mod_http2: HTTP/2: large amount
  of data request leads to denial of service
- Resolves: #1745086 - CVE-2019-9516 httpd:2.4/mod_http2: HTTP/2: 0-length
  headers leads to denial of service
- Resolves: #1745154 - CVE-2019-9517 httpd:2.4/mod_http2: HTTP/2: request for
  large response leads to denial of service

* Tue Jul 16 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-15
- Resolves: #1730721 - absolute path used for default state and runtime dir by
  default

* Thu Jun 27 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-14
- Resolves: #1724549 - httpd response contains garbage in Content-Type header

* Wed Jun 12 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-13
- Resolves: #1696142 - CVE-2019-0217 httpd:2.4/httpd: mod_auth_digest: access
  control bypass due to race condition
- Resolves: #1696097 - CVE-2019-0220 httpd:2.4/httpd: URL normalization
  inconsistency
- Resolves: #1669221 - `ExtendedStatus Off` directive when using mod_systemd
  causes systemctl to hang
- Resolves: #1673022 - httpd can not be started with mod_md enabled

* Mon Apr 08 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-11
- Resolves: #1695432 - CVE-2019-0211 httpd: privilege escalation
  from modules scripts
- Resolves: #1696091 - CVE-2019-0215 httpd:2.4/httpd: mod_ssl: access control 
  bypass when using per-location client certification authentication

* Wed Feb 06 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-10
- Resolves: #1672977 - state-dir corruption on reload 

* Tue Feb 05 2019 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-9
- Resolves: #1670716 - Coredump when starting in FIPS mode

* Fri Feb  1 2019 Joe Orton <jorton@redhat.com> - 2.4.37-8
- add security fix for CVE-2019-0190 (#1671282)

* Tue Dec 11 2018 Joe Orton <jorton@redhat.com> - 2.4.37-7
- add DefaultStateDir/ap_state_dir_relative() (#1653009)
- mod_dav_fs: use state dir for default DAVLockDB
- mod_md: use state dir for default MDStoreDir

* Mon Dec 10 2018 Joe Orton <jorton@redhat.com> - 2.4.37-6
- add httpd.conf(5) (#1611361)

* Mon Nov 26 2018 Luboš Uhliarik <luhliari@redhat.com> - 2.4.37-5
- Resolves: #1652966 - Missing RELEASE in http header

* Fri Nov 23 2018 Luboš Uhliarik <luhliari@redhat.com> - 2.4.37-4
- Resolves: #1641951 - No Documentation= line in htcacheclean.service files

* Fri Nov 23 2018 Luboš Uhliarik <luhliari@redhat.com> - 2.4.37-3
- Resolves: #1643713 - TLS connection allowed while all protocols are forbidden

* Thu Nov 22 2018 Joe Orton <jorton@redhat.com> - 2.4.37-2
- mod_ssl: fix off-by-one causing crashes in CGI children (#1649428)

* Wed Nov 21 2018 Lubos Uhliarik <luhliari@redhat.com> - 2.4.37-1
- Resolves: #1644625 - httpd rebase to 2.4.37

* Thu Oct 18 2018 Luboš Uhliarik <luhliari@redhat.com> - 2.4.35-10
- Related: #1493510 - RFE: httpd, add IP_FREEBIND support for Listen

* Tue Oct 16 2018 Lubos Uhliarik <luhliari@redhat.com> - 2.4.35-9
- mod_ssl: allow sending multiple CA names which differ only in case

* Tue Oct 16 2018 Joe Orton <jorton@redhat.com> - 2.4.35-7
- mod_ssl: drop SSLRandomSeed from default config (#1638730)
- mod_ssl: follow OpenSSL protocol defaults if SSLProtocol
     is not configured (Rob Crittenden, #1638738)

* Mon Oct 15 2018 Joe Orton <jorton@redhat.com> - 2.4.35-5
- mod_ssl: don't require SSLCryptoDevice to be set for PKCS#11 cert

* Mon Oct 15 2018 Lubos Uhliarik <luhliari@redhat.com> - 2.4.35-4
- Resolves: #1635681 - sync with Fedora 28/29 httpd
- comment-out SSLProtocol, SSLProxyProtocol from ssl.conf in default
  configuration; now follow OpenSSL system default (#1468322)
- dropped NPN support
- mod_md: change hard-coded default MdStoreDir to state/md (#1563846)
- don't block on service try-restart in posttrans scriptlet
- build and load mod_brotli
- mod_systemd: show bound ports in status and log to journal
  at startup
- updated httpd.service.xml man page
- tweak wording in privkey passphrase prompt
- drop sslmultiproxy patch
- apachectl: don't read /etc/sysconfig/httpd
- drop irrelevant Obsoletes for devel subpackage
- move instantiated httpd@.service to main httpd package

* Mon Oct 15 2018 Lubos Uhliarik <luhliari@redhat.com> - 2.4.35-3
- Resolves: #1602548 - various covscan fixes

* Thu Sep 27 2018 Lubos Uhliarik <luhliari@redhat.com> - 2.4.35-2
- apache httpd can work with TLS 1.3 (#1617997)
- drop SSLv3 support patch

* Thu Sep 27 2018 Lubos Uhliarik <luhliari@redhat.com> - 2.4.35-1
- new version 2.4.35 (#1632754)

* Mon Sep 03 2018 Lubos Uhliarik <luhliari@redhat.com> - 2.4.33-4
- mod_ssl: enable SSLv3 and change behavior of "SSLProtocol All" 
  configuration (#1622630)

* Thu Jul 26 2018 Joe Orton <jorton@redhat.com> - 2.4.33-3
- mod_ssl: add PKCS#11 cert/key support (Anderson Sasaki, #1527084)

* Mon Apr 30 2018 Luboš Uhliarik <luhliari@redhat.com> - 2.4.33-2
- new version 2.4.33
- add mod_md subpackage; load mod_proxy_uwsgi by default

* Mon Apr 30 2018 Joe Orton <jorton@redhat.com> - 2.4.28-8
- remove %%ghosted /etc/sysconfig/httpd (#1572676)

* Wed Mar 07 2018 Luboš Uhliarik <luhliari@redhat.com> - 2.4.28-2
- Resolves: #1512563 - httpd: update welcome page branding
- Resolves: #1511123 - RFE: httpd use event MPM by default
- Resolves: #1493510 - RFE: httpd, add IP_FREEBIND support for Listen

* Fri Oct 06 2017 Luboš Uhliarik <luhliari@redhat.com> - 2.4.28-1
- new version 2.4.28

* Tue Oct  3 2017 Joe Orton <jorton@redhat.com> - 2.4.27-14
- add notes on enabling httpd_graceful_shutdown boolean for prefork

* Fri Sep 22 2017 Joe Orton <jorton@redhat.com> - 2.4.27-13
- drop Requires(post) for mod_ssl

* Fri Sep 22 2017 Joe Orton <jorton@redhat.com> - 2.4.27-12
- better error handling in httpd-ssl-gencerts (#1494556)

* Thu Sep 21 2017 Stephen Gallagher <sgallagh@redhat.com> - 2.4.27-11
- Require sscg 2.2.0 for creating service and CA certificates together

* Thu Sep 21 2017 Jeroen van Meeuwen <kanarip@fedoraproject.org> - 2.4.27-10
- Address CVE-2017-9798 by applying patch from upstream (#1490344)

* Thu Sep 21 2017 Joe Orton <jorton@redhat.com> - 2.4.27-9
- use sscg defaults; append CA cert to generated cert
- document httpd-init.service in httpd-init.service(8)

* Thu Sep 21 2017 Jeroen van Meeuwen <kanarip@fedoraproject.org> - 2.4.27-8
- Address CVE-2017-9798 by applying patch from upstream (#1490344)

* Wed Sep 20 2017 Stephen Gallagher <sgallagh@redhat.com> - 2.4.27-8.1
- Generate SSL certificates on service start, not %%posttrans

* Tue Sep 19 2017 Joe Orton <jorton@redhat.com> - 2.4.27-8.1
- move httpd.service.d, httpd.socket.d dirs to -filesystem

* Wed Sep 13 2017 Joe Orton <jorton@redhat.com> - 2.4.27-7
- add new content-length filter (upstream PR 61222)

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.27-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.27-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jul 18 2017 Joe Orton <jorton@redhat.com> - 2.4.27-4
- update mod_systemd (r1802251)

* Mon Jul 17 2017 Joe Orton <jorton@redhat.com> - 2.4.27-3
- switch to event by default for Fedora 27 and later (#1471708)

* Wed Jul 12 2017 Luboš Uhliarik <luhliari@redhat.com> - 2.4.27-2
- Resolves: #1469959 - httpd update cleaned out /etc/sysconfig

* Mon Jul 10 2017 Luboš Uhliarik <luhliari@redhat.com> - 2.4.27-1
- new version 2.4.27

* Fri Jun 30 2017 Joe Orton <jorton@redhat.com> - 2.4.26-2
- mod_proxy_fcgi: fix further regressions (PR 61202)

* Mon Jun 19 2017 Luboš Uhliarik <luhliari@redhat.com> - 2.4.26-1
- new version 2.4.26

* Mon Jun  5 2017 Joe Orton <jorton@redhat.com> - 2.4.25-10
- move unit man pages to section 8, add as Documentation= in units

* Fri May 19 2017 Joe Orton <jorton@redhat.com> - 2.4.25-9
- add httpd.service(5) and httpd.socket(5) man pages

* Tue May 16 2017 Joe Orton <jorton@redhat.com> - 2.4.25-8
- require mod_http2, now packaged separately

* Wed Mar 29 2017 Luboš Uhliarik <luhliari@redhat.com> - 2.4.25-7
- Resolves: #1397243 - Backport Apache Bug 53098 - mod_proxy_ajp:
  patch to set worker secret passed to tomcat

* Tue Mar 28 2017 Luboš Uhliarik <luhliari@redhat.com> - 2.4.25-6
- Resolves: #1434916 - httpd.service: Failed with result timeout

* Fri Mar 24 2017 Joe Orton <jorton@redhat.com> - 2.4.25-5
- link only httpd, not support/* against -lselinux -lsystemd

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.25-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Joe Orton <jorton@redhat.com> - 2.4.25-3
- mod_watchdog: restrict thread lifetime (#1410883)

* Thu Dec 22 2016 Luboš Uhliarik <luhliari@redhat.com> - 2.4.25-2
- Resolves: #1358875 - require nghttp2 >= 1.5.0

* Thu Dec 22 2016 Luboš Uhliarik <luhliari@redhat.com> - 2.4.25-1
- new version 2.4.25

* Mon Dec 05 2016 Luboš Uhliarik <luhliari@redhat.com> - 2.4.23-7
- Resolves: #1401530 - CVE-2016-8740 httpd: Incomplete handling of
  LimitRequestFields directive in mod_http2

* Mon Nov 14 2016 Joe Orton <jorton@redhat.com> - 2.4.23-6
- fix build with OpenSSL 1.1 (#1392900)
- fix typos in ssl.conf (josef randinger, #1379407)

* Wed Nov  2 2016 Joe Orton <jorton@redhat.com> - 2.4.23-5
- no longer package /etc/sysconfig/httpd
- synch ssl.conf with upstream

* Mon Jul 18 2016 Joe Orton <jorton@redhat.com> - 2.4.23-4
- add security fix for CVE-2016-5387

* Thu Jul  7 2016 Joe Orton <jorton@redhat.com> - 2.4.23-3
- load mod_watchdog by default (#1353582)

* Thu Jul  7 2016 Joe Orton <jorton@redhat.com> - 2.4.23-2
- restore build of mod_proxy_fdpass (#1325883)
- improve check tests to catch configured-but-not-built modules

* Thu Jul  7 2016 Joe Orton <jorton@redhat.com> - 2.4.23-1
- update to 2.4.23 (#1325883, #1353203)
- load mod_proxy_hcheck
- recommend use of "systemctl edit" in httpd.service

* Thu Apr  7 2016 Joe Orton <jorton@redhat.com> - 2.4.18-6
- have "apachectl graceful" start httpd if not running, per man page

* Wed Apr  6 2016 Joe Orton <jorton@redhat.com> - 2.4.18-5
- use redirects for lang-specific /manual/ URLs

* Fri Mar 18 2016 Joe Orton <jorton@redhat.com> - 2.4.18-4
- fix welcome page HTML validity (Ville Skyttä)

* Fri Mar 18 2016 Joe Orton <jorton@redhat.com> - 2.4.18-3
- remove httpd pre script (duplicate of httpd-filesystem's)
- in httpd-filesystem pre script, create group/user iff non-existent

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.18-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 14 2015 Jan Kaluza <jkaluza@redhat.com> - 2.4.18-1
- update to new version 2.4.18

* Wed Dec  9 2015 Joe Orton <jorton@redhat.com> - 2.4.17-4
- re-enable mod_asis due to popular demand (#1284315)

* Mon Oct 26 2015 Jan Kaluza <jkaluza@redhat.com> - 2.4.17-3
- fix crash when using -X argument (#1272234)

* Wed Oct 14 2015 Jan Kaluza <jkaluza@redhat.com> - 2.4.17-2
- rebase socket activation patch to 2.4.17

* Tue Oct 13 2015 Joe Orton <jorton@redhat.com> - 2.4.17-1
- update to 2.4.17 (#1271224)
- build, load mod_http2
- don't build mod_asis, mod_file_cache
- load mod_cache_socache, mod_proxy_wstunnel by default
- check every built mod_* is configured
- synch ssl.conf with upstream; disable SSLv3 by default

* Wed Jul 15 2015 Jan Kaluza <jkaluza@redhat.com> - 2.4.12-4
- update to 2.4.16

* Tue Jul  7 2015 Joe Orton <jorton@redhat.com> - 2.4.12-3
- mod_ssl: use "localhost" in the dummy SSL cert if len(FQDN) > 59 chars

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Mar 27 2015 Jan Kaluza <jkaluza@redhat.com> - 2.4.12-1
- update to 2.4.12

* Tue Mar 24 2015 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-17
- fix compilation with lua-5.3

* Tue Mar 24 2015 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-16
- remove filter for auto-provides of httpd modules, it is not needed since F20

* Wed Dec 17 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-15
- core: fix bypassing of mod_headers rules via chunked requests (CVE-2013-5704)
- mod_cache: fix NULL pointer dereference on empty Content-Type (CVE-2014-3581)
- mod_proxy_fcgi: fix a potential crash with long headers (CVE-2014-3583)
- mod_lua: fix handling of the Require line when a LuaAuthzProvider is used
  in multiple Require directives with different arguments (CVE-2014-8109)

* Tue Oct 14 2014 Joe Orton <jorton@redhat.com> - 2.4.10-14
- require apr-util 1.5.x

* Thu Sep 18 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-13
- use NoDelay and DeferAcceptSec in httpd.socket

* Mon Sep 08 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-12
- increase suexec minimum acceptable uid/gid to 1000 (#1136391)

* Wed Sep 03 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-11
- fix hostname requirement and conflict with openssl-libs

* Mon Sep 01 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-10
- use KillMode=mixed in httpd.service (#1135122)

* Fri Aug 29 2014 Joe Orton <jorton@redhat.com> - 2.4.10-9
- set vstring based on /etc/os-release (Pat Riehecky, #1114539)

* Fri Aug 29 2014 Joe Orton <jorton@redhat.com> - 2.4.10-8
- pull in httpd-filesystem as Requires(pre) (#1128328)
- fix cipher selection in default ssl.conf, depend on new OpenSSL (#1134348)
- require hostname for mod_ssl post script (#1135118)

* Fri Aug 22 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-7
- mod_systemd: updated to the latest version
- use -lsystemd instead of -lsystemd-daemon (#1125084)
- fix possible crash in SIGINT handling (#958934)

* Thu Aug 21 2014 Joe Orton <jorton@redhat.com> - 2.4.10-6
- mod_ssl: treat "SSLCipherSuite PROFILE=..." as special (#1109119)
- switch default ssl.conf to use PROFILE=SYSTEM (#1109119)

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.10-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-4
- add /usr/bin/useradd dependency to -filesystem requires

* Thu Aug 14 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.10-3
- fix creating apache user in pre script (#1128328)

* Thu Jul 31 2014 Joe Orton <jorton@redhat.com> - 2.4.10-2
- enable mod_request by default for mod_auth_form
- move disabled-by-default modules from 00-base.conf to 00-optional.conf

* Mon Jul 21 2014 Joe Orton <jorton@redhat.com> - 2.4.10-1
- update to 2.4.10
- expand variables in docdir example configs

* Tue Jul 08 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.9-8
- add support for systemd socket activation (#1111648)

* Mon Jul 07 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.9-7
- remove conf.modules.d from httpd-filesystem subpackage (#1081453)

* Mon Jul 07 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.9-6
- add httpd-filesystem subpackage (#1081453)

* Fri Jun 20 2014 Joe Orton <jorton@redhat.com> - 2.4.9-5
- mod_ssl: don't use the default OpenSSL cipher suite in ssl.conf (#1109119)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.9-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Mar 28 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.9-3
- add support for SetHandler + proxy (#1078970)

* Thu Mar 27 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.9-2
- move macros from /etc/rpm to macros.d (#1074277)
- remove unused patches

* Mon Mar 17 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.9-1
- update to 2.4.9

* Fri Feb 28 2014 Joe Orton <jorton@redhat.com> - 2.4.7-6
- use 2048-bit RSA key with SHA-256 signature in dummy certificate

* Fri Feb 28 2014 Stephen Gallagher <sgallagh@redhat.com> 2.4.7-5
- Create drop directory for systemd snippets

* Thu Feb 27 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.7-4
- remove provides of old MMN, because it contained double-dash (#1068851)

* Thu Feb 20 2014 Jan Kaluza <jkaluza@redhat.com> - 2.4.7-3
- fix graceful restart using legacy actions

* Thu Dec 12 2013 Joe Orton <jorton@redhat.com> - 2.4.7-2
- conflict with pre-1.5.0 APR
- fix sslsninotreq patch

* Wed Nov 27 2013 Joe Orton <jorton@redhat.com> - 2.4.7-1
- update to 2.4.7 (#1034071)

* Fri Nov 22 2013 Joe Orton <jorton@redhat.com> - 2.4.6-10
- switch to requiring system-logos-httpd (#1031288)

* Tue Nov 12 2013 Joe Orton <jorton@redhat.com> - 2.4.6-9
- change mmnisa to drop "-" altogether

* Tue Nov 12 2013 Joe Orton <jorton@redhat.com> - 2.4.6-8
- drop ambiguous invalid "-" in RHS of httpd-mmn Provide, keeping old Provide
  for transition

* Fri Nov  1 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-7
- systemd: use {MAINPID} notation to ensure /bin/kill has always the second arg

* Thu Oct 31 2013 Joe Orton <jorton@redhat.com> - 2.4.6-6
- mod_ssl: allow SSLEngine to override Listen-based default (r1537535)

* Thu Oct 24 2013 Jan kaluza <jkaluza@redhat.com> - 2.4.6-5
- systemd: send SIGWINCH signal without httpd -k in ExecStop

* Mon Oct 21 2013 Joe Orton <jorton@redhat.com> - 2.4.6-4
- load mod_macro by default (#998452)
- add README to conf.modules.d
- mod_proxy_http: add possible fix for threading issues (r1534321)
- core: add fix for truncated output with CGI scripts (r1530793)

* Thu Oct 10 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-3
- require fedora-logos-httpd (#1009162)

* Wed Jul 31 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.6-2
- revert fix for dumping vhosts twice

* Mon Jul 22 2013 Joe Orton <jorton@redhat.com> - 2.4.6-1
- update to 2.4.6
- mod_ssl: use revised NPN API (r1487772)

* Thu Jul 11 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-12
- mod_unique_id: replace use of hostname + pid with PRNG output (#976666)
- apxs: mention -p option in manpage

* Tue Jul  2 2013 Joe Orton <jorton@redhat.com> - 2.4.4-11
- add patch for aarch64 (Dennis Gilmore, #925558)

* Mon Jul  1 2013 Joe Orton <jorton@redhat.com> - 2.4.4-10
- remove duplicate apxs man page from httpd-tools

* Mon Jun 17 2013 Joe Orton <jorton@redhat.com> - 2.4.4-9
- remove zombie dbmmanage script

* Fri May 31 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-8
- return 400 Bad Request on malformed Host header

* Fri May 24 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-7
- ignore /etc/sysconfig/httpd and document systemd way of setting env variables
  in this file

* Mon May 20 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-6
- htpasswd/htdbm: fix hash generation bug (#956344)
- do not dump vhosts twice in httpd -S output (#928761)
- mod_cache: fix potential crash caused by uninitialized variable (#954109)

* Thu Apr 18 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-5
- execute systemctl reload as result of apachectl graceful
- mod_ssl: ignore SNI hints unless required by config
- mod_cache: forward-port CacheMaxExpire "hard" option
- mod_ssl: fall back on another module's proxy hook if mod_ssl proxy
  is not configured.

* Tue Apr 16 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-4
- fix service file to not send SIGTERM after ExecStop (#906321, #912288)

* Tue Mar 26 2013 Jan Kaluza <jkaluza@redhat.com> - 2.4.4-3
- protect MIMEMagicFile with IfModule (#893949)

* Tue Feb 26 2013 Joe Orton <jorton@redhat.com> - 2.4.4-2
- really package mod_auth_form in mod_session (#915438)

* Tue Feb 26 2013 Joe Orton <jorton@redhat.com> - 2.4.4-1
- update to 2.4.4
- fix duplicate ownership of mod_session config (#914901)

* Fri Feb 22 2013 Joe Orton <jorton@redhat.com> - 2.4.3-17
- add mod_session subpackage, move mod_auth_form there (#894500)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.3-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Jan  8 2013 Joe Orton <jorton@redhat.com> - 2.4.3-15
- add systemd service for htcacheclean

* Tue Nov 13 2012 Joe Orton <jorton@redhat.com> - 2.4.3-14
- drop patch for r1344712

* Tue Nov 13 2012 Joe Orton <jorton@redhat.com> - 2.4.3-13
- filter mod_*.so auto-provides (thanks to rcollet)
- pull in syslog logging fix from upstream (r1344712)

* Fri Oct 26 2012 Joe Orton <jorton@redhat.com> - 2.4.3-12
- rebuild to pick up new apr-util-ldap

* Tue Oct 23 2012 Joe Orton <jorton@redhat.com> - 2.4.3-11
- rebuild

* Wed Oct  3 2012 Joe Orton <jorton@redhat.com> - 2.4.3-10
- pull upstream patch r1392850 in addition to r1387633

* Mon Oct  1 2012 Joe Orton <jorton@redhat.com> - 2.4.3-9
- define PLATFORM in os.h using vendor string

* Mon Oct  1 2012 Joe Orton <jorton@redhat.com> - 2.4.3-8
- use systemd script unconditionally (#850149)

* Mon Oct  1 2012 Joe Orton <jorton@redhat.com> - 2.4.3-7
- use systemd scriptlets if available (#850149)
- don't run posttrans restart if /etc/sysconfig/httpd-disable-posttrans exists

* Mon Oct 01 2012 Jan Kaluza <jkaluza@redhat.com> - 2.4.3-6
- use systemctl from apachectl (#842736)

* Wed Sep 19 2012 Joe Orton <jorton@redhat.com> - 2.4.3-5
- fix some error log spam with graceful-stop (r1387633)
- minor mod_systemd tweaks

* Thu Sep 13 2012 Joe Orton <jorton@redhat.com> - 2.4.3-4
- use IncludeOptional for conf.d/*.conf inclusion

* Fri Sep 07 2012 Jan Kaluza <jkaluza@redhat.com> - 2.4.3-3
- adding mod_systemd to integrate with systemd better

* Tue Aug 21 2012 Joe Orton <jorton@redhat.com> - 2.4.3-2
- mod_ssl: add check for proxy keypair match (upstream r1374214)

* Tue Aug 21 2012 Joe Orton <jorton@redhat.com> - 2.4.3-1
- update to 2.4.3 (#849883)
- own the docroot (#848121)

* Mon Aug  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-23
- add mod_proxy fixes from upstream (r1366693, r1365604)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.2-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-21
- drop explicit version requirement on initscripts

* Thu Jul  5 2012 Joe Orton <jorton@redhat.com> - 2.4.2-20
- mod_ext_filter: fix error_log warnings

* Mon Jul  2 2012 Joe Orton <jorton@redhat.com> - 2.4.2-19
- support "configtest" and "graceful" as initscripts "legacy actions"

* Fri Jun  8 2012 Joe Orton <jorton@redhat.com> - 2.4.2-18
- avoid use of "core" GIF for a "core" directory (#168776)
- drop use of "syslog.target" in systemd unit file

* Thu Jun  7 2012 Joe Orton <jorton@redhat.com> - 2.4.2-17
- use _unitdir for systemd unit file
- use /run in unit file, ssl.conf

* Thu Jun  7 2012 Joe Orton <jorton@redhat.com> - 2.4.2-16
- mod_ssl: fix NPN patch merge

* Wed Jun  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-15
- move tmpfiles.d fragment into /usr/lib per new guidelines
- package /run/httpd not /var/run/httpd
- set runtimedir to /run/httpd likewise

* Wed Jun  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-14
- fix htdbm/htpasswd crash on crypt() failure (#818684)

* Wed Jun  6 2012 Joe Orton <jorton@redhat.com> - 2.4.2-13
- pull fix for NPN patch from upstream (r1345599)

* Thu May 31 2012 Joe Orton <jorton@redhat.com> - 2.4.2-12
- update suexec patch to use LOG_AUTHPRIV facility

* Thu May 24 2012 Joe Orton <jorton@redhat.com> - 2.4.2-11
- really fix autoindex.conf (thanks to remi@)

* Thu May 24 2012 Joe Orton <jorton@redhat.com> - 2.4.2-10
- fix autoindex.conf to allow symlink to poweredby.png

* Wed May 23 2012 Joe Orton <jorton@redhat.com> - 2.4.2-9
- suexec: use upstream version of patch for capability bit support

* Wed May 23 2012 Joe Orton <jorton@redhat.com> - 2.4.2-8
- suexec: use syslog rather than suexec.log, drop dac_override capability

* Tue May  1 2012 Joe Orton <jorton@redhat.com> - 2.4.2-7
- mod_ssl: add TLS NPN support (r1332643, #809599)

* Tue May  1 2012 Joe Orton <jorton@redhat.com> - 2.4.2-6
- add BR on APR >= 1.4.0

* Fri Apr 27 2012 Joe Orton <jorton@redhat.com> - 2.4.2-5
- use systemctl from logrotate (#221073)

* Fri Apr 27 2012 Joe Orton <jorton@redhat.com> - 2.4.2-4
- pull from upstream:
  * use TLS close_notify alert for dummy_connection (r1326980+)
  * cleanup symbol exports (r1327036+)

* Fri Apr 20 2012 Joe Orton <jorton@redhat.com> - 2.4.2-3
- really fix restart

* Fri Apr 20 2012 Joe Orton <jorton@redhat.com> - 2.4.2-2
- tweak default ssl.conf
- fix restart handling (#814645)
- use graceful restart by default

* Wed Apr 18 2012 Jan Kaluza <jkaluza@redhat.com> - 2.4.2-1
- update to 2.4.2

* Fri Mar 23 2012 Joe Orton <jorton@redhat.com> - 2.4.1-6
- fix macros

* Fri Mar 23 2012 Joe Orton <jorton@redhat.com> - 2.4.1-5
- add _httpd_moddir to macros

* Tue Mar 13 2012 Joe Orton <jorton@redhat.com> - 2.4.1-4
- fix symlink for poweredby.png
- fix manual.conf

* Tue Mar 13 2012 Joe Orton <jorton@redhat.com> - 2.4.1-3
- add mod_proxy_html subpackage (w/mod_proxy_html + mod_xml2enc)
- move mod_ldap, mod_authnz_ldap to mod_ldap subpackage

* Tue Mar 13 2012 Joe Orton <jorton@redhat.com> - 2.4.1-2
- clean docroot better
- ship proxy, ssl directories within /var/cache/httpd
- default config:
 * unrestricted access to (only) /var/www
 * remove (commented) Mutex, MaxRanges, ScriptSock
 * split autoindex config to conf.d/autoindex.conf
- ship additional example configs in docdir

* Tue Mar  6 2012 Joe Orton <jorton@redhat.com> - 2.4.1-1
- update to 2.4.1
- adopt upstream default httpd.conf (almost verbatim)
- split all LoadModules to conf.modules.d/*.conf
- include conf.d/*.conf at end of httpd.conf
- trim %%changelog

* Mon Feb 13 2012 Joe Orton <jorton@redhat.com> - 2.2.22-2
- fix build against PCRE 8.30

* Mon Feb 13 2012 Joe Orton <jorton@redhat.com> - 2.2.22-1
- update to 2.2.22

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 2.2.21-8
- Rebuild against PCRE 8.30

* Mon Jan 23 2012 Jan Kaluza <jkaluza@redhat.com> - 2.2.21-7
- fix #783629 - start httpd after named

* Mon Jan 16 2012 Joe Orton <jorton@redhat.com> - 2.2.21-6
- complete conversion to systemd, drop init script (#770311)
- fix comments in /etc/sysconfig/httpd (#771024)
- enable PrivateTmp in service file (#781440)
- set LANG=C in /etc/sysconfig/httpd

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.21-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 06 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.21-4
- fix #751591 - start httpd after remote-fs

* Mon Oct 24 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.21-3
- allow change state of BalancerMember in mod_proxy_balancer web interface

* Thu Sep 22 2011 Ville Skyttä <ville.skytta@iki.fi> - 2.2.21-2
- Make mmn available as %%{_httpd_mmn}.
- Add .svgz to AddEncoding x-gzip example in httpd.conf.

* Tue Sep 13 2011 Joe Orton <jorton@redhat.com> - 2.2.21-1
- update to 2.2.21

* Mon Sep  5 2011 Joe Orton <jorton@redhat.com> - 2.2.20-1
- update to 2.2.20
- fix MPM stub man page generation

* Wed Aug 10 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.19-5
- fix #707917 - add httpd-ssl-pass-dialog to ask for SSL password using systemd

* Fri Jul 22 2011 Iain Arnell <iarnell@gmail.com> 1:2.2.19-4
- rebuild while rpm-4.9.1 is untagged to remove trailing slash in provided
  directory names

* Wed Jul 20 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.19-3
- fix #716621 - suexec now works without setuid bit

* Thu Jul 14 2011 Jan Kaluza <jkaluza@redhat.com> - 2.2.19-2
- fix #689091 - backported patch from 2.3 branch to support IPv6 in logresolve

* Fri Jul  1 2011 Joe Orton <jorton@redhat.com> - 2.2.19-1
- update to 2.2.19
- enable dbd, authn_dbd in default config

* Thu Apr 14 2011 Joe Orton <jorton@redhat.com> - 2.2.17-13
- fix path expansion in service files

* Tue Apr 12 2011 Joe Orton <jorton@redhat.com> - 2.2.17-12
- add systemd service files (#684175, thanks to Jóhann B. Guðmundsson)

* Wed Mar 23 2011 Joe Orton <jorton@redhat.com> - 2.2.17-11
- minor updates to httpd.conf
- drop old patches

* Wed Mar  2 2011 Joe Orton <jorton@redhat.com> - 2.2.17-10
- rebuild

* Wed Feb 23 2011 Joe Orton <jorton@redhat.com> - 2.2.17-9
- use arch-specific mmn

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.17-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Joe Orton <jorton@redhat.com> - 2.2.17-7
- generate dummy mod_ssl cert with CA:FALSE constraint (#667841)
- add man page stubs for httpd.event, httpd.worker
- drop distcache support
- add STOP_TIMEOUT support to init script

* Sat Jan  8 2011 Joe Orton <jorton@redhat.com> - 2.2.17-6
- update default SSLCipherSuite per upstream trunk

* Wed Jan  5 2011 Joe Orton <jorton@redhat.com> - 2.2.17-5
- fix requires (#667397)

* Wed Jan  5 2011 Joe Orton <jorton@redhat.com> - 2.2.17-4
- de-ghost /var/run/httpd

* Tue Jan  4 2011 Joe Orton <jorton@redhat.com> - 2.2.17-3
- add tmpfiles.d configuration, ghost /var/run/httpd (#656600)

* Sat Nov 20 2010 Joe Orton <jorton@redhat.com> - 2.2.17-2
- drop setuid bit, use capabilities for suexec binary

* Wed Oct 27 2010 Joe Orton <jorton@redhat.com> - 2.2.17-1
- update to 2.2.17

* Fri Sep 10 2010 Joe Orton <jorton@redhat.com> - 2.2.16-2
- link everything using -z relro and -z now

* Mon Jul 26 2010 Joe Orton <jorton@redhat.com> - 2.2.16-1
- update to 2.2.16

* Fri Jul  9 2010 Joe Orton <jorton@redhat.com> - 2.2.15-3
- default config tweaks:
 * harden httpd.conf w.r.t. .htaccess restriction (#591293)
 * load mod_substitute, mod_version by default
 * drop proxy_ajp.conf, load mod_proxy_ajp in httpd.conf
 * add commented list of shipped-but-unloaded modules
 * bump up worker defaults a little
 * drop KeepAliveTimeout to 5 secs per upstream
- fix LSB compliance in init script (#522074)
- bundle NOTICE in -tools
- use init script in logrotate postrotate to pick up PIDFILE
- drop some old Obsoletes/Conflicts

* Sun Apr 04 2010 Robert Scheck <robert@fedoraproject.org> - 2.2.15-1
- update to 2.2.15 (#572404, #579311)

