#!/bin/sh -x

CODE_DIR=../fwknop-codecov.git
AFL_COV=../../afl-cov

echo "[+] server-access"
$AFL_COV --overwrite --afl-queue-id-limit 5 -d e3ae6747/server-access.out --coverage-cmd "LD_LIBRARY_PATH=$CODE_DIR/lib/.libs $CODE_DIR/server/.libs/fwknopd -c $CODE_DIR/test/conf/ipt_snat_fwknopd.conf -a AFL_FILE -O $CODE_DIR/test/conf/override_no_digest_tracking_fwknopd.conf -f -t --exit-parse-config -v -v -v -r `pwd`" --code-dir $CODE_DIR

exit 0
