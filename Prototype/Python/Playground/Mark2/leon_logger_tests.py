import unittest
from leon_logger import LeonLoggerUnion
from leon_logger import NodeCounter as LeonCounter

class TestLeonLogger(unittest.TestCase):
    def test_leon_counter(self):
        counter = LeonCounter()
        union = LeonLoggerUnion([counter])
        union.exclude_backtrack_index(None, None, None)
        union.leaf_fail_backtrack_index(None, None, None)
        union.exclude_backtrack_index(None, None, None)
        union.leaf_pass_backtrack_index(None, None, None)
        union.leaf_fail_backtrack_index(None, None, None)
        union.leaf_pass_backtrack_index(None, None, None)
        self.assertEqual(counter.leaf_count, 4)
        self.assertEqual(counter.pos_leaf_count, 2)
        self.assertEqual(counter.node_count, 2)

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLeonLogger))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())