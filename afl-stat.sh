#!/bin/sh
test "$1" = "-h" -o -z "$1" -o -z "$1" && { 
  echo Syntax: $0 out-dir 
  echo "Shows statistics of a run (in progress or done)"
  exit 1
}
test -n "$AFL_PATH" && PATH=$AFL_PATH:$PATH
while [ -n "$1" ]; do
  test -d "$1" || { echo Error: not a directory: $1 ;  } 
  test -e "$1"/fuzzer_stats || { echo Error: not an afl-fuzz -o out directory ;  }
  echo File: `realpath "$1"`
  {
    grep -E 'run_time|execs_done|execs_per_sec|paths_total|^unique_|stability' "$1"/fuzzer_stats
    SECONDS=`grep -E run_time "$1"/fuzzer_stats | awk '{print$3}'`
    test -n "$SECONDS" && {
      DAYS=`expr $SECONDS / 86400`
      SECONDS=`expr $SECONDS % 86400`
      TIME=`date -u -d "@$SECONDS" +"%T"`
      echo "run_clock         : $DAYS:$TIME"
    }
  } | sort | tee "$1"/stats.out
  LINES=
  test -e "$1"/cov/afl-cov.log && {
    LINES=`grep -w lines "$1"/cov/afl-cov.log|tail -n 1|sed 's/.*(//'|sed 's/ .*//'`
    echo "coverage          : $LINES lines" | tee -a "$1"/stats.out
  }
  shift
done
