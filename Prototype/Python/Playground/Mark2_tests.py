import unittest
import os
import importlib
import sys

def all_tests_suite(path):
    suites = []    
    for file in os.listdir(path):
        if not os.path.isfile(os.path.join(path, file)):
            continue
        name, extention = os.path.splitext(file)
        if name.endswith("_tests") and extention == ".py":
            test_mod = importlib.import_module(name)
            suites.append(test_mod.all_tests_suite())
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    cur_dir = os.getcwd()
    relative_path = "\\Mark2"
    abs_path = cur_dir + relative_path
    sys.path.append(abs_path)
    test_runner = unittest.TextTestRunner(verbosity=2)
    suite = all_tests_suite(abs_path)
    test_runner.run(suite)