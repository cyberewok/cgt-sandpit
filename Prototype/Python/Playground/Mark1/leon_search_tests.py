import unittest

class TestLeonSearch(unittest.TestCase):
    def test_preprocess(self):
        pass

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLeonSearch))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())