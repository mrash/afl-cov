#!/bin/sh
#
# easy wrapper script for afl-cov
#
test "$1" = "-h" -o -z "$1" && { 
  echo "Syntax: $0 [-v] [-c] out-dir \"exec cmd --foo @@\""
  echo
  echo Generates the coverage information for an AFL run.
  echo Must be run from the top directory of the coverage build.
  echo The -v option enables verbose output.
  echo The option -c specifies that clang was used for the coverage build
  echo
  echo Example: $0 ../target/out \"tools/target @@\"
  exit 1
}

test "$1" = "-v" && { OPT1="-v" ; shift ; }
test "$1" = "-c" && { OPT2="--clang" ; shift ; }
test "$1" = "-v" && { OPT1="-v" ; shift ; }

test -d "$1" || { echo Error: not a directory: $1 ; exit 1 ; } 


DST=`realpath "$1"`
test -e "$DST"/queue || {
  DST="$DST/default"
  test -e "$DST"/queue || {
    echo Error: not an afl-fuzz -o out directory
    exit 1
  }
}

HOMEPATH=`dirname $0`
export PATH="$HOMEPATH:$PATH"

afl-cov $OPT1 $OPT2 -d "$DST" --cover-corpus --coverage-cmd "$2" --code-dir . --overwrite

test -e "$1"/fuzzer_stats && {
  DIFF=$(expr `grep last_update "$DST"/fuzzer_stats|awk '{print$3}'` - `grep start_time "$DST"/fuzzer_stats|awk '{print$3}'`)
  echo "runtime           : $DIFF seconds"
  TIME=`date -u -d "@$SECONDS" +"%T"`
  echo "run_clock         : $TIME"
  grep -E 'execs_done|paths_total|^unique_|stability' "$DST"/fuzzer_stats
  LINES=
  test -e "$1"/cov/afl-cov.log && LINES=`grep -w lines "$1"/cov/afl-cov.log|tail -n 1|sed 's/.*(//'|sed 's/ .*//'`
  echo "coverage          : $LINES lines"
} | tee "$1"/stats.out

echo open "file://$DST/cov/web/index.html"
