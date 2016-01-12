# Testing afl-cov

This is the test suite for the afl-cov project and consists of three things:

1. A set of test cases that were built by running AFL against the fwknop project.
2. A set of unit tests in the `test-afl-cov.py` script.
3. A wrapper script `run.py` that is designed to set everything up and run the
unit tests.

When running the test suite, it is best to run the `run.py` script. However,
individual unit test can be invoked as follows like this: `python ./test-afl-cov.py TestAflCov.test_<name>` (where `<name>` corresponds to a unit test method name
in `test-afl-cov.py`).
