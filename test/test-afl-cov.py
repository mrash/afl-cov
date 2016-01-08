#!/usr/bin/env python
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

import unittest
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

class TestAflCov(unittest.TestCase):

    ### set a few paths
    tmp_file     = './tmp_cmd.out'
    version_file = '../VERSION'

    def run_cmd(self, cmd):
        out = []
        fh = open(self.tmp_file, 'w')
        subprocess.call(cmd, stdin=None,
                stdout=fh, stderr=subprocess.STDOUT, shell=True)
        fh.close()
        with open(self.tmp_file, 'r') as f:
            for line in f:
                out.append(line.rstrip('\n'))
        return out

    def test_version(self):
        with open(self.version_file, 'r') as f:
            version = f.readline().rstrip()
        self.assertTrue(version in ''.join(self.run_cmd('../afl-cov --version')))

    def test_help(self):
        self.assertTrue('--verbose' in ''.join(self.run_cmd('../afl-cov -h')))

if __name__ == "__main__":
    unittest.main()
