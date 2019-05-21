import unittest
from permutation import Permutation
from partition import PartitionStack, Partition
from refinement import Refinement
from refinement import IdentityFamily
from refinement import PartitionStabaliserFamily
from refinement import SubgroupFamily
from refinement import UnorderedPartitionStabaliserFamily
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

class TestUnorderedPartitionStabaliserFamily(unittest.TestCase):
    def test_height_increase_decrease(self):
        size = 5
        
        to_stab = Partition([[1,2],[3,4],[5]])
        fam = UnorderedPartitionStabaliserFamily(to_stab)
        
        stack = PartitionStack([0]*size, [-1]*size)
        fam.begin_preprocessing()
        self.assertEqual(fam.derived[-1], Partition([[3],[1,2]]))
        self.assertEqual(fam.derived_indices, [1])
        
        stack.extend(0,[4])
        self.assertEqual(stack[-1], Partition([[1,2,3,5],[4]]))
        fam.height_increase(stack, stack, None, len(stack) - 1)
        self.assertEqual(fam.derived[-1], Partition([[3],[1],[2]]))
        self.assertEqual(fam.derived_indices, [1,2])
        
        stack.pop()  
        self.assertEqual(stack[-1], Partition([[1,2,3,4,5]]))
        fam.height_decrease(stack, stack, None, len(stack) - 1)
        self.assertEqual(fam.derived[-1], Partition([[3],[1,2]]))
        self.assertEqual(fam.derived_indices, [1])

        stack.extend(0,[2,3])          
        self.assertEqual(stack[-1], Partition([[1,4,5],[2,3]]))
        fam.height_increase(stack, stack, None, len(stack) - 1)
        self.assertEqual(fam.derived[-1], Partition([[3],[1,2]]))
        self.assertEqual(fam.derived_indices, [1,1])
        
        stack.pop()  
        self.assertEqual(stack[-1], Partition([[1,2,3,4,5]]))
        fam.height_decrease(stack, stack, None, len(stack) - 1)
        self.assertEqual(fam.derived[-1], Partition([[3],[1,2]]))
        self.assertEqual(fam.derived_indices, [1])
        
        stack.extend(0,[])          
        self.assertEqual(stack[-1], Partition([[1,2,3,4,5]]))
        fam.height_increase(stack, stack, None, len(stack))
        self.assertEqual(fam.derived[-1], Partition([[3],[1,2]]))
        self.assertEqual(fam.derived_indices, [1,1])
    
    def test_height_increase(self):
        size = 13
        cf = lambda x: Permutation.read_cycle_form(x, size)
        
        to_stab = Partition([[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13]])
        fam = UnorderedPartitionStabaliserFamily(to_stab)
        
        stack = PartitionStack([0]*size, [-1]*size)
        fam.begin_preprocessing()
        stack.extend(0,[3,7,8,10,12])    
        fam.height_increase(stack, stack, None, len(stack) - 1)
        stack.extend(0,[2,9,13])        
        fam.height_increase(stack, stack, None, len(stack) - 1)
        self.assertEqual(stack[-1],Partition([[1,4,5,6,11],[3,7,8,10,12],[2,9,13]]))
        self.assertEqual(fam.derived[-1], Partition([[7],[3],[4],[2,6],[1],[5]]))

    def test_unordered_partition_stabaliser_family(self):
        size = 13
        cf = lambda x: Permutation.read_cycle_form(x, size)
        
        to_stab = Partition([[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13]])
        fam = UnorderedPartitionStabaliserFamily(to_stab)
        
        stack = PartitionStack([0]*size, [-1]*size)
        fam.begin_preprocessing()
        func1 = fam.extension_functions(stack)[1]
        func1(stack)
        fam.height_increase(stack, stack, None, len(stack) - 1)
        self.assertEqual(stack[-1],Partition([[1,2,3,4,5,6,7,8,9,10,11,12],[13]]))     
        self.assertTrue(fam.extension_functions(stack) is None)
        
        stack.extend(0,[3,7,8,10,12])
        self.assertEqual(stack[-1],Partition([[1,2,4,5,6,9,11],[13],[3,7,8,10,12]]))   
        fam.height_increase(stack, stack, None, len(stack) - 1)
        self.assertEqual(fam.derived[-1],Partition([[7],[1,3],[4],[2,5,6]]))
        
        func1 = fam.extension_functions(stack)[1]
        func1(stack)  
        fam.height_increase(stack, stack, None, len(stack) - 1)
        self.assertEqual(stack[-1],Partition([[4,9,11],[13],[3,7,8,10,12],[1,2,5,6]])) 
        
        func2 = fam.extension_functions(stack)[1]
        func2(stack)
        fam.height_increase(stack, stack, None, len(stack) - 1)
        self.assertEqual(stack[-1],Partition([[4,9,11],[13],[3,10,12],[1,2,5,6],[7,8]]))
        self.assertEqual(fam.derived[-1],Partition([[7],[1,3],[4],[2,5,6]]))
        self.assertTrue(fam.extension_functions(stack) is None)
              
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRefinements))
    suite.addTest(unittest.makeSuite(TestUnorderedPartitionStabaliserFamily))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())