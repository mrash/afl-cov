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

Although of no use to AFL itself, the main application of `afl-cov` is to wrap
some automation around gcov and thereby provide data on how to maximize code
coverage with AFL fuzzing runs. Manual interpretation of cumulative gcov
results from AFL test cases is usually still required, but the "fiddly" steps
of iterating over all test cases and generating code coverage reports (along
with the "zero coverage" report) is automated by `afl-cov`.

Producing code coverage data for AFL test cases is an important step to try
and maximize code coverage, and thereby help to maximize the effectiveness of
AFL. For example, some binaries have code that is reachable only after a
complicated (or even cryptographic) test is passed, and AFL may not be able to
exercise this code without taking special measures. These measures commonly
include patching the project code to bypass such tests. (For example, there is
a patch to solve this problem for a CRC test in libpng included in the AFL
sources at `experimental/libpng_no_checksum/libpng-nocrc.patch`.)
When a project implements a patch to assist AFL in reaching code that would
otherwise be inaccessible, a natural question to ask is whether the patch is
effective. Code coverage results can help to verify this.

## Work Flow
The general workflow for `afl-cov` is:

1) Copy the project sources to two different directories
`/path/to/project-fuzzing/` and `/path/to/project-gcov/`. The first
will contain the project binaries compiled for AFL fuzzing, and the second will
contain the project binaries compiled for gcov profiling support. For the
`/path/to/project-gcov/` directory, compile the project with gcov profiling
support (gcc `-fprofile-arcs -ftest-coverage`).

2) Start up `afl-cov` in `--live` mode before also starting the `afl-fuzz`
fuzzing cycle. The command line arguments to `afl-cov` must specify the path to
the output directory used by `afl-fuzz`, and the command to execute along with
associated arguments. This command and arguments should closely resemble the
manner in which `afl-fuzz` executes the targeted binary during the fuzzing
cycle.

Here is an example:

$ cd /path/to/project-gcov/
$ afl-cov -d /path/to/afl-fuzz-output/dir/ --live --coverage-cmd "cat AFL_FILE | LD_LIBRARY_PATH=./lib/.libs ./bin/.libs/somebin -a -b -c" --code-dir .

Note the `AFL_FILE` string above refers to the test case file that AFL will
build in the `queue/` directory under `/path/to/project-fuzz`. Just leave this
string as-is - `afl-cov` will automatically substitute it with each AFL
`queue/id:NNNNNN*` in succession as is builds the code coverage reports.

Also, in the above command, this handles the case where the AFL fuzzing cycle
is fuzzing the targeted binary via stdin. This explains the
`cat AFL_FILE | ... ./bin/.lib/somebin ...` invocation. For the other style of
fuzzing with AFL where a file is read from the filesystem, here is an example:

$ cd /path/to/project-gcov/
$ afl-cov -d /path/to/afl-fuzz-output/dir/ --live --coverage-cmd "LD_LIBRARY_PATH=./lib/.libs ./bin/.libs/somebin -f AFL_FILE -a -b -c" --code-dir .

3) With `afl-cov` running, open a separate terminal/shell, and launch
`afl-fuzz`:

$ cd /path/to/project-fuzzing/
$ LD_LIBRARY_PATH=./lib/.libs afl-fuzz -t 1000 -i ./test-cases/ -o /path/to/afl-fuzz-output/dir/ ./bin/.libs/somebin -a -b -c"

The familiar AFL status screen will be displayed, and `afl-cov` will start
generating code coverage data.

## Example Output

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
