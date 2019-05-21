import unittest
from permutation_P import Permutation
from partition import Partition

class TestPermutation(unittest.TestCase):
    
    def test_equlity(self):
        a=Permutation([2,3,1,4])
        b=Permutation([2,1,4,3])
        self.assertEqual(b, Permutation([2,1,4,3]))
        self.assertNotEqual(a,b)    
    
    def test_cycle_form_reading(self):
        a=Permutation([2,3,1,4])
        b=Permutation.read_cycle_form([],4)
        e=Permutation([1,2,3,4])
        self.assertEqual(b, e)        
        self.assertEqual(a, Permutation.read_cycle_form([[1,2,3]],4))
        self.assertEqual(a, Permutation.read_cycle_form([[2,3,1]],4))
        self.assertEqual(a, Permutation.read_cycle_form([[3,1,2]],4))

    def test_read_partitions(self):
        a=Partition([[1],[2],[3],[4],[5]])
        b=Partition([[2],[3],[4],[5],[1]])
        c=Partition([[2],[1],[4],[3],[5]])
        perm1 = Permutation([2,3,4,5,1])
        perm1alt = Permutation.read_partitions(a,b)
        perm2 = Permutation([2,1,4,3,5])
        perm2alt = Permutation.read_partitions(a,c)
        perm3 = Permutation([5,2,1,4,3])
        perm3alt = Permutation.read_partitions(b,c)
        self.assertEqual(perm1, perm1alt)
        self.assertEqual(perm2, perm2alt)           
        self.assertEqual(perm3, perm3alt)
                        
        
    def test_composition(self):
        a=Permutation([2,3,1,4])
        b=Permutation([2,1,4,3])
        self.assertEqual(a*b, Permutation.read_cycle_form([[2,4,3]],4))
        self.assertEqual(b*a, Permutation.read_cycle_form([[1,3,4]],4))
    
    def test_action_on_numbers(self):
        a=Permutation([2,3,1,4])
        b=Permutation([2,1,4,3])
        self.assertEqual(1**a,2)
        self.assertEqual(1**b,2)
        self.assertEqual(3**a,1)
        self.assertEqual(3**b,4)
        self.assertEqual(4**a,4)
        self.assertEqual(4**b,3)
    
    def test_inverse(self):
        a=Permutation([2,3,1,4])
        b=Permutation([2,1,4,3])
        self.assertEqual(a**-1, Permutation([3,1,2,4]))
    
    def test_identity(self):
        a=Permutation([2,3,1,4])
        c=Permutation([])
        self.assertEqual(a**-1 * a, Permutation.read_cycle_form([],4))
        self.assertEqual(a * a**-1, Permutation.read_cycle_form([],4))
        self.assertEqual((a * a**-1)._func, (1,2,3,4))
        self.assertEqual(c._func, ())
    
    def test_order(self):
        a=Permutation([2,3,1,4])
        self.assertEqual(1 ** a ** -1, 3)
        
    def test_cycle_notation(self):
        a = Permutation([1,2,3,4,5,6])
        b = Permutation([1,3,2,5,6,4])
        c = Permutation([2,3,4,5,6,1])
        d = Permutation([6,4,5,2,3,1])
        self.assertEqual(a.cycle_notation(), [])
        self.assertEqual(b.cycle_notation(), [[2,3],[4,5,6]])
        self.assertEqual(c.cycle_notation(), [[1,2,3,4,5,6]])
        self.assertEqual(d.cycle_notation(), [[1,6],[2,4],[3,5]])
        
    def test_element_cycle(self):
        cf = lambda x:Permutation.read_cycle_form(x, 20)
        a = cf([[1,2,3],[4,5],[7,8,9,10,11,12,13,14,15]])
        self.assertEqual(a.element_cycle(1), [1,2,3])
        self.assertEqual(a.element_cycle(2), [2,3,1])
        self.assertEqual(a.element_cycle(5), [5,4])
        self.assertEqual(a.element_cycle(6), [6])
        self.assertEqual(a.element_cycle(13), [13,14,15,7,8,9,10,11,12])
        self.assertEqual(a.element_cycle(20), [20])
        a = cf([])
        self.assertEqual(a.element_cycle(1), [1])
        self.assertEqual(a.element_cycle(2), [2])
        
    
    def test_power(self):
        cf = lambda x:Permutation.read_cycle_form(x, 20)
        e = cf([])
        a = cf([[1,2,3],[4,5],[7,8,9,10,11,12,13,14,15,16,17,18]])
        b = cf([[1,2,3],[7,11,15],[8,12,16],[9,13,17],[10,14,18]])
        self.assertEqual(a**0, e) 
        self.assertEqual(a**1, a) 
        self.assertEqual(a**4, b)
        
    
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPermutation))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())