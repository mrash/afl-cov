#!/bin/sh -x

CODE_DIR=./fwknop-codecov.git
AFL_COV=../afl-cov
AFL_TEST_CASES=./afl/e3ae6747/server-access-parallel.out

echo "[+] server-access-parallel"
$AFL_COV -d $AFL_TEST_CASES --coverage-cmd "LD_LIBRARY_PATH=$CODE_DIR/lib/.libs $CODE_DIR/server/.libs/fwknopd -c $CODE_DIR/test/conf/ipt_snat_fwknopd.conf -a AFL_FILE -O $CODE_DIR/test/conf/override_no_digest_tracking_fwknopd.conf -f -t --exit-parse-config -v -v -v -r `pwd`" --code-dir $CODE_DIR $@

exit 0
