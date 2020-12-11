#!/usr/bin/env python3

### IMPORTS ###
import glob
#import logging
import os
import sys
import unittest

#from tests.init_test_env import start_thread

### GLOBALS ###

### FUNCTIONS ###
def build_test_suites(test_glob):
    test_files = glob.glob(test_glob)
    suites = []
    for tmp_test_file in test_files:
        tmp_test_file_replace = tmp_test_file.replace('/', '.')
        tmp_test_file_replace = tmp_test_file_replace.replace('\\', '.')
        tmp_mod_str = "tests.{}".format(tmp_test_file_replace[0:len(tmp_test_file_replace) - 3])
        suites.append(unittest.defaultTestLoader.loadTestsFromName(tmp_mod_str))
    return suites

def run_all_tests():
    # Start the test server on a new thread
    #start_thread()

    #===== Run all test modules========
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Get all python files that start with 'test_'
    #test_files = glob.glob('test_*.py')
    # Convert files found into module names
    #module_strings = ['tests.' + test_file[0:len(test_file) - 3] for test_file in test_files]
    # Make testing suites for each module
    #suites = [unittest.defaultTestLoader.loadTestsFromName(test_file) for test_file in
    #          module_strings]
    # Consolidate all suites into one
    suites = []
    suites.extend(build_test_suites("test_*.py"))
    suites.extend(build_test_suites("utilities/binpacker/test_*.py"))
    test_suite = unittest.TestSuite(suites)
    # Run the test suite containing all the tests from all the modules
    test_runner = unittest.TextTestRunner()
    result = test_runner.run(test_suite)
    if result.wasSuccessful():
        return True
    return False

### CLASSES ###

### MAIN ###
if __name__ == '__main__':
    if run_all_tests() is False:
        sys.exit(1)
    sys.exit(0)
