# afl-cov - AFL Fuzzing Code Coverage

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Workflow](#workflow)
  - [Parallelized AFL Execution](#parallelized-afl-execution)
  - [Other Examples](#other-examples)
- [Directory and File Structure](#directory-and-file-structure)
- [Usage Information](#usage-information)
- [License](#license)
- [Contact](#contact)

## Introduction
`afl-cov` uses test case files produced by the
[AFL fuzzer](http://lcamtuf.coredump.cx/afl/) `afl-fuzz` to generate gcov code
coverage results for a targeted binary. Code coverage is interpreted from one
case to the next by `afl-cov` in order to determine which new functions and
lines are hit by AFL with each new test case. Further, `afl-cov` allows for
specific lines or functions to be searched for within coverage results, and
when a match is found the corresponding test case file is displayed. This
allows the user to discover which AFL test case is the first to exercise a
particular function. In addition, `afl-cov` produces a "zero coverage" report
of functions and lines that were never executed during any AFL fuzzing run.

Although of no use to AFL itself, the main application of `afl-cov` is to wrap
some automation around gcov together with AFL test cases and thereby provide
data on how to maximize code coverage with AFL fuzzing runs. Manual
interpretation of cumulative gcov results from AFL test cases is usually still
required, but the "fiddly" steps of iterating over all test cases and
generating code coverage reports (along with the "zero coverage" report) is
automated by `afl-cov`.

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

## Prerequisites
`afl-cov` requires the following software:

 * afl-fuzz
 * python
 * gcov, lcov, genhtml

Note that `afl-cov` can parse files created by `afl-fuzz` from a different
system, so technically `afl-fuzz` does not need to be installed on the same
system as `afl-cov`. This supports scenarios where fuzzing output is collected,
say, within a git repository on one system, and coverage results are produced
on a different system. However, most workflows typically focus on producing
`afl-cov` results simultaneously for current fuzzing runs on the same system.

## Workflow
At a high level, the general workflow for `afl-cov` against a targeted project
is:

1. Have a target project compiled and known to work with AFL.
2. Create a spare copy of the project sources, and compile this copy with gcov
profiling support.
3. Run `afl-cov` against the copy either while `afl-fuzz` is building test
cases against the original sources, or after `afl-fuzz` has been stopped.
4. Review the cumulative code coverage results in the final web report.
5. Iterate to achieve higher coverage results. This might involve building
better initial test cases for AFL, or sometimes changing project sources
themselves.

Now, in more detail:

* Copy the project sources to a new directory, `/path/to/project-gcov/`.
This directory should contain the project binaries compiled for gcov profiling
support (gcc `-fprofile-arcs -ftest-coverage`).

* Start up `afl-cov` in `--live` mode before also starting the `afl-fuzz`
fuzzing cycle. The command line arguments to `afl-cov` must specify the path to
the output directory used by `afl-fuzz`, and the command to execute along with
associated arguments. This command and arguments should closely resemble the
manner in which `afl-fuzz` executes the targeted binary during the fuzzing
cycle. If there is already an existing directory of AFL fuzzing results, then
just omit the `--live` argument to process the existing results. Here is an
example:

```bash
$ cd /path/to/project-gcov/
$ afl-cov -d /path/to/afl-fuzz-output/ --live --coverage-cmd \
"cat AFL_FILE | LD_LIBRARY_PATH=./lib/.libs ./bin/.libs/somebin -a -b -c" \
--code-dir .
```

`/path/to/afl-fuzz-output/` is the output directory of afl-fuzz.

The `AFL_FILE` string above refers to the test case file that AFL will
build in the `queue/` directory under `/path/to/afl-fuzz-output`. Just leave this
string as-is since `afl-cov` will automatically substitute it with each AFL
`queue/id:NNNNNN*` in succession as it builds the code coverage reports.

Also, in the above command, this handles the case where the AFL fuzzing cycle
is fuzzing the targeted binary via stdin. This explains the
`cat AFL_FILE | ... ./bin/.lib/somebin ...` invocation. For the other style of
fuzzing with AFL where a file is read from the filesystem, here is an example:

```bash
$ cd /path/to/project-gcov/
$ afl-cov -d /path/to/afl-fuzz-output/ --live --coverage-cmd \
"LD_LIBRARY_PATH=./lib/.libs ./bin/.libs/somebin -f AFL_FILE -a -b -c" \
--code-dir .
```

* With `afl-cov` running, open a separate terminal/shell, and launch
`afl-fuzz`:

```bash
$ LD_LIBRARY_PATH=./lib/.libs afl-fuzz -T somebin -t 1000 \
-i /path/to/test-cases/ -o /path/to/afl-fuzz-output/ ./bin/.libs/somebin -a -b -c
```

The familiar AFL status screen will be displayed, and `afl-cov` will start
generating code coverage data.

![alt text][AFL-status-screen]

[AFL-status-screen]: doc/AFL_status_screen.png "AFL Fuzzing Cycle"

Note that by default `afl-cov` does not direct `lcov` to include branch
coverage results. This is because there are commonly many hundreds of AFL
test cases in the `queue/` directory, and generating branch coverage across all
of these cases may slow `afl-cov` down significantly. If branch coverage is
desired, just add the `--enable-branch-coverage` argument to `afl-cov`.

Here is a sample of what the `afl-cov` output looks like (note this includes
the `--enable-branch-coverage` argument as described above):

```bash
$ afl-cov -d /path/to/afl-fuzz-output/ --live --coverage-cmd \
"LD_LIBRARY_PATH=./lib/.libs ./bin/.libs/somebin -f AFL_FILE -a -b -c" \
--code-dir . --enable-branch-coverage
[+] Imported 184 files from: /path/to/afl-fuzz-output/queue
[+] AFL file: id:000000,orig:somestr.start (1 / 184), cycle: 0
    lines......: 18.6% (1122 of 6032 lines)
    functions..: 30.7% (100 of 326 functions)
    branches...: 14.0% (570 of 4065 branches)
[+] AFL file: id:000001,orig:somestr256.start (2 / 184), cycle: 2
    lines......: 18.7% (1127 of 6032 lines)
    functions..: 30.7% (100 of 326 functions)
    branches...: 14.1% (572 of 4065 branches)
[+] Coverage diff id:000000,orig:somestr.start id:000001,orig:somestr256.start
    Src file: /path/to/project-gcov/lib/proj_decode.c
      New 'line' coverage: 140
      New 'line' coverage: 141
      New 'line' coverage: 142
    Src file: /path/to/project-gcov/lib/proj_util.c
      New 'line' coverage: 217
      New 'line' coverage: 218
[+] AFL file: id:000002,orig:somestr384.start (3 / 184), cycle: 10
    lines......: 18.8% (1132 of 6032 lines)
    functions..: 30.7% (100 of 326 functions)
    branches...: 14.1% (574 of 4065 branches)
[+] Coverage diff id:000001,orig:somestr256.start id:000002,orig:somestr384.start
    Src file: /path/to/project-gcov/lib/proj_decode.c
      New 'line' coverage: 145
      New 'line' coverage: 146
      New 'line' coverage: 147
    Src file: /path/to/project-gcov/lib/proj_util.c
      New 'line' coverage: 220
      New 'line' coverage: 221
[+] AFL file: id:000003,orig:somestr.start (4 / 184), cycle: 5
    lines......: 18.9% (1141 of 6032 lines)
    functions..: 31.0% (101 of 326 functions)
    branches...: 14.3% (581 of 4065 branches)
[+] Coverage diff id:000002,orig:somestr384.start id:000003,orig:somestr.start
    Src file: /path/to/project-gcov/lib/proj_message.c
      New 'function' coverage: validate_cmd_msg()
      New 'line' coverage: 244
      New 'line' coverage: 247
      New 'line' coverage: 248
      New 'line' coverage: 250
      New 'line' coverage: 255
      New 'line' coverage: 262
      New 'line' coverage: 263
      New 'line' coverage: 266
.
.
.
[+] Coverage diff id:000182,src:000000,op:havoc,rep:64 id:000184,src:000000,op:havoc,rep:4
[+] Processed 184 / 184 files

[+] Final zero coverage report: /path/to/afl-fuzz-output/cov/zero-cov
[+] Final positive coverage report: /path/to/afl-fuzz-output/cov/pos-cov
[+] Final lcov web report: /path/to/afl-fuzz-output/cov/web/lcov-web-final.html
```

In the last few lines above, the locations of the final web coverage and zero
coverage reports are shown. The zero coverage reports contains function names
that were never executed across the entire `afl-fuzz` run.

The code coverage results in `/path/to/afl-fuzz-output/cov/web/lcov-web-final`
represent cumulative code coverage across all AFL test cases. This data can then
be reviewed to ensure that all expected functions are indeed exercised by AFL -
just point a web browser at `/path/to/afl-fuzz-output/cov/web/lcov-web-final.html`.
Below is a sample of what this report looks like for a cumulative AFL fuzzing
run - this is against the [fwknop](https://github.com/mrash/fwknop) project, and
the full report is [available here](https://www.cipherdyne.org/fwknop/2.6.7-afl-lcov-results/).
Note that even though fwknop has a dedicated set of
[AFL wrappers](https://github.com/mrash/fwknop/tree/master/test/afl), it is still
difficult to achieve high percentages of code coverage. This provides evidence
that measuring code coverage under AFL fuzzing runs is an important aspect of
trying to achieve maximal fuzzing results. Every branch/line/function that is
not exercised by AFL represents a location for which AFL has not been given the
opportunity to find bugs.

![alt text][AFL-lcov-web-report]

[AFL-lcov-web-report]: doc/AFL_lcov_web_report.png "AFL lcov web report"

### Parallelized AFL Execution
With the 0.4 release, `afl-cov` supports parallelized execution runs of
`afl-fuzz`. All that is required is to point `afl-cov -d sync_dir` at the top
level sync directory that is used by all `afl-fuzz` instances
(`afl-fuzz -o sync_dir`). The coverage results are calculated globally
across all fuzzing instances, and in `--live` mode new instances will be added
to the coverage results as they are created.

### Other Examples
The workflow above is probably the main strategy for using `afl-cov`. However,
additional use cases are supported such as:

1. Suppose there are a set of wrapper scripts around `afl-fuzz` to run fuzzing
cycles against various aspects of a project. By building a set of corresponding
`afl-cov` wrappers, and then using the `--disable-coverage-init` option on all
but the first of these wrappers, it is possible to generate code coverage
results across the entire set of `afl-fuzz` fuzzing runs. (By default,
`afl-cov` resets gcov counters to zero at start time, but the
`--disable-coverage-init` argument stops this behavior.) The end result is a
global picture of code coverage across all invocations of `afl-fuzz`.

2. Specific functions can be searched for in the code coverage results, and
`afl-cov` will return the first `afl-fuzz` test case where a given function is
executed. This allows `afl-cov` to be used as a validation tool by other scripts
and testing infrastructure. For example, a test case could be written around
whether an important function is executed by `afl-fuzz` to validate a patching
strategy mentioned in the introduction.

Here is an example where the first test case that executes the function
`validate_cmd_msg()` is returned (this is after all `afl-cov` results have been
produced in the main workflow above):

```bash
$ ./afl-cov -d /path/to/afl-fuzz-output --func-search "validate_cmd_msg"
[+] Function 'validate_cmd_mag()' executed by: id:000002,orig:somestr384.start
```

An equivalent way of searching the coverage results is to just `grep` the
function from the `cov/id-delta-cov` file described below. The number _"3"_ in
the output below is the AFL cycle number where the function is first executed:

```bash
$ grep validate_cmd_msg /path/to/afl-fuzz-output/cov/id-delta-cov
id:000002,orig:somestr384.start, 3, /path/to/project-gcov/file.c, function, validate_cmd_msg()
```

## Directory and File Structure
`afl-cov` creates a few files and directories for coverage results within the
specified `afl-fuzz` directory (`-d`). These files and directories are
displayed below, and all are contained within the main
`/path/to/afl-fuzz-output/cov/` directory and `<dirname>` refers to the
top level directory name for the fuzzing instance. When AFL is parallelized,
there will be one `<dirname>` directory path for each `afl-fuzz` instance.

 * `cov/diff/<dirname>` - contains new code coverage results when a
                `queue/id:NNNNNN*` file causes `afl-fuzz` to execute new code.
 * `cov/lcov/<dirname>` - contains raw code coverage data produced by the lcov
                front-end to gcov.
 * `cov/web/<dirname>`  - contains code coverage results in web format produced
                by `genhtml`.
 * `cov/zero-cov` - file that globally lists all functions (and optionally
                lines) that are never executed by any `afl-fuzz` test case.
 * `cov/pos-cov` - file that globally lists all functions (and optionally
                lines) that are executed at least once by an `afl-fuzz` test
                case.
 * `cov/id-delta-cov` - lists the functions (and optionally lines) that are
                executed by the first `id:000000*` test case, and then lists
                all new functions/lines executed in subsequent test cases.
 * `cov/afl-cov.log` - log file for `afl-cov` logging output.
 * `cov/afl-cov-status` - status file for `afl-cov` PID, version number , and
                command line arguments.

## Usage Information
Basic `--help` output appears below:

    usage: afl-cov [-h] [-e COVERAGE_CMD] [-d AFL_FUZZING_DIR] [-c CODE_DIR] [-O]
               [--disable-cmd-redirection] [--disable-lcov-web]
               [--disable-coverage-init] [--coverage-include-lines]
               [--enable-branch-coverage] [--live] [--cover-corpus]
               [--coverage-at-exit] [--sleep SLEEP] [--gcov-check]
               [--gcov-check-bin GCOV_CHECK_BIN] [--background]
               [--lcov-web-all] [--disable-lcov-exclude-pattern]
               [--lcov-exclude-pattern LCOV_EXCLUDE_PATTERN]
               [--func-search FUNC_SEARCH] [--line-search LINE_SEARCH]
               [--src-file SRC_FILE] [--afl-queue-id-limit AFL_QUEUE_ID_LIMIT]
               [--ignore-core-pattern] [--lcov-path LCOV_PATH]
               [--genhtml-path GENHTML_PATH] [--readelf-path READELF_PATH]
               [--stop-afl] [--validate-args] [-v] [-V] [-q]

    optional arguments:
      -h, --help            show this help message and exit
      -e COVERAGE_CMD, --coverage-cmd COVERAGE_CMD
                            Set command to exec (including args, and assumes code
                            coverage support)
      -d AFL_FUZZING_DIR, --afl-fuzzing-dir AFL_FUZZING_DIR
                            top level AFL fuzzing directory
      -c CODE_DIR, --code-dir CODE_DIR
                            Directory where the code lives (compiled with code
                            coverage support)
      -O, --overwrite       Overwrite existing coverage results
      --disable-cmd-redirection
                            Disable redirection of command results to /dev/null
      --disable-lcov-web    Disable generation of all lcov web code coverage
                            reports
      --disable-coverage-init
                            Disable initialization of code coverage counters at
                            afl-cov startup
      --coverage-include-lines
                            Include lines in zero-coverage status files
      --enable-branch-coverage
                            Include branch coverage in code coverage reports (may
                            be slow)
      --live                Process a live AFL directory, and afl-cov will exit
                            when it appears afl-fuzz has been stopped
      --cover-corpus        Measure coverage after running all available tests
                            instead of individually per queue file
      --coverage-at-exit    Only calculate coverage just before afl-cov exit.
      --sleep SLEEP         In --live mode, # of seconds to sleep between checking
                            for new queue files
      --gcov-check          Check to see if there is a binary in --coverage-cmd
                            (or in --gcov-check-bin) has coverage support
      --gcov-check-bin GCOV_CHECK_BIN
                            Test a specific binary for code coverage support
      --background          Background mode - if also in --live mode, will exit
                            when the alf-fuzz process is finished
      --lcov-web-all        Generate lcov web reports for all id:NNNNNN* files
                            instead of just the last one
      --disable-lcov-exclude-pattern
                            Allow default /usr/include/* pattern to be included in
                            lcov results
      --lcov-exclude-pattern LCOV_EXCLUDE_PATTERN
                            Set exclude pattern for lcov results
      --func-search FUNC_SEARCH
                            Search for coverage of a specific function
      --line-search LINE_SEARCH
                            Search for coverage of a specific line number
                            (requires --src-file)
      --src-file SRC_FILE   Restrict function or line search to a specific source
                            file
      --afl-queue-id-limit AFL_QUEUE_ID_LIMIT
                            Limit the number of id:NNNNNN* files processed in the
                            AFL queue/ directory
      --ignore-core-pattern
                            Ignore the /proc/sys/kernel/core_pattern setting in
                            --live mode
      --lcov-path LCOV_PATH
                            Path to lcov command
      --genhtml-path GENHTML_PATH
                            Path to genhtml command
      --readelf-path READELF_PATH
                            Path to readelf command
      --stop-afl            Stop all running afl-fuzz instances associated with
                            --afl-fuzzing-dir <dir>
      --validate-args       Validate args and exit
      -v, --verbose         Verbose mode
      -V, --version         Print version and exit
      -q, --quiet           Quiet mode

## License
`afl-cov` is released as open source software under the terms of
the **GNU General Public License (GPL v2+)**. The latest release can be found
at [https://github.com/mrash/afl-cov/releases](https://github.com/mrash/afl-cov/releases)

## Contact
All feature requests and bug fixes are managed through github issues tracking.
However, you can also email me (michael.rash_AT_gmail.com), or reach me through
Twitter ([@michaelrash](https://twitter.com/michaelrash)).
