import unittest
import os
import importlib
import sys

def all_tests_suite(path):
    suites = []    
    for file in os.listdir(path):
        if not os.path.isfile(os.path.join(path, file)):
            break
        name, extention = os.path.splitext(file)
        if name.endswith("_tests") and extention == ".py":
            test_mod = importlib.import_module(name)
            suites.append(test_mod.all_tests_suite())
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    abs_path = "C:\\Users\\admin-u5887726\\Google Drive\\Phd\\Programming\\cgt-sandpit\\Prototype\\Python\\Playground\\Mark1"
    sys.path.append(abs_path)
    test_runner = unittest.TextTestRunner(verbosity=2)
    suite = all_tests_suite(abs_path)
    test_runner.run(suite)