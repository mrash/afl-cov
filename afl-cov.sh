#!/bin/sh
#
# easy wrapper script for afl-cov
#
test "$1" = "-h" -o -z "$1" && { 
  echo Syntax: $0 out-dir \"exec cmd --foo @@\"
  echo Generates the coverage information for an AFL run.
  echo Must be run from the top directory of the coverage build.
  echo Example: $0 ../target/out \"tools/target @@\"
  exit 1
}
test -d "$1" || { echo Error: not a directory: $1 ; exit 1 ; } 
test -e "$1"/queue || { echo Error: not an afl-fuzz -o out directory ; exit 1 ; }
DST=`realpath "$1"`
afl-cov -v -d "$DST" --cover-corpus --coverage-cmd "$2" --code-dir . --overwrite
test -e "$1"/fuzzer_stats && {
  echo "runtime           :" $(expr `grep last_update "$DST"/fuzzer_stats|awk '{print$3}'` - `grep start_time "$DST"/fuzzer_stats|awk '{print$3}'`) seconds
  egrep 'execs_done|paths_total|^unique_|stability' "$DST"/fuzzer_stats
}
echo open "file://$DST/cov/web/index.html"
