import unittest
from cgt.group import PermGroup as Group
from cgt.ordering import ordering_to_perm_key, ordering_to_key
from cgt.permutation import Permutation
from cgt.random_element_generator import ProductReplacer

class TestProductReplacer(unittest.TestCase):
    def test_init(self):
        degree = 10
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3],[4,5],[8,9]])
        b = cf([[3,4],[5,8],[9,10,2]])
        pr = ProductReplacer([a,b])
        pr.element()
        pr.element()
        pr.element()

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProductReplacer))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())