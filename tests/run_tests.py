# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Process for running tests
# ---------------------------------------------------------
# ./tests/run_tests.py

import unittest
import argparse
import sys
import re

def _getTestSuite(test_suite_names:list[str]):

    if len(test_suite_names) == 0:
        return unittest.TestLoader().discover("tests")
    
    suite = unittest.TestSuite()
    for test_suite_name in test_suite_names:

        # Load the test suite
        if not test_suite_name.startswith("test_"):
            test_suite_name = "test_" + test_suite_name

        test_suite = unittest.TestLoader().discover("tests/"+test_suite_name)
        if test_suite.countTestCases() != 0:
            suite.addTest(test_suite)

    return suite
def _getTestCase(ts:unittest.TestSuite,tc=list()):
    for test in ts:
        if isinstance(test,unittest.TestSuite):
            _ = _getTestCase(test,tc)
        else:
            tc.append(test)
    return tc

def create_test_suite(test_suite_names:list[str], test_case_names:list[str], tag:str=None):
    """ create_test_suite
    Load a test suite by first loading every testcase of a module,
    then for each test case found, add the test case if it contains
    the correct tag.
    """
    suite = unittest.TestSuite()
    big_testSuite = _getTestSuite(test_suite_names)
    all_testcase = _getTestCase(big_testSuite)

    # Compile the test case name:
    re_test_case_pattern = list()
    for name in test_case_names:
        if not name.startswith("test_"):
            name = "test_"+name
        name.replace(".",r"\.")
        name = name.replace("*","(.*)")
        re_test_case_pattern.append(name)
    test_case_pattern = re.compile("|".join(re_test_case_pattern))

    for testCase in all_testcase:

        # Check name:
        if not test_case_pattern.search(testCase._testMethodName):
            continue
        
        # Check tag:
        # if tag := getattr(testCase,"_tag",None):
        #     print(f"tag: {tag}")

        suite.addTest(testCase)

    return suite

if __name__ == '__main__':

    # Arguments Parser:
    # -----------------
    parser = argparse.ArgumentParser(description='Run unit tests.')
    parser.add_argument('-ts','--test-suites', nargs='+', dest="test_suites", default=list(),
                        help="Test suite names to run. A test suite is considered to be the test of a module, and if the name dosen't start with 'test_', we automagically prepend 'test_' to the name. If none provided, test all")
    parser.add_argument('-tc','--test-cases', nargs='+', dest="test_cases", default=list(),
                        help="Test case names to run. Support re, so * will be replaced by (.*), and if the name dosen't start by 'test_', it will be prepended. If none provided, test all")
    parser.add_argument('-t','--tag', nargs='+', help='Run only test cases containing this tag. Not used',default=list())
    parser.add_argument('-v','--verbosity', help='Verbosity level (same as unittest.TextTestRunner)',choices=[0,1,2], default=1, type=int)
    args = parser.parse_args()

    # Start Process:
    # --------------
    if len(args.test_cases) == 0:
        args.test_cases = ["test_*"]
    suite = create_test_suite(args.test_suites, args.test_cases, args.tag)
    runner = unittest.TextTestRunner(verbosity=args.verbosity)
    result = runner.run(suite)

    # Exit:
    # -----
    sys.exit(not result.wasSuccessful())