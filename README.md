# afl-cov - AFL Code Coverage

## Introduction
`afl-cov` uses test case files produced by the AFL fuzzer (see:
[http://lcamtuf.coredump.cx/afl/](http://lcamtuf.coredump.cx/afl/) to produce
gcov/lcov code coverage results of the targeted binary. Code coverage is
interpreted from one case to the next by `afl-cov` in order to determine which
new functions and lines are hit by AFL with new test cases. Further, `afl-cov`
allows for specific lines or functions to be searched for within coverage
results, and when a match is found the corresponding test case file is
displayed. This allows the user to discover which AFL test case is the first to
exercise a particular function. In addition, `afl-cov` produces a "zero
coverage" report of functions and lines that were never executed during an AFL
fuzzing run.

Although `afl-cov` is of no use to AFL itself, the main application of
`afl-cov` is to help wrap some automation around gcov and thereby provide data
on how to maximize code coverage with AFL. Manual interpretation of cumulative
gcov results from AFL test cases is usually still required, but the first
"fiddly" step of iterating over all test cases and generating code coverage
reports (along with the "zero coverage" report) is solved by `afl-cov`.

Producing code coverage reports for AFL test cases is an important step to try
and maximize code coverage, and thereby help to maximize the effectiveness of
AFL. For example, some binaries have code that is reachable only after a
complicated (or even cryptographic) test is passed, and AFL may not be able to
exercise such code without taking special measures. For example, a patch to
solve this problem for CRC test in libpng, see the
`experimental/libpng_no_checksum/libpng-nocrc.patch` file in the AFL sources.
Code coverage results can help to verify whether such measures are effective.

## Work Flow
The general work flow for `afl-cov` is:

1) Compile the targeted project with 

2) Start up `afl-cov` in `--live` mode

$ afl-cov -d /tmp/afl-ramdisk/fwknop.git/test/afl/fuzzing-output/spa-pkts.out --live --coverage-cmd "cat AFL_FILE | LD_LIBRARY_PATH=./lib/.libs ./server/.libs/fwknopd -c ./test/conf/default_fwknopd.conf -a ./test/conf/default_access.conf -A -f -t" --code-dir . -v

## Usage Information
Basic `--help` output appears below:

      usage: afl-cov [-h] [-e COVERAGE_CMD] [-d AFL_FUZZING_DIR] [-c CODE_DIR] [-O]
               [--disable-cmd-redirection] [--disable-lcov-web]
               [--disable-coverage-diff] [--disable-coverage-init]
               [--coverage-diff-only] [--live] [--sleep SLEEP]
               [--func-search FUNC_SEARCH] [--line-search LINE_SEARCH]
               [--src-file SRC_FILE] [-v] [-V] [-q]

      optional arguments:
        -h, --help            show this help message and exit
        -e COVERAGE_CMD, --coverage-cmd COVERAGE_CMD
                              set command to exec (including args, and assumes code
                              coverage support)
        -d AFL_FUZZING_DIR, --afl-fuzzing-dir AFL_FUZZING_DIR
                              top level AFL fuzzing directory
        -c CODE_DIR, --code-dir CODE_DIR
                              directory where the code lives (compiled with code
                              coverage support)
        -O, --overwrite       overwrite existing coverage results
        --disable-cmd-redirection
                              disable redirection of command results to /dev/null
        --disable-lcov-web    disable generate of lcov web code coverage reports
        --disable-coverage-diff
                              disable code coverage diff mode
        --disable-coverage-init
                              disable initialization of code coverage counters at
                              afl-cov startup
        --coverage-diff-only  skip running lcov - just show code coverage diffs from
                              previous afl-cov run
        --live                process a live AFL directory, stop with Ctrl-C
        --sleep SLEEP         In --live mode, # of seconds to sleep between checking
                              for new queue files
        --func-search FUNC_SEARCH
                              search for coverage of a specific function
        --line-search LINE_SEARCH
                              search for coverage of a specific line number
                              (requires --src-file)
        --src-file SRC_FILE   restrict function or line search to a specfic source
                              file
        -v, --verbose         verbose mode
        -V, --version         print version and exit
        -q, --quiet           quiet mode

## License
`afl-cov` is released as open source software under the terms of
the **GNU General Public License (GPL v2)**. The latest release can be found
at [https://github.com/mrash/afl-cov/releases](https://github.com/mrash/afl-cov/releases)
