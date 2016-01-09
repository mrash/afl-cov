#!/bin/sh

CODE_DIR=./fwknop-codecov.git
AFL_COV=../afl-cov
AFL_TEST_CASES=./fwknop-afl.git/test/afl/fuzzing-output/server-access.out

$AFL_COV --live --sleep 2 --afl-queue-id-limit 3 -d $AFL_TEST_CASES --coverage-cmd "LD_LIBRARY_PATH=$CODE_DIR/lib/.libs $CODE_DIR/server/.libs/fwknopd -c $CODE_DIR/test/conf/ipt_snat_fwknopd.conf -a AFL_FILE -O $CODE_DIR/test/conf/override_no_digest_tracking_fwknopd.conf -f -t --exit-parse-config -v -v -v -r `pwd`" --code-dir $CODE_DIR $@ > /dev/null

exit 0
