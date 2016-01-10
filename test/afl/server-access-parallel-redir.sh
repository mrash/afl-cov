#!/bin/sh

#
# Parallel fuzzing for the fwknopd access.conf file. This script
# requires multiple invocations, the first with something like
# '-M fuzzer01' and all subsequent instances with '-S fuzzer02', etc.
#

. ./fuzzing-wrappers/fcns

FDIR="server-access.out"
OUT_DIR="$TOP_DIR/$FDIR"
PREV_OUT_DIR=''
IN_DIR="test-cases/server-access"
FUZZ_FILE=$OUT_DIR/afl_access.conf

### build up our afl-fuzz text banner
TSTR="fwknopd,access.conf"
GIT_STR=''
git_banner GIT_STR
BANNER="$TSTR$GIT_STR"

[ ! -d $OUT_DIR ] && mkdir $OUT_DIR

### run afl-fuzz
LD_LIBRARY_PATH=$LIB_DIR afl-fuzz \
    -m $MEM_LIMIT -T $BANNER -t $TIMEOUT \
    -i $IN_DIR -o $OUT_DIR $@ -f $FUZZ_FILE \
    $SERVER -c ../conf/ipt_snat_fwknopd.conf \
    -a $FUZZ_FILE \
    -O ../conf/override_no_digest_tracking_fwknopd.conf \
    -A -f -t --exit-parse-config -v -v -v -r `pwd`/run > /dev/null

exit $?
