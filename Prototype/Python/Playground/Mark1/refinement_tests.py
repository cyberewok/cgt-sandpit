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
        fam = Refinement([IdentityFamily()])
        triple = fam.extend(None,None)
        self.assertEqual(triple,(None,None,None))
        a = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1])             
        b = PartitionStack([0,1,1,1,0],[-1,0,0,0,-1])             
        triple = fam.extend(a,None)
        self.assertEqual(triple,(a,None,None))
        triple = fam.extend(None,b)
        self.assertEqual(triple,(None,b,None))
        triple = fam.extend(a,b)
        self.assertEqual(triple,(a,b,None))
        self.assertEqual(a, PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1]))
        self.assertEqual(b, PartitionStack([0,1,1,1,0],[-1,0,0,0,-1]))          
        
    def test_partition_stabaliser(self):
        fam = Refinement([PartitionStabaliserFamily(Partition([[1,2],[3,4]]))])
        a = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        b = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        _,_, func = fam.extend(a,b)
        c = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        d = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        func(c,d)
        self.assertEqual((a,b),(c,d))
        _,_,func2 = fam.extend(a,b)
        self.assertTrue(func2 == None)
        self.assertEqual((a,b),(c,d))
    
    def test_partition_stabaliser_with_none(self):
        stab = Partition([[1],[2],[3,4]])
        fam = Refinement([PartitionStabaliserFamily(stab)])
        a = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        b = PartitionStack([0,0,0,0],[-1,-1,-1,-1])
        _,_,func1 = fam.extend(a,None)
        _,_,func2 = fam.extend(a,None)
        _,_,func3 = fam.extend(a,None)
        self.assertTrue(func3 == None)
        func1(None,b)
        func2(None,b)                
        self.assertEqual(a,b)
        self.assertEqual(len(a[-1]),3)
        self.assertEqual(sorted(stab), sorted(a[-1]))
        
    def test_subgroup_family(self):
        cf = Permutation.read_cycle_form
        a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
        fam = Refinement([SubgroupFamily(PermGroup([a,b]))])
        stack = PartitionStack([0]*13,[-1]*13)
        stack.extend(0,[1,3,5,7,9,11])
        stack.extend(1,[1])
        stack.extend(1,[3])
        _,_,func1 = fam.extend(stack,None)
        after = Partition([[4,6,8,10,13],[5,7,9,11],[1],[3],[2,12]])
        self.assertEqual(stack[-1],after)
        stack.extend(1,[5])
        fam.extend(stack,None)
        fam.extend(stack,None)
        fam.extend(stack,None)
        fam.extend(stack,None)
        fam.extend(stack,None)
        fam.extend(stack,None)
        self.assertFalse(stack.discrete())
        fam.extend(stack,None)
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