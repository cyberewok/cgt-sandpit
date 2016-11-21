import unittest
from permutation import Permutation
from partition import PartitionStack, Partition
from refinement import Refinement
from refinement import IdentityFamily
from refinement import PartitionStabaliserFamily
from refinement import SubgroupFamily
from group import PermGroup

class TestRefinements(unittest.TestCase):
    def test_refinement_init(self):
        fam = IdentityFamily()
        a = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1])             
        b = PartitionStack([0,1,1,1,0],[-1,0,0,0,-1])             
        funcs = fam.extension_functions(a)
        self.assertEqual(funcs,None)

    def test_partition_stabaliser(self):
        fam = PartitionStabaliserFamily(Partition([[1,2],[3,4]]))
        a = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        func, _ = fam.extension_functions(a)
        func(a)
        funcs = fam.extension_functions(a)
        self.assertTrue(funcs is None)        
        self.assertEqual(sorted(a[-1]),  sorted(Partition([[1,2],[3,4]])))
    
    def test_partition_stabaliser_with_none(self):
        stab = Partition([[1],[2],[3,4]])
        fam = PartitionStabaliserFamily(stab)
        a = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        b = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        funcs1 = fam.extension_functions(a)
        funcs1[0](a)
        funcs2 = fam.extension_functions(a)
        funcs2[0](a)
        funcs3 = fam.extension_functions(a)
        self.assertTrue(funcs3 is None)
        funcs1[0](b)
        funcs2[0](b)                
        self.assertEqual(a,b)
        self.assertEqual(len(a[-1]),3)
        self.assertEqual(sorted(stab), sorted(a[-1]))
        
    def test_subgroup_family(self):
        cf = Permutation.read_cycle_form
        a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
        fam = SubgroupFamily(PermGroup([a,b]))
        stack = PartitionStack([0]*13,[-1]*13)
        stack.extend(0,[1,3,5,7,9,11])
        stack.extend(1,[1])
        stack.extend(1,[3])
        func1 = fam.extension_functions(stack)[1]
        extend = lambda x:fam.extension_functions(x)[0](x)
        extend(stack)
        after = Partition([[4,6,8,10,13],[5,7,9,11],[1],[3],[2,12]])
        self.assertEqual(stack[-1],after)
        stack.extend(1,[5])
        extend(stack)
        extend(stack)
        extend(stack)
        extend(stack)
        extend(stack)
        extend(stack)
        self.assertFalse(stack.discrete())
        extend(stack)
        self.assertTrue(stack.discrete())
        
        right_before = PartitionStack.single_partition_stack([[2,4,6,8,10,12,13],[1,5,7,11],[9],[3]])
        func1(right_before)
        right_after = Partition([[2,6,8,12,13],[1,5,7,11],[9],[3],[4,10]])
        self.assertEqual(right_before[-1],right_after)        
        
                
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRefinements))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())