import unittest
from partition import Partition
from permutation import Permutation
from coset_property import CosetProperty
from coset_property import _identity
from coset_property import partition_stabaliser

class TestCosetProperty(unittest.TestCase):
    def test_coset_init(self):
        prop = CosetProperty([_identity()])
        self.assertTrue(prop.check(Permutation.read_cycle_form([[1,2,3,4]], 5)))
                
    def test_partition_stabaliser(self):
        prop = CosetProperty([partition_stabaliser(Partition([[1,2],[3,4],[5]]))])
        pos = Permutation.read_cycle_form([[1,2]],5)
        neg = Permutation.read_cycle_form([[1,2],[4,5]],5)
        self.assertTrue(prop.check(pos))
        self.assertFalse(prop.check(neg))

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCosetProperty))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())