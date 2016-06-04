#!/usr/bin/env python2

from aflcov import *
import argparse
import sys, os
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

def main():

    cargs = parse_cmdline()

    ### config
    tmp_file = './tmp_cmd.out'
    test_cmd = './test-afl-cov.py'

    ### the AFL test cases in the test suite are built against this
    ### commit in the fwknop code base
    fwknop_commit = 'e3ae6747'

    fwknop_codecov_dir     = 'fwknop-codecov.git'
    fwknop_codecov_compile = './compile/afl-compile-code-coverage.sh'

    fwknop_afl_dir     = 'fwknop-afl.git'
    fwknop_afl_compile = './compile/afl-compile.sh'

    ### system commands that we require
    cmds = {
        'git':'',
        'lcov':'',
        'make':'',
        'genhtml':'',
        'afl-fuzz':'',
        'python':'',
    }

    print "[+] Starting up afl-cov test suite..."

    ### check /proc/sys/kernel/core_pattern to see if afl-fuzz will
    ### accept it
    if not cargs.ignore_core_pattern:
        if not check_core_pattern():
            return

    ### make sure required system binaries are installed
    for cmd in cmds:
        cmds[cmd] = which(cmd)
        if not cmds[cmd]:
            print "[*] Could not find command '%s', exiting." % (cmd)
            return
    print "[+] Required binaries exist."

    ### clone the fwknop repository since the test suite operates
    ### against fwknop code
    if not is_dir(fwknop_codecov_dir):
        print "[+] (Code cov) Cloning fwknop repo: %s -> %s" % \
                (cargs.fwknop_git, fwknop_codecov_dir)
        do_cmd("%s clone %s %s" % (cmds['git'],
            cargs.fwknop_git, fwknop_codecov_dir), None, cargs)

    if not is_dir(fwknop_codecov_dir):
        print "[*] Could not clone %s, set a different --fwknop-git path?"
        return

    if not is_dir(fwknop_afl_dir):
        print "[+] (AFL support) Cloning fwknop repo: %s -> %s" % \
                (fwknop_codecov_dir, fwknop_afl_dir)
        do_cmd("%s clone %s %s" % (cmds['git'],
            fwknop_codecov_dir, fwknop_afl_dir), None, cargs)

    if not cargs.skip_compile:
        ### build both fwknop repositories under the specified commit
        build_fwknop(fwknop_codecov_dir, fwknop_commit,
                fwknop_codecov_compile, cmds, cargs)
        build_fwknop(fwknop_afl_dir, fwknop_commit,
                fwknop_afl_compile, cmds, cargs)

    ### run the actual tests
    print "[+] Running afl-cov tests (ignore 'Terminated' messages)..."
    subprocess.call("%s %s" % (cmds['python'], test_cmd),
            stdin=None, shell=True)

    return

def build_fwknop(cdir, commit, compile_cmd, cmds, cargs):

    curr_dir = os.getcwd()
    os.chdir(cdir)
    if os.path.exists('./server/.libs/fwknopd'):
        do_cmd("%s clean" % (cmds['make']), None, cargs)
    do_cmd("%s checkout %s" % (cmds['git'], commit), None, cargs)
    do_cmd("./autogen.sh", None, cargs)

    print "[+] Compiling %s with test/afl/%s..." % (cdir, compile_cmd)
    os.chdir('./test/afl')
    do_cmd("%s" % (compile_cmd), None, cargs)
    os.chdir(curr_dir)

    return

def do_cmd(cmd, tmp_file, cargs):

    out = []

    if cargs.verbose:
        print "    CMD: %s" % cmd

    fh = None
    if tmp_file:
        fh = open(tmp_file, 'w')
    else:
        fh = open(os.devnull, 'w')

    if cargs.verbose and not tmp_file:
        subprocess.call(cmd, stdin=None, shell=True)
    else:
        subprocess.call(cmd, stdin=None,
                stdout=fh, stderr=subprocess.STDOUT, shell=True)

    fh.close()

    if tmp_file:
        with open(tmp_file, 'r') as f:
            for line in f:
                out.append(line.rstrip('\n'))

    return out

def parse_cmdline():

    p = argparse.ArgumentParser()

    p.add_argument("--fwknop-git", type=str,
            help="Location of fwknop git repository",
            default="https://github.com/mrash/fwknop.git")
    p.add_argument("--ignore-core-pattern", action='store_true',
            help="Ignore the /proc/sys/kernel/core_pattern setting in --live mode",
            default=False)
    p.add_argument("--skip-compile", action='store_true',
            help="Skip fwknop compilation (assumes it was already done from a previous run)",
            default=False)
    p.add_argument("-v", "--verbose", action='store_true',
            help="Verbose mode", default=False)

    return p.parse_args()

if __name__ == "__main__":
    sys.exit(main())
