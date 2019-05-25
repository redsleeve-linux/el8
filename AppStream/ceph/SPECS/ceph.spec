# vim: set noexpandtab ts=8 sw=8 :
#
# spec file for package ceph
#
# Copyright (C) 2004-2017 The Ceph Project Developers. See COPYING file
# at the top-level directory of this distribution and at
# https://github.com/ceph/ceph/blob/master/COPYING
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon.
#
# This file is under the GNU Lesser General Public License, version 2.1
#
# Please submit bugfixes or comments via http://tracker.ceph.com/
#
%global _hardened_build 1

%bcond_with ocf
%bcond_with tcmalloc
%bcond_with lowmem_builder
%bcond_with lttng

%{!?_udevrulesdir: %global _udevrulesdir /lib/udev/rules.d}
%{!?tmpfiles_create: %global tmpfiles_create systemd-tmpfiles --create}
%{!?python3_pkgversion: %global python3_pkgversion 3}

# unify libexec for all targets
%global _libexecdir %{_exec_prefix}/lib

# disable dwz which compresses the debuginfo
%global _find_debuginfo_dwz_opts %{nil}

%if ( 0%{?rhel} && 0%{?rhel} < 7 )
%global _rundir %{_localstatedir}/run
%else
%global _rundir /run
%endif

#################################################################################
# main package definition
#################################################################################
Name:		ceph
Version:	12.2.7
Release:	9%{?dist}
%if 0%{?fedora} || 0%{?rhel}
Epoch:		1
%endif

# define %%_epoch_prefix macro which will expand to the empty string if %%epoch is undefined
%global _epoch_prefix %{?epoch:%{epoch}:}

Summary:	User space components of the Ceph file system
License:	LGPL-2.1 and CC-BY-SA-1.0 and GPL-2.0 and BSL-1.0 and BSD-3-Clause and MIT
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
URL:		http://ceph.com/
Source0:	http://download.ceph.com/tarballs/%{name}-%{version}.tar.gz
# https://bugzilla.redhat.com/show_bug.cgi?id=1474773
Patch001:	0001-src-rocksdb-util-murmurhash.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1474774
Patch002:	0002-cmake-Support-ppc64.patch
Patch003:	0003-librbd-Conditionally-import-TrimRequest.cc.patch
Patch004:	0004-mount-Enlarge-buffer-to-fix-overflow-warning.patch
Patch005:	0005-Disable-rocksdb-Werror.patch
Patch006:	0006-python-to-python3.patch
Patch007:	0007-Strip-away-python2.patch
Patch008:	0008-Fix-python-executable.patch
%if 0%{?suse_version}
%if 0%{?is_opensuse}
ExclusiveArch:	x86_64 aarch64 ppc64 ppc64le
%else
ExclusiveArch:	x86_64 aarch64 ppc64le s390x
%endif
%endif
#################################################################################
# dependencies that apply across all distro families
#################################################################################
BuildRequires:	bc
BuildRequires:	gperf
BuildRequires:  cmake
BuildRequires:	cryptsetup
BuildRequires:	fuse-devel
BuildRequires:	gcc-c++
BuildRequires:	gdbm
%if 0%{with tcmalloc}
BuildRequires:	gperftools-devel >= 2.4
%endif
BuildRequires:	libaio-devel
BuildRequires:	libblkid-devel >= 2.17
BuildRequires:	libcurl-devel
BuildRequires:	libudev-devel
BuildRequires:	libtool
BuildRequires:	libxml2-devel
BuildRequires:	make
BuildRequires:	parted
BuildRequires:	perl
BuildRequires:	pkgconfig
BuildRequires:	python3
BuildRequires:	python3-devel
BuildRequires:	python3-nose
BuildRequires:	python3-requests
BuildRequires:	snappy-devel
BuildRequires:	udev
BuildRequires:	util-linux
%ifarch %{valgrind_arches}
BuildRequires:	valgrind-devel
%endif
BuildRequires:	which
BuildRequires:	xfsprogs
BuildRequires:	xfsprogs-devel

#################################################################################
# distro-conditional dependencies
#################################################################################
BuildRequires:  boost-random
BuildRequires:  boost-devel
BuildRequires:	nss-devel
BuildRequires:	keyutils-libs-devel
# RDMA is no longer built on 32-bit ARM: see #1484155
%ifnarch %{arm}
BuildRequires:	rdma-core-devel
%endif
BuildRequires:  openldap-devel
BuildRequires:  openssl-devel
BuildRequires:  redhat-lsb-core
BuildRequires:	python3-prettytable
BuildRequires:	python3-sphinx
BuildRequires:	python3-devel
BuildRequires:	python3-setuptools
BuildRequires:	python3-Cython
# lttng and babeltrace for rbd-replay-prep
%if %{with lttng}
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	lttng-ust-devel
BuildRequires:	libbabeltrace-devel
%endif
%if 0%{?suse_version}
BuildRequires:	lttng-ust-devel
BuildRequires:  babeltrace-devel
%endif
%endif
%if 0%{?suse_version}
BuildRequires:	libexpat-devel
%endif
%if 0%{?rhel} || 0%{?fedora}
BuildRequires:	expat-devel
%endif
#hardened-cc1
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:  redhat-rpm-config
%endif

%description
Ceph is a massively scalable, open-source, distributed storage system that runs
on commodity hardware and delivers object, block and file system storage.


#################################################################################
# subpackages
#################################################################################

%package -n ceph-common
Summary:	Ceph Common
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	python3-rados = %{_epoch_prefix}%{version}-%{release}
Requires:	python3-rbd = %{_epoch_prefix}%{version}-%{release}
Requires:	python3-cephfs = %{_epoch_prefix}%{version}-%{release}
Requires:	python3-prettytable
Requires:	python3-requests
%{?systemd_requires}
%description -n ceph-common
Common utilities to mount and interact with a ceph storage cluster.
Comprised of files that are common to Ceph clients and servers.

%if %{with ocf}
%package resource-agents
Summary:	OCF-compliant resource agents for Ceph daemons
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}
Requires:	resource-agents
%description resource-agents
Resource agents for monitoring and managing Ceph daemons
under Open Cluster Framework (OCF) compliant resource
managers such as Pacemaker.
%endif

%package -n librados2
Summary:	RADOS distributed object store client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-libs-compat < %{_epoch_prefix}%{version}-%{release}
%endif
%description -n librados2
RADOS is a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to access the distributed object
store using a simple file-like interface.

%package -n librados-devel
Summary:	RADOS headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	librados2-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	librados2-devel < %{_epoch_prefix}%{version}-%{release}
%description -n librados-devel
This package contains libraries and headers needed to develop programs
that use RADOS object store.

%package -n python%{python3_pkgversion}-rados
Summary:	Python 3 libraries for the RADOS object store
%if 0%{?suse_version}
Group:		Development/Languages/Python
%endif
Requires:	%{__python3}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-rados
This package contains Python 3 libraries for interacting with Cephs RADOS
object store.

%package -n libradosstriper1
Summary:       RADOS striping interface
%if 0%{?suse_version}
Group:         System/Libraries
%endif
Requires:      librados2 = %{_epoch_prefix}%{version}-%{release}
%description -n libradosstriper1
Striping interface built on top of the rados library, allowing
to stripe bigger objects onto several standard rados objects using
an interface very similar to the rados one.

%package -n libradosstriper-devel
Summary:       RADOS striping interface headers
%if 0%{?suse_version}
Group:         Development/Libraries/C and C++
%endif
Requires:      libradosstriper1 = %{_epoch_prefix}%{version}-%{release}
Requires:      librados-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:     ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:      libradosstriper1-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:     libradosstriper1-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libradosstriper-devel
This package contains libraries and headers needed to develop programs
that use RADOS striping interface.

%package -n librbd1
Summary:	RADOS block device client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%if 0%{?suse_version}
Requires(post): coreutils
%endif
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-libs-compat < %{_epoch_prefix}%{version}-%{release}
%endif
%description -n librbd1
RBD is a block device striped across multiple distributed objects in
RADOS, a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to manage these block devices.

%package -n librbd-devel
Summary:	RADOS block device headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	librbd1-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	librbd1-devel < %{_epoch_prefix}%{version}-%{release}
%description -n librbd-devel
This package contains libraries and headers needed to develop programs
that use RADOS block device.

%package -n python%{python3_pkgversion}-rbd
Summary:	Python 3 libraries for the RADOS block device
%if 0%{?suse_version}
Group:		Development/Languages/Python
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-rbd
This package contains Python 3 libraries for interacting with Cephs RADOS
block device.

%package -n libcephfs2
Summary:	Ceph distributed file system client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Obsoletes:	libcephfs1
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-libs-compat < %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-libcephfs
%endif
%description -n libcephfs2
Ceph is a distributed network file system designed to provide excellent
performance, reliability, and scalability. This is a shared library
allowing applications to access a Ceph distributed file system via a
POSIX-like interface.

%package -n libcephfs-devel
Summary:	Ceph distributed file system headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	libcephfs2-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	libcephfs2-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libcephfs-devel
This package contains libraries and headers needed to develop programs
that use Cephs distributed file system.

%package -n python%{python3_pkgversion}-cephfs
Summary:	Python 3 libraries for Ceph distributed file system
%if 0%{?suse_version}
Group:		Development/Languages/Python
%endif
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-cephfs
This package contains Python 3 libraries for interacting with Cephs distributed
file system.

#################################################################################
# common
#################################################################################
%prep
%autosetup -p1 -n %{name}-%{version}

%build
%if %{with lowmem_builder}
RPM_OPT_FLAGS="$RPM_OPT_FLAGS --param ggc-min-expand=20 --param ggc-min-heapsize=32768"
%endif
%ifnarch armv7hl
export RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/i386/i486/'`
%else
export RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e 's/i386/i486/' -e 's/-pipe//g'`
%endif

export CPPFLAGS="$java_inc"
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="$RPM_LD_FLAGS"

env | sort

%if %{with lowmem_builder}
%ifnarch armv7hl
%if 0%{?jobs} > 8
%define _smp_mflags -j8
%endif
%else
%define _smp_mflags -j1
%endif
%endif

# unlimit _smp_mflags in system macro if not set above
# Brew cannot handle -j24 here
%define _smp_ncpus_max 16
# extract the number of processors for use with cmake
%define _smp_ncpus %(echo %{_smp_mflags} | sed 's/-j//')

mkdir build
cd build
cmake .. \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DCMAKE_INSTALL_LIBEXECDIR=%{_libexecdir} \
    -DCMAKE_INSTALL_LOCALSTATEDIR=%{_localstatedir} \
    -DCMAKE_INSTALL_SYSCONFDIR=%{_sysconfdir} \
    -DCMAKE_INSTALL_MANDIR=%{_mandir} \
    -DCMAKE_INSTALL_DOCDIR=%{_docdir}/ceph \
    -DCMAKE_INSTALL_INCLUDEDIR=%{_includedir} \
    -DWITH_MGR=OFF \
    -DWITH_EMBEDDED=OFF \
    -DWITH_MANPAGE=ON \
    -DWITH_PYTHON3=ON \
    -DWITH_SYSTEMD=ON \
    -DWITH_SYSTEM_BOOST=ON \
    -DWITH_SPDK=OFF \
    -DWITH_PMEM=OFF \
    -DWITH_BLUESTORE=OFF \
    -DWITH_BOOST_CONTEXT=OFF \
    -DWITH_LEVELDB=OFF \
    -DWITH_RADOSGW=OFF \
%if ( ( 0%{?rhel} && 0%{?rhel} <= 7) && ! 0%{?centos} )
    -DWITH_SUBMAN=ON \
%endif
    -DWITH_TESTS=OFF \
%if %{with lttng}
    -DWITH_LTTNG=ON \
    -DWITH_BABELTRACE=ON \
%else
    -DWITH_LTTNG=OFF \
    -DWITH_BABELTRACE=OFF \
%endif
    $CEPH_EXTRA_CMAKE_ARGS \
%if 0%{with ocf}
    -DWITH_OCF=ON \
%endif
%ifarch aarch64 armv7hl mips mipsel ppc ppc64 ppc64le %{ix86} x86_64
    -DWITH_RADOSGW_BEAST_FRONTEND=ON \
%else
    -DWITH_RADOSGW_BEAST_FRONTEND=OFF \
%endif
%ifnarch %{arm}
    -DWITH_RDMA=OFF \
%endif
    -DBOOST_J=%{_smp_ncpus}

make %{?_smp_mflags}


%install
pushd build
make DESTDIR=%{buildroot} install
# we have dropped sysvinit bits
rm -f %{buildroot}/%{_sysconfdir}/init.d/ceph
popd
install -m 0644 -D src/etc-rbdmap %{buildroot}%{_sysconfdir}/ceph/rbdmap
install -m 0644 -D systemd/ceph.tmpfiles.d %{buildroot}%{_tmpfilesdir}/ceph-common.conf
mkdir -p %{buildroot}%{_sbindir}
chmod 0644 %{buildroot}%{_docdir}/ceph/sample.ceph.conf
install -m 0644 -D COPYING %{buildroot}%{_docdir}/ceph/COPYING

# firewall templates and /sbin/mount.ceph symlink
%if 0%{?suse_version}
mkdir -p %{buildroot}/sbin
ln -sf %{_sbindir}/mount.ceph %{buildroot}/sbin/mount.ceph
%endif

# udev rules
install -m 0644 -D udev/50-rbd.rules %{buildroot}%{_udevrulesdir}/50-rbd.rules

#set up placeholder directories
mkdir -p %{buildroot}%{_sysconfdir}/ceph
mkdir -p %{buildroot}%{_rundir}/ceph
mkdir -p %{buildroot}%{_localstatedir}/log/ceph
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph

# Remove the rbd/fuse bits
rm -f %{buildroot}%{_bindir}/ceph-fuse
rm -f %{buildroot}%{_mandir}/man8/ceph-fuse.8*
rm -f %{buildroot}%{_sbindir}/mount.fuse.ceph
rm -f %{buildroot}%{_unitdir}/ceph-fuse@.service
rm -f %{buildroot}%{_unitdir}/ceph-fuse.target
rm -f %{buildroot}%{_bindir}/rbd-fuse
rm -f %{buildroot}%{_mandir}/man8/rbd-fuse.8*

# Remove the ceph-base package
rm -f %{buildroot}%{_bindir}/crushtool
rm -f %{buildroot}%{_bindir}/monmaptool
rm -f %{buildroot}%{_bindir}/osdmaptool
rm -f %{buildroot}%{_bindir}/ceph-run
rm -f %{buildroot}%{_bindir}/ceph-detect-init
rm -f %{buildroot}%{_sbindir}/ceph-create-keys
rm -f %{buildroot}%{_sbindir}/ceph-disk
rm -f %{buildroot}%{_sbindir}/ceph-volume
rm -f %{buildroot}%{_sbindir}/ceph-volume-systemd
rm -f %{buildroot}%{_libexecdir}/ceph/ceph_common.sh
rm -rf %{buildroot}%{_libdir}/rados-classes
rm -f %{buildroot}%{_libdir}/rados-classes/*
rm -rf %{buildroot}%{_libdir}/ceph/erasure-code
rm -f %{buildroot}%{_libdir}/ceph/erasure-code/libec_*.so*
rm -rf %{buildroot}%{_libdir}/ceph/compressor
rm -f %{buildroot}%{_libdir}/ceph/compressor/libceph_*.so*
rm -rf %{buildroot}%{_libdir}/ceph/crypto
rm -f %{buildroot}%{_libdir}/ceph/crypto/libceph_*.so*
rm -f %{buildroot}%{_libdir}/libos_tp.so*
rm -f %{buildroot}%{_libdir}/libosd_tp.so*
rm -f %{buildroot}%{_localstatedir}/adm/fillup-templates/sysconfig.*
rm -f %{buildroot}%{_unitdir}/ceph-disk@.service
rm -f %{buildroot}%{_unitdir}/ceph-volume@.service
rm -f %{buildroot}%{_unitdir}/ceph.target
rm -rf %{buildroot}%{python_sitelib}/ceph_detect_init*
rm -rf %{buildroot}%{python_sitelib}/ceph_disk*
rm -rf %{buildroot}%{python_sitelib}/ceph_volume/*
rm -rf %{buildroot}%{python_sitelib}/ceph_volume-*
rm -f %{buildroot}%{_mandir}/man8/ceph-deploy.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-detect-init.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-create-keys.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-disk.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-volume.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-volume-systemd.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-run.8*
rm -f %{buildroot}%{_mandir}/man8/crushtool.8*
rm -f %{buildroot}%{_mandir}/man8/osdmaptool.8*
rm -f %{buildroot}%{_mandir}/man8/monmaptool.8*

# Remove the ceph-mds package
rm -f %{buildroot}%{_bindir}/ceph-mds
rm -f %{buildroot}%{_mandir}/man8/ceph-mds.8*
rm -f %{buildroot}%{_unitdir}/ceph-mds@.service
rm -f %{buildroot}%{_unitdir}/ceph-mds.target

# Remove the ceph-mgr package
rm -f %{buildroot}%{_bindir}/ceph-mgr
rm -rf %{buildroot}%{_libdir}/ceph/mgr
rm -f %{buildroot}%{_unitdir}/ceph-mgr@.service
rm -f %{buildroot}%{_unitdir}/ceph-mgr.target

# Remove the ceph-mon package
rm -f %{buildroot}%{_bindir}/ceph-mon
rm -f %{buildroot}%{_bindir}/ceph-rest-api
rm -f %{buildroot}%{_mandir}/man8/ceph-mon.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-rest-api.8*
rm -f %{buildroot}%{python3_sitelib}/__pycache__/ceph_rest_api.*
rm -f %{buildroot}%{python3_sitelib}/ceph_rest_api.py*
rm -f %{buildroot}%{_unitdir}/ceph-mon@.service
rm -f %{buildroot}%{_unitdir}/ceph-mon.target

# Remove the ceph-radosgw package
rm -f %{buildroot}%{_bindir}/radosgw
rm -f %{buildroot}%{_bindir}/radosgw-token
rm -f %{buildroot}%{_bindir}/radosgw-es
rm -f %{buildroot}%{_bindir}/radosgw-object-expirer
rm -f %{buildroot}%{_mandir}/man8/radosgw.8*
rm -f %{buildroot}%{_unitdir}/ceph-radosgw@.service
rm -f %{buildroot}%{_unitdir}/ceph-radosgw.target

# Remove the ceph-osd package
rm -f %{buildroot}%{_bindir}/ceph-clsinfo
rm -f %{buildroot}%{_bindir}/ceph-bluestore-tool
rm -f %{buildroot}%{_bindir}/ceph-objectstore-tool
rm -f %{buildroot}%{_bindir}/ceph-osd
rm -f %{buildroot}%{_libexecdir}/ceph/ceph-osd-prestart.sh
#rm -rf %{buildroot}%dir %{_udevrulesdir}
rm -f %{buildroot}%{_mandir}/man8/ceph-clsinfo.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-osd.8*
rm -f %{buildroot}%{_mandir}/man8/ceph-bluestore-tool.8*
rm -f %{buildroot}%{_unitdir}/ceph-osd@.service
rm -f %{buildroot}%{_unitdir}/ceph-osd.target

# Remove debuginfo for server bits
rm -f %{buildroot}/usr/lib/debug/%{_bindir}/ceph-fuse-*
rm -f %{buildroot}/usr/lib/debug/%{_bindir}/rbd-fuse-*

# Remove incorrectly installed man page
rm -f %{buildroot}%{_mandir}/man8/ceph-kvstore-tool.8*

# Make sure radosgw bits do not exist
rm -f %{buildroot}%{_bindir}/radosgw-admin
rm -f %{buildroot}%{_mandir}/man8/radosgw-admin.8*
rm -f %{buildroot}%{_sysconfdir}/bash_completion.d/radosgw-admin

# Remove rbd-mirror
rm -f %{buildroot}%{_bindir}/rbd-mirror
rm -f %{buildroot}%{_mandir}/man8/rbd-mirror.8*
rm -f %{buildroot}%{_unitdir}/ceph-rbd-mirror@.service
rm -f %{buildroot}%{_unitdir}/ceph-rbd-mirror.target

# Remove rbd-nbd
rm -f %{buildroot}%{_bindir}/rbd-nbd
rm -f %{buildroot}%{_mandir}/man8/rbd-nbd.8*

# Remove rados-objclass-devel
rm -f %{buildroot}%{_includedir}/rados/objclass.h

%clean
rm -rf %{buildroot}

#################################################################################
# files and systemd scriptlets
#################################################################################
%files common
%dir %{_docdir}/ceph
%doc %{_docdir}/ceph/sample.ceph.conf
%doc %{_docdir}/ceph/COPYING
%{_bindir}/ceph
%{_bindir}/ceph-authtool
%{_bindir}/ceph-conf
%{_bindir}/ceph-dencoder
%{_bindir}/ceph-rbdnamer
%{_bindir}/ceph-syn
%{_bindir}/ceph-crush-location
%{_bindir}/cephfs-data-scan
%{_bindir}/cephfs-journal-tool
%{_bindir}/cephfs-table-tool
%{_bindir}/rados
%{_bindir}/rbd
%{_bindir}/rbd-replay
%{_bindir}/rbd-replay-many
%{_bindir}/rbdmap
%{_sbindir}/mount.ceph
%if 0%{?suse_version}
/sbin/mount.ceph
%endif
%if %{with lttng}
%{_bindir}/rbd-replay-prep
%endif
%{_bindir}/ceph-post-file
%{_bindir}/ceph-brag
%{_tmpfilesdir}/ceph-common.conf
%{_mandir}/man8/ceph-authtool.8*
%{_mandir}/man8/ceph-conf.8*
%{_mandir}/man8/ceph-dencoder.8*
%{_mandir}/man8/ceph-rbdnamer.8*
%{_mandir}/man8/ceph-syn.8*
%{_mandir}/man8/ceph-post-file.8*
%{_mandir}/man8/ceph.8*
%{_mandir}/man8/mount.ceph.8*
%{_mandir}/man8/rados.8*
%{_mandir}/man8/rbd.8*
%{_mandir}/man8/rbdmap.8*
%{_mandir}/man8/rbd-replay.8*
%{_mandir}/man8/rbd-replay-many.8*
%{_mandir}/man8/rbd-replay-prep.8*
%dir %{_datadir}/ceph/
%{_datadir}/ceph/known_hosts_drop.ceph.com
%{_datadir}/ceph/id_rsa_drop.ceph.com
%{_datadir}/ceph/id_rsa_drop.ceph.com.pub
%dir %{_sysconfdir}/ceph/
%config %{_sysconfdir}/bash_completion.d/ceph
%config %{_sysconfdir}/bash_completion.d/rados
%config %{_sysconfdir}/bash_completion.d/rbd
%config(noreplace) %{_sysconfdir}/ceph/rbdmap
%{_unitdir}/rbdmap.service
%{python3_sitelib}/ceph_argparse.py*
%{python3_sitelib}/__pycache__/ceph_argparse.cpython*.py*
%{python3_sitelib}/ceph_daemon.py*
%{python3_sitelib}/__pycache__/ceph_daemon.cpython*.py*
%dir %{_udevrulesdir}
%{_udevrulesdir}/50-rbd.rules
%attr(3770,ceph,ceph) %dir %{_localstatedir}/log/ceph/
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/

%pre common
CEPH_GROUP_ID=167
CEPH_USER_ID=167
%if 0%{?rhel} || 0%{?fedora}
/usr/sbin/groupadd ceph -g $CEPH_GROUP_ID -o -r 2>/dev/null || :
/usr/sbin/useradd ceph -u $CEPH_USER_ID -o -r -g ceph -s /sbin/nologin -c "Ceph daemons" -d %{_localstatedir}/lib/ceph 2>/dev/null || :
%endif
%if 0%{?suse_version}
if ! getent group ceph >/dev/null ; then
    CEPH_GROUP_ID_OPTION=""
    getent group $CEPH_GROUP_ID >/dev/null || CEPH_GROUP_ID_OPTION="-g $CEPH_GROUP_ID"
    groupadd ceph $CEPH_GROUP_ID_OPTION -r 2>/dev/null || :
fi
if ! getent passwd ceph >/dev/null ; then
    CEPH_USER_ID_OPTION=""
    getent passwd $CEPH_USER_ID >/dev/null || CEPH_USER_ID_OPTION="-u $CEPH_USER_ID"
    useradd ceph $CEPH_USER_ID_OPTION -r -g ceph -s /sbin/nologin 2>/dev/null || :
fi
usermod -c "Ceph storage service" \
        -d %{_localstatedir}/lib/ceph \
        -g ceph \
        -s /sbin/nologin \
        ceph
%endif
exit 0

%post common
%tmpfiles_create %{_tmpfilesdir}/ceph-common.conf

%postun common
# Package removal cleanup
if [ "$1" -eq "0" ] ; then
    rm -rf %{_localstatedir}/log/ceph
    rm -rf %{_sysconfdir}/ceph
fi

%if %{with ocf}

%files resource-agents
%dir %{_prefix}/lib/ocf
%dir %{_prefix}/lib/ocf/resource.d
%dir %{_prefix}/lib/ocf/resource.d/ceph
%{_prefix}/lib/ocf/resource.d/ceph/rbd

%endif

%files -n librados2
%{_libdir}/librados.so.*
%dir %{_libdir}/ceph
%{_libdir}/ceph/libceph-common.so*
%if %{with lttng}
%{_libdir}/librados_tp.so.*
%endif

%post -n librados2 -p /sbin/ldconfig

%postun -n librados2 -p /sbin/ldconfig

%files -n librados-devel
%dir %{_includedir}/rados
%{_includedir}/rados/librados.h
%{_includedir}/rados/librados.hpp
%{_includedir}/rados/buffer.h
%{_includedir}/rados/buffer_fwd.h
%{_includedir}/rados/inline_memory.h
%{_includedir}/rados/page.h
%{_includedir}/rados/crc32c.h
%{_includedir}/rados/rados_types.h
%{_includedir}/rados/rados_types.hpp
%{_includedir}/rados/memory.h
%{_libdir}/librados.so
%if %{with lttng}
%{_libdir}/librados_tp.so
%endif
%{_bindir}/librados-config
%{_mandir}/man8/librados-config.8*

%files -n python%{python3_pkgversion}-rados
%{python3_sitearch}/rados.cpython*.so
%{python3_sitearch}/rados-*.egg-info

%files -n libradosstriper1
%{_libdir}/libradosstriper.so.*

%post -n libradosstriper1 -p /sbin/ldconfig

%postun -n libradosstriper1 -p /sbin/ldconfig

%files -n libradosstriper-devel
%dir %{_includedir}/radosstriper
%{_includedir}/radosstriper/libradosstriper.h
%{_includedir}/radosstriper/libradosstriper.hpp
%{_libdir}/libradosstriper.so

%files -n librbd1
%{_libdir}/librbd.so.*
%if %{with lttng}
%{_libdir}/librbd_tp.so.*
%endif

%post -n librbd1 -p /sbin/ldconfig

%postun -n librbd1 -p /sbin/ldconfig

%files -n librbd-devel
%dir %{_includedir}/rbd
%{_includedir}/rbd/librbd.h
%{_includedir}/rbd/librbd.hpp
%{_includedir}/rbd/features.h
%{_libdir}/librbd.so
%if %{with lttng}
%{_libdir}/librbd_tp.so
%endif

%files -n python%{python3_pkgversion}-rbd
%{python3_sitearch}/rbd.cpython*.so
%{python3_sitearch}/rbd-*.egg-info

%files -n libcephfs2
%{_libdir}/libcephfs.so.*

%post -n libcephfs2 -p /sbin/ldconfig

%postun -n libcephfs2 -p /sbin/ldconfig

%files -n libcephfs-devel
%dir %{_includedir}/cephfs
%{_includedir}/cephfs/libcephfs.h
%{_includedir}/cephfs/ceph_statx.h
%{_libdir}/libcephfs.so

%files -n python%{python3_pkgversion}-cephfs
%{python3_sitearch}/cephfs.cpython*.so
%{python3_sitearch}/cephfs-*.egg-info
%{python3_sitelib}/ceph_volume_client.py
%{python3_sitelib}/__pycache__/ceph_volume_client.cpython*.py*


%changelog
* Wed Oct 03 2018 Boris Ranto <branto@redhat.com> - 1:12.2.7-9
- fix link-time hardening (1630554)

* Tue Sep 25 2018 Boris Ranto <branto@redhat.com> - 1:12.2.7-8
- do not require yasm
- strip away crypto implementations

* Wed Sep 19 2018 Tomas Orsava <torsava@redhat.com> - 1:12.2.7-7
- Require the Python interpreter directly instead of using the package name
- Related: rhbz#1619153

* Fri Sep 14 2018 Boris Ranto <branto@redhat.com> - 1:12.2.7-6
- Drop ceph-resource-agents

* Wed Sep 12 2018 Boris Ranto <branto@redhat.com> - 1:12.2.7-5
- Reintroduce libradosstriper for /usr/bin/rados binary

* Fri Aug  3 2018 Florian Weimer <fweimer@redhat.com> - 1:12.2.7-4
- Honor %%{valgrind_arches}

* Mon Jul 30 2018 Florian Weimer <fweimer@redhat.com> - 1:12.2.7-3
- Rebuild with fixed binutils

* Wed Jul 25 2018 Petr Kubat <pkubat@redhat.com> - 1:12.2.7-2
- Rebuilt for gdbm

* Tue Jul 17 2018 Boris Ranto <branto@redhat.com> - 2:12.2.7-1
- Rebase to latest luminous

* Fri Jul 13 2018 Boris Ranto <branto@redhat.com> - 2:12.2.6-1
- Rebase to fix the recent ceph CVEs

* Fri Jun 22 2018 Boris Ranto <branto@redhat.com> - 2:12.2.5-5
- Remove virtualenv dependency

* Wed Jun 20 2018 Boris Ranto <branto@redhat.com> - 2:12.2.5-4
- Strip away xmlstarlet

* Wed Jun 06 2018 Boris Ranto <branto@redhat.com> - 2:12.2.5-3
- Strip away further dependencies
- Remove more packages
- Strip sourca tarball from boost sources

* Wed May 30 2018 Boris Ranto <branto@redhat.com> - 2:12.2.5-2
- Strip out btrfs-progs

* Tue May 22 2018 Boris Ranto <branto@redhat.com> - 2:12.2.5-1
- update to latest luminous release

* Tue May 01 2018 Boris Ranto <branto@redhat.com> - 2:12.2.2-3
- clean-up the spec file
- remove old dependencies
- enable ocf build

* Mon Apr 30 2018 Boris Ranto <branto@redhat.com> - 1:12.2.2-2
- Strip away unnecessary packages

* Tue Dec 5 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.2-1
- New release (1:12.2.2-1)
- Fix build error on arm

* Thu Oct 05 2017 Boris Ranto <branto@redhat.com> - 1:12.2.1-2
- Obsolete ceph-libs-compat package

* Wed Sep 27 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.1-1
- New release (1:12.2.1-1)

* Tue Aug 29 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.0-1
- New release (1:12.2.0-1)

* Thu Aug 24 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-5
- libibverbs(-devel) is superceded by rdma-core(-devel), again

* Thu Aug 24 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-4
- libibverbs(-devel) is superceded by rdma-core(-devel)

* Tue Aug 22 2017 Adam Williamson <awilliam@redhat.com> - 1:12.1.4-3
- Disable RDMA support on 32-bit ARM (#1484155)

* Thu Aug 17 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-2
- fix %%epoch in comment, ppc64le lowmem_builder

* Wed Aug 16 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-1
- New release (1:12.1.4-1)

* Sat Aug 12 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.3-1
- New release (1:12.1.3-1)

* Fri Aug 11 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-3
- rebuild with librpm.so.7

* Thu Aug 10 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-2
- Fix 32-bit alignment

* Thu Aug 3 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-1
- New release (1:12.1.2-1)

* Tue Aug 1 2017 Boris Ranto <branto@redhat.com> - 1:12.1.1-8
- Fix ppc64 build

* Tue Aug 1 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-7
- python34 and other nits
- still no fix for ppc64

* Sun Jul 30 2017 Florian Weimer <fweimer@redhat.com> - 1:12.1.1-6
- Reenable ppc64le, with binutils fix for ppc64le (#1475636)

* Fri Jul 28 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-5
- ppc64le disabled until bz #1475636 resolution

* Fri Jul 28 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-4
- 12.1.1 w/ hacks for armv7hl: low mem, no java jni
- WTIH_BABELTRACE -> WITH_BABELTRACE for all archs
- still no fix for ppc64

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:12.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Jul 22 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-2
- 12.1.1 w/ rocksdb patch (i686)

* Sat Jul 22 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-1
- New release (1:12.1.1-1)

* Fri Jul 21 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-0
- New release (1:12.1.1-0)

* Fri Jul 21 2017 Kalev Lember <klember@redhat.com> - 1:10.2.7-3
- Rebuilt for Boost 1.64

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.2.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Mon Apr 17 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:10.2.7-1
- New release (1:10.2.7-1)

* Wed Feb 08 2017 Boris Ranto <branto@redhat.com> - 1:10.2.5-2
- New release (1:10.2.5-2)

* Fri Jan 13 2017 Boris Ranto <branto@redhat.com> - 1:10.2.5-1
- New release (1:10.2.5-1)
- hack: do not test for libxfs, assume it is present

* Wed Dec 14 2016 Boris Ranto <branto@redhat.com> - 1:10.2.4-2
- New version (1:10.2.4-2)
- This syncs up with the upstream 10.2.5
- Doing it this way because of broken lookaside cache
- Fix the -devel obsoletes

* Thu Dec 08 2016 Boris Ranto <branto@redhat.com> - 1:10.2.4-1
- New version (1:10.2.4-1)
- Disable erasure_codelib neon build
- Use newer -devel package format
- Sync up the spec file

* Wed Oct 26 2016 Ken Dreyer <ktdreyer@ktdreyer.com> 1:10.2.3-4
- librgw: add API version defines for librgw and rgw_file

* Wed Oct 26 2016 Ken Dreyer <ktdreyer@ktdreyer.com> 1:10.2.3-3
- update patches style for rdopkg

* Thu Sep 29 2016 Boris Ranto <branto@redhat.com> - 1:10.2.3-2
- New release (1:10.2.3-2)
- common: instantiate strict_si_cast<long> not

* Thu Sep 29 2016 Boris Ranto <branto@redhat.com> - 1:10.2.3-1
- New version (1:10.2.3-1)
- Disable erasure_codelib neon build

* Sun Aug 07 2016 Igor Gnatenko <ignatenko@redhat.com> - 1:10.2.2-4
- Rebuild for LevelDB 1.18

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.2.2-3
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Jun 21 2016 Boris Ranto <branto@redhat.com> - 1:10.2.2-2
- New release (1:10.2.2-2)
- fix tcmalloc handling in spec file

* Mon Jun 20 2016 Boris Ranto <branto@redhat.com> - 1:10.2.2-1
- New version (1:10.2.2-1)
- Disable erasure_codelib neon build
- Do not use -momit-leaf-frame-pointer flag

* Mon May 16 2016 Boris Ranto <branto@redhat.com> - 1:10.2.1-1
- New version (1:10.2.1-1)
- Disable erasure_codelib neon build
- Do not use -momit-leaf-frame-pointer flag

* Fri May 06 2016 Dan Horák <dan[at]danny.cz> - 10.2.0-3
- fix build on s390(x) - gperftools/tcmalloc not available there

* Fri Apr 22 2016 Boris Ranto <branto@redhat.com> - 10.2.0-2
- Do not use -momit-leaf-frame-pointer flag

* Fri Apr 22 2016 Boris Ranto <branto@redhat.com> - -
- Rebase to version 10.2.0
- Disable erasure_codelib neon build

* Mon Apr 11 2016 Richard W.M. Jones <rjones@redhat.com> - 1:9.2.0-5
- Fix large startup times of processes linking to -lrbd.
  Backport upstream commit 1c2831a2, fixes RHBZ#1319483.
- Add workaround for XFS header brokenness.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:9.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 14 2016 Jonathan Wakely <jwakely@redhat.com> - 1:9.2.0-3
- Rebuilt for Boost 1.60

* Mon Dec 14 2015 Dan Horák <dan[at]danny.cz> - 1:9.2.0-2
- fix build on s390(x) - gperftools/tcmalloc not available there

* Tue Nov 10 2015 Boris Ranto <branto@redhat.com> - 1:9.2.0-1
- Rebase to latest stable upstream version (9.2.0 - infernalis)
- Use upstream spec file

* Tue Oct 27 2015 Boris Ranto <branto@redhat.com> - 1:0.94.5-1
- Rebase to latest upstream version

* Tue Oct 20 2015 Boris Ranto <branto@redhat.com> - 1:0.94.4-1
- Rebase to latest upstream version
- The rtdsc patch got merged upstream and is already present in the release

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 1:0.94.3-2
- Rebuilt for Boost 1.59

* Thu Aug 27 2015 Boris Ranto <branto@redhat.com> - 1:0.94.3-1
- Rebase to latest upstream version
- The boost patch got merged upstream and is already present in the release

* Fri Jul 31 2015 Richard W.M. Jones <rjones@redhat.com> - 1:0.94.2-4
- Fix build against boost 1.58 (http://tracker.ceph.com/issues/11576).

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.94.2-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 1:0.94.2-2
- rebuild for Boost 1.58

* Thu Jul 16 2015 Boris Ranto <branto@redhat.com> - 1:0.94.2-1
- Rebase to latest upstream version

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.94.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 Dan Horák <dan[at]danny.cz> - 1:0.94.1-4
- fix build on s390(x) - no gperftools there

* Thu May 21 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-3
- Disable lttng support (rhbz#1223319)

* Mon May 18 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-2
- Fix arm linking issue (rhbz#1222286)

* Tue Apr 14 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-1
- Rebase to latest upstream version and sync-up the spec file
- Add arm compilation patches

* Wed Apr 01 2015 Ken Dreyer <ktdreyer@ktdreyer.com> - 1:0.87.1-3
- add version numbers to Obsoletes (RHBZ #1193182)

* Wed Mar 4 2015 Boris Ranto <branto@redhat.com> - 1:0.87.1-2
- Perform a hardened build
- Use git-formatted patches
- Add patch for pthreads rwlock unlock problem
- Do not remove conf files on uninstall
- Remove the cleanup function, it is only necessary for f20 and f21

* Wed Feb 25 2015 Boris Ranto <branto@redhat.com> - 1:0.87.1-1
- Rebase to latest upstream
- Remove boost patch, it is in upstream tarball
- Build with yasm, tarball contains fix for the SELinux issue

* Thu Jan 29 2015 Petr Machata <pmachata@redhat.com> - 1:0.87-2
- Rebuild for boost 1.57.0
- Include <boost/optional/optional_io.hpp> instead of
  <boost/optional.hpp>.  Keep the old dumping behavior in
  osd/ECBackend.cc (ceph-0.87-boost157.patch)

* Mon Nov 3 2014 Boris Ranto <branto@redhat.com> - 1:0.87-1
- Rebase to latest major version (firefly -> giant)

* Thu Oct 16 2014 Boris Ranto <branto@redhat.com - 1:0.80.7-1
- Rebase to latest upstream version

* Sat Oct 11 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-3
- Fix a typo in librados-devel vs librados2-devel dependency

* Fri Oct 10 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-2
- Provide empty file list for python-ceph-compat and ceph-devel-compat

* Fri Oct 10 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-1
- Rebase to 0.80.6
- Split ceph-devel and python-ceph packages

* Tue Sep 9 2014 Dan Horák <dan[at]danny.cz> - 1:0.80.5-10
- update Requires for s390(x)

* Wed Sep 3 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-9
- Symlink librd.so.1 to /usr/lib64/qemu only on rhel6+ x86_64 (1136811)

* Thu Aug 21 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-8
- Revert the previous change
- Fix bz 1118504, second attempt (yasm appears to be the package that caused this
- Fix bogus dates

* Wed Aug 20 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-7
- Several more merges from file to try to fix the selinux issue (1118504)

* Sun Aug 17 2014 Kalev Lember <kalevlember@gmail.com> - 1:0.80.5-6
- Obsolete ceph-libcephfs

* Sat Aug 16 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-5
- Do not require xfsprogs/xfsprogs-devel for el6
- Require gperftools-devel for non-ppc*/s390* architectures only
- Do not require junit -- no need to build libcephfs-test.jar
- Build without libxfs for el6
- Build without tcmalloc for ppc*/s390* architectures
- Location of mkcephfs must depend on a rhel release
- Use epoch in the Requires fields [1130700]

* Sat Aug 16 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-4
- Use the proper version name in Obsoletes

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.80.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-2
- Add the arm pthread hack

* Fri Aug 15 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-1
- Bump the Epoch, we need to keep the latest stable, not development, ceph version in fedora
- Use the upstream spec file with the ceph-libs split
- Add libs-compat subpackage [1116546]
- use fedora in rhel 7 checks
- obsolete libcephfs [1116614]
- depend on redhat-lsb-core for the initscript [1108696]

* Wed Aug 13 2014 Kalev Lember <kalevlember@gmail.com> - 0.81.0-6
- Add obsoletes to keep the upgrade path working (#1118510)

* Mon Jul 7 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-5
- revert to old spec until after f21 branch

* Fri Jul 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- temporary exclude f21/armv7hl. N.B. it builds fine on f20/armv7hl.

* Fri Jul 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-4
- upstream ceph.spec file

* Tue Jul 1 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-3
- upstream ceph.spec file

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.81.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- el6 ppc64 likewise for tcmalloc, merge from origin/el6

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- el6 ppc64 does not have gperftools, merge from origin/el6

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-1
- ceph-0.81.0

* Wed Jun  4 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.80.1-5
- gperftools now available on aarch64/ppc64

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 0.80.1-4
- Rebuild for boost 1.55.0

* Fri May 23 2014 David Tardon <dtardon@redhat.com> - 0.80.1-3
- rebuild for boost 1.55.0

* Wed May 14 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.80.1-2
- build epel-6
- exclude %%{_libdir}/ceph/erasure-code in base package

* Tue May 13 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.80.1-1
- Update to latest stable upstream release, BZ 1095201
- PIE, _hardened_build, BZ 955174

* Thu Feb 06 2014 Ken Dreyer <ken.dreyer@inktank.com> - 0.72.2-2
- Move plugins from -devel into -libs package (#891993). Thanks Michael
  Schwendt.

* Mon Jan 06 2014 Ken Dreyer <ken.dreyer@inktank.com> 0.72.2-1
- Update to latest stable upstream release
- Use HTTPS for URLs
- Submit Automake 1.12 patch upstream
- Move unversioned shared libs from ceph-libs into ceph-devel

* Wed Dec 18 2013 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> 0.67.3-4
- build without tcmalloc on aarch64 (no gperftools)

* Sat Nov 30 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.67.3-3
- gperftools not currently available on aarch64

* Mon Oct 07 2013 Dan Horák <dan[at]danny.cz> - 0.67.3-2
- fix build on non-x86_64 64-bit arches

* Wed Sep 11 2013 Josef Bacik <josef@toxicpanda.com> - 0.67.3-1
- update to 0.67.3

* Wed Sep 11 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 0.61.7-3
- let base package include all its documentation files via %%doc magic,
  so for Fedora 20 Unversioned Docdirs no files are included accidentally
- include the sample config files again (instead of just an empty docdir
  that has been added for #846735)
- don't include librbd.so.1 also in -devel package (#1003202)
- move one misplaced rados plugin from -devel into -libs package (#891993)
- include missing directories in -devel and -libs packages
- move librados-config into the -devel pkg where its manual page is, too
- add %%_isa to subpackage dependencies
- don't use %%defattr anymore
- add V=1 to make invocation for verbose build output

* Wed Jul 31 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.61.7-2
- re-enable tmalloc on arm now gperftools is fixed

* Mon Jul 29 2013 Josef Bacik <josef@toxicpanda.com> - 0.61.7-1
- Update to 0.61.7

* Sat Jul 27 2013 pmachata@redhat.com - 0.56.4-2
- Rebuild for boost 1.54.0

* Fri Mar 29 2013 Josef Bacik <josef@toxicpanda.com> - 0.56.4-1
- Update to 0.56.4
- Add upstream d02340d90c9d30d44c962bea7171db3fe3bfba8e to fix logrotate

* Wed Feb 20 2013 Josef Bacik <josef@toxicpanda.com> - 0.56.3-1
- Update to 0.56.3

* Mon Feb 11 2013 Richard W.M. Jones <rjones@redhat.com> - 0.53-2
- Rebuilt to try to fix boost dependency problem in Rawhide.

* Thu Nov  1 2012 Josef Bacik <josef@toxicpanda.com> - 0.53-1
- Update to 0.53

* Mon Sep 24 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-3
- Fix automake 1.12 error
- Rebuild after buildroot was messed up

* Tue Sep 18 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-2
- Use system leveldb

* Fri Sep 07 2012 David Nalley <david@gnsa.us> - 0.51-1
- Updating to 0.51
- Updated url and source url.

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.46-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May  9 2012 Josef Bacik <josef@toxicpanda.com> - 0.46-1
- updated to upstream 0.46
- broke out libcephfs (rhbz# 812975)

* Mon Apr 23 2012 Dan Horák <dan[at]danny.cz> - 0.45-2
- fix detection of C++11 atomic header

* Thu Apr 12 2012 Josef Bacik <josef@toxicpanda.com> - 0.45-1
- updating to upstream 0.45

* Wed Apr  4 2012 Niels de Vos <devos@fedoraproject.org> - 0.44-5
- Add LDFLAGS=-lpthread on any ARM architecture
- Add CFLAGS=-DAO_USE_PTHREAD_DEFS on ARMv5tel

* Mon Mar 26 2012 Dan Horák <dan[at]danny.cz> 0.44-4
- gperftools not available also on ppc

* Mon Mar 26 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-3
- Remove unneeded patch

* Sun Mar 25 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-2
- Update to 0.44
- Fix build problems

* Mon Mar  5 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.43-1
- Update to 0.43
- Remove upstreamed compile fixes patch
- Remove obsoleted dump_pop patch

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.41-2
- Rebuilt for c++ ABI breakage

* Thu Feb 16 2012 Tom Callaway <spot@fedoraproject.org> 0.41-1
- update to 0.41
- fix issues preventing build
- rebuild against gperftools

* Sat Dec 03 2011 David Nalley <david@gnsa.us> 0.38-1
- updating to upstream 0.39

* Sat Nov 05 2011 David Nalley <david@gnsa.us> 0.37-1
- create /etc/ceph - bug 745462
- upgrading to 0.37, fixing 745460, 691033
- fixing various logrotate bugs 748930, 747101

* Fri Aug 19 2011 Dan Horák <dan[at]danny.cz> 0.31-4
- google-perftools not available also on s390(x)

* Mon Jul 25 2011 Karsten Hopp <karsten@redhat.com> 0.31-3
- build without tcmalloc on ppc64, BR google-perftools is not available there

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-2
- Remove curl/types.h include since we don't use it anymore

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-1
- Update to 0.31

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26-2
- Add the compile fix patch

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26
- Update to 0.26

* Tue Mar 22 2011 Josef Bacik <josef@toxicpanda.com> 0.25.1-1
- Update to 0.25.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 Steven Pritchard <steve@kspei.com> 0.21.3-1
- Update to 0.21.3.

* Mon Aug 30 2010 Steven Pritchard <steve@kspei.com> 0.21.2-1
- Update to 0.21.2.

* Thu Aug 26 2010 Steven Pritchard <steve@kspei.com> 0.21.1-1
- Update to 0.21.1.
- Sample configs moved to /usr/share/doc/ceph/.
- Added cclass, rbd, and cclsinfo.
- Dropped mkmonfs and rbdtool.
- mkcephfs moved to /sbin.
- Add libcls_rbd.so.

* Tue Jul  6 2010 Josef Bacik <josef@toxicpanda.com> 0.20.2-1
- update to 0.20.2

* Wed May  5 2010 Josef Bacik <josef@toxicpanda.com> 0.20-1
- update to 0.20
- disable hadoop building
- remove all the test binaries properly

* Fri Apr 30 2010 Sage Weil <sage@newdream.net> 0.19.1-5
- Remove java deps (no need to build hadoop by default)
- Include all required librados helpers
- Include fetch_config sample
- Include rbdtool
- Remove misc debugging, test binaries

* Fri Apr 30 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-4
- Add java-devel and java tricks to get hadoop to build

* Mon Apr 26 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-3
- Move the rados and cauthtool man pages into the base package

* Sun Apr 25 2010 Jonathan Dieter <jdieter@lesbg.com> 0.19.1-2
- Add missing libhadoopcephfs.so* to file list
- Add COPYING to all subpackages
- Fix ownership of /usr/lib[64]/ceph
- Enhance description of fuse client

* Tue Apr 20 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-1
- Update to 0.19.1

* Mon Feb  8 2010 Josef Bacik <josef@toxicpanda.com> 0.18-1
- Initial spec file creation, based on the template provided in the ceph src
