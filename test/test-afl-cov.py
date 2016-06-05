#!/usr/bin/env python2
#
#  File: test-afl-cov.py
#
#  Purpose: Run afl-cov through a series of tests to ensure proper operations
#           on the local system.
#
#  License (GNU General Public License):
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02111-1301,
#  USA
#

from shutil import rmtree, copy
from aflcov import *
import unittest
import time
import signal
import os
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

class TestAflCov(unittest.TestCase):

    ### set a few paths
    tmp_file     = './tmp_cmd.out'
    version_file = '../VERSION'
    afl_cov_cmd  = '../afl-cov'
    single_generator   = './afl/afl-cov-generator.sh'
    parallel_generator = './afl/afl-cov-generator-parallel.sh'
    afl_cov_live       = './afl/afl-cov-generator-live.sh'

    top_out_dir  = './fwknop-afl.git/test/afl/fuzzing-output/server-access.out'
    live_afl_cmd = './fuzzing-wrappers/server-access-redir.sh'
    live_parallel_afl_cmd = './fuzzing-wrappers/server-access-parallel-redir.sh'

    def do_cmd(self, cmd):
        out = []
        fh = open(self.tmp_file, 'w')
        subprocess.call(cmd, stdin=None,
                stdout=fh, stderr=subprocess.STDOUT, shell=True)
        fh.close()
        with open(self.tmp_file, 'r') as f:
            for line in f:
                out.append(line.rstrip('\n'))
        return out

    ### start afl-cov in --live mode - this is for both single and
    ### parallel instance testing
    def live_init(self):
        if is_dir(os.path.dirname(self.top_out_dir)):
            if is_dir(self.top_out_dir):
                rmtree(self.top_out_dir)
        else:
            if not is_dir(os.path.dirname(self.top_out_dir)):
                os.mkdir(os.path.dirname(self.top_out_dir))

        ### start up afl-cov in the background before AFL is running
        try:
            subprocess.Popen([self.afl_cov_live])
        except OSError:
            return False
        time.sleep(2)
        return True

    def afl_stop(self):

        ### stop any afl-fuzz instances
        self.do_cmd("%s --stop-afl --afl-fuzzing-dir %s" \
                % (self.afl_cov_cmd, self.top_out_dir))

        ### now stop afl-cov
        afl_cov_pid = get_running_pid(
                self.top_out_dir + '/cov/afl-cov-status',
                'afl_cov_pid\s+\:\s+(\d+)')
        if afl_cov_pid:
            os.kill(afl_cov_pid, signal.SIGTERM)

        return

    def test_version(self):
        with open(self.version_file, 'r') as f:
            version = f.readline().rstrip()
        self.assertTrue(version
                in ''.join(self.do_cmd("%s --version" % (self.afl_cov_cmd))),
                "afl-cov --version does not match VERSION file")

    def test_help(self):
        self.assertTrue('--verbose'
                in ''.join(self.do_cmd("%s -h" % (self.afl_cov_cmd))),
                "--verbose not in -h output")

    def test_stop_requires_fuzz_dir(self):
        self.assertTrue('Must set'
                in ''.join(self.do_cmd("%s --stop-afl" % (self.afl_cov_cmd))),
                "--afl-fuzzing-dir missing from --stop-afl mode")

    def test_func_search_requires_fuzz_dir(self):
        self.assertTrue('Must set'
                in ''.join(self.do_cmd("%s --func-search test" % (self.afl_cov_cmd))),
                "--afl-fuzzing-dir missing from --func-search mode")

    def test_line_search_requires_fuzz_dir(self):
        self.assertTrue('Must set'
                in ''.join(self.do_cmd("%s --line-search 1234" % (self.afl_cov_cmd))),
                "--afl-fuzzing-dir missing from --line-search mode")

    def test_live_parallel(self):

        if not self.live_init():
            return self.assertTrue(False, "Could not run generator cmd: %s" \
                    % (self.afl_cov_live))

        ### put the wrapper in place
        wrapper ='fwknop-afl.git/test/afl/fuzzing-wrappers' + \
                '/server-access-parallel-redir.sh'
        if os.path.exists(wrapper):
            os.remove(wrapper)
        copy('afl/server-access-parallel-redir.sh', wrapper)
        curr_dir = os.getcwd()
        os.chdir('./fwknop-afl.git/test/afl')

        ### now start two copies of AFL
        try:
            subprocess.Popen([self.live_parallel_afl_cmd, "-M", "fuzzer01"])
        except OSError:
            os.chdir(curr_dir)
            return self.assertTrue(False,
                    "Could not run live_parallel_afl_cmd: %s -M fuzzer01" \
                            % (self.live_parallel_afl_cmd))

        try:
            subprocess.Popen([self.live_parallel_afl_cmd, "-S", "fuzzer02"])
        except OSError:
            os.chdir(curr_dir)
            return self.assertTrue(False,
                    "Could not run live_parallel_afl_cmd: %s -S fuzzer02" \
                            % (self.live_parallel_afl_cmd))

        os.chdir(curr_dir)

        time.sleep(3)

        self.afl_stop()

        if not (is_dir(self.top_out_dir + '/fuzzer01')
                and is_dir(self.top_out_dir + '/fuzzer02')):
            return self.assertTrue(False,
                    "fuzzer01 or fuzzer02 directory missing")

        ### check for the coverage directory since afl-cov should have
        ### seen the running AFL instance by now
        return self.assertTrue(is_dir(self.top_out_dir + '/cov'),
                "live coverage directory '%s' does not exist" \
                        % (self.top_out_dir + '/cov'))

    def test_live(self):

        if not self.live_init():
            return self.assertTrue(False, "Could not run generator cmd: %s" \
                    % (self.afl_cov_live))

        ### put the wrapper in place
        wrapper = 'fwknop-afl.git/test/afl/fuzzing-wrappers/server-access-redir.sh'
        if os.path.exists(wrapper):
            os.remove(wrapper)
        copy('afl/server-access-redir.sh', wrapper)
        curr_dir = os.getcwd()
        os.chdir('./fwknop-afl.git/test/afl')

        ### now start AFL and let it run for longer than --sleep in the
        ### generator script - then look for the coverage directory
        try:
            subprocess.Popen([self.live_afl_cmd])
        except OSError:
            os.chdir(curr_dir)
            return self.assertTrue(False,
                    "Could not run live_afl_cmd: %s" % (self.live_afl_cmd))
        os.chdir(curr_dir)

        time.sleep(3)

        self.afl_stop()

        ### check for the coverage directory since afl-cov should have
        ### seen the running AFL instance by now
        return self.assertTrue(is_dir(self.top_out_dir + '/cov'),
                "live coverage directory '%s' does not exist" \
                        % (self.top_out_dir + '/cov'))

    def test_queue_limit_5(self):
        out_str = ''.join(self.do_cmd("%s --afl-queue-id-limit 5 --overwrite" \
                        % (self.single_generator)))
        self.assertTrue('Final lcov web report' in out_str
                and "New 'line' coverage: 1585" in out_str)

    def test_queue_limit_5_cover_corpus(self):
        out_str = ''.join(self.do_cmd("%s --afl-queue-id-limit 5 --overwrite --cover-corpus" \
                        % (self.single_generator)))
        self.assertTrue('Final lcov web report' in out_str
                and "New 'line' coverage: 1585" in out_str)

    def test_overwrite_dir(self):
        ### generate coverage, and then try to regenerate without --overwrite
        self.do_cmd("%s --afl-queue-id-limit 1 --overwrite" \
                        % (self.single_generator))
        out_str = ''.join(self.do_cmd("%s --afl-queue-id-limit 1" \
                        % (self.single_generator)))
        self.assertTrue("use --overwrite" in out_str,
                "Missing --overwrite not caught")

    def test_queue_limit_5_parallel(self):
        out_str = ''.join(self.do_cmd("%s --afl-queue-id-limit 5 --overwrite" \
                        % (self.parallel_generator)))
        self.assertTrue('Final lcov web report' in out_str
                and "New 'line' coverage: 977" in out_str
                and "Imported 145 new test cases" in out_str
                and "Imported 212 new test cases" in out_str)

    def test_queue_limit_5_parallel_cover_corpus(self):
        out_str = ''.join(self.do_cmd("%s --afl-queue-id-limit 5 --overwrite --cover-corpus" \
                        % (self.parallel_generator)))
        self.assertTrue('Final lcov web report' in out_str
                and "New 'line' coverage: 977" in out_str
                and "Imported 145 new test cases" in out_str
                and "Imported 212 new test cases" in out_str)

if __name__ == "__main__":
    unittest.main()
