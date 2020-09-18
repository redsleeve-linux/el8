#!/bin/sh
#
# This script will initialise token storage of softhsm PKCS11 provider
# in custom location. Is useful to store tokens in non-standard location.

SOFTHSM2_CONF="$1"
TOKENPATH="$2"
GROUPNAME="$3"
# Do not use this script for real keys worth protection
# This is intended for crypto accelerators using PKCS11 interface.
# Uninitialized token would fail any crypto operation.
PIN=1234

set -e

if [ -z "$SOFTHSM2_CONF" -o -z "$TOKENPATH" ]; then
	echo "Usage: $0 <config file> <token directory> [group]" >&2
	exit 1
fi

if ! [ -f "$SOFTHSM2_CONF" ]; then
cat  << SED > "$SOFTHSM2_CONF"
# SoftHSM v2 configuration file

directories.tokendir = ${TOKENPATH}
objectstore.backend = file

# ERROR, WARNING, INFO, DEBUG
log.level = ERROR

# If CKF_REMOVABLE_DEVICE flag should be set
slots.removable = false
SED
else
	echo "Config file $SOFTHSM2_CONF already exists" >&2
fi

[ -d "$TOKENPATH" ] || mkdir -p "$TOKENPATH"

export SOFTHSM2_CONF

if softhsm2-util --show-slots | grep 'Initialized:[[:space:]]*yes' > /dev/null
then
	echo "Token in ${TOKENPATH} is already initialized" >&2
else
	echo "Initializing tokens to ${TOKENPATH}..."
	softhsm2-util --init-token --free --label rpm --pin $PIN --so-pin $PIN

	if [ -n "$GROUPNAME" ]; then
		chgrp -R -- "$GROUPNAME" "$TOKENPATH"
		chmod -R -- g=rX,o= "$TOKENPATH"
	fi
fi

echo "export SOFTHSM2_CONF=\"$SOFTHSM2_CONF\""
