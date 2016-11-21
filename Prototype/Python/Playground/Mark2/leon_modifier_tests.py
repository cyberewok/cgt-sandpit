import unittest
from permutation import Permutation
from partition import PartitionStack, Partition
from group import PermGroup
from leon_modifier import ModifierUnion
from leon_modifier import PartitionStackConstraint
from refinement import RefinementUnion
from refinement import IdentityFamily
from refinement import PartitionStabaliserFamily
from refinement import SubgroupFamily
from coset_property import CosetPropertyUnion
from coset_property import IdentityProperty
from coset_property import SubgroupProperty
from coset_property import PartitionStabaliserProperty
from leon_logger import LeonLoggerUnion
from leon_logger import NodeCounter as LeonCounter

class TestModifiers(unittest.TestCase):
    def test_identity_modifiers(self):
        cf = lambda x:Permutation.read_cycle_form(x,5)
        fam = RefinementUnion([IdentityFamily()])
        prop = CosetPropertyUnion([IdentityProperty()])
        log = LeonLoggerUnion([LeonCounter()])
        union = ModifierUnion([fam,prop,log])
        a = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1])             
        b = PartitionStack([0,1,1,1,0],[-1,0,0,0,-1])
        funcs = union.extension_functions(a)
        self.assertEqual(funcs,None)
        index = union.exclude_backtrack_index(a,b, None, None)
        self.assertEqual(index,None)
        check = union.property_check(None)
        self.assertTrue(check)
        pos_leaf = union.leaf_fail_backtrack_index(a,b,None)
        neg_leaf = union.leaf_pass_backtrack_index(a,b,None)
        self.assertEqual(pos_leaf, None)
        self.assertEqual(neg_leaf, None)

    def test_non_trivial_modifiers(self):
        cf = lambda x: Permutation.read_cycle_form(x,13)
        a = cf([[2,3],[4,6],[5,8],[9,11]])
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]])
        G = PermGroup([a,b])
        part_stab = Partition([[3,2],[6,4],[5,1,7,8,9,10,11,12,13]])
        
        fam = RefinementUnion([PartitionStabaliserFamily(part_stab), SubgroupFamily(G)])
        
        prop = CosetPropertyUnion([PartitionStabaliserProperty(part_stab), SubgroupProperty(G)])
        
        log = LeonLoggerUnion([LeonCounter()])
        
        cons = ModifierUnion([PartitionStackConstraint()])
        
        union = ModifierUnion([fam,prop,log,cons])
        
        left = PartitionStack([0]*13,[-1]*13)         
        right = PartitionStack.deep_copy(left)
        
        funcs = union.extension_functions(left)
        self.assertFalse(funcs is None)
        funcs[0](left)
        funcs[1](right)
        
        index = union.exclude_backtrack_index(left,right, None, 1)
        self.assertEqual(index,None)

        index = union.exclude_backtrack_index(left,right, None, 2)
        self.assertEqual(index,1)
        
        self.assertTrue(union.property_check(a))
        self.assertFalse(union.property_check(b))
        
        pos_leaf = union.leaf_fail_backtrack_index(a,b,None)
        neg_leaf = union.leaf_pass_backtrack_index(a,b,None)
        self.assertEqual(pos_leaf, None)
        self.assertEqual(neg_leaf, None)
                
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestModifiers))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())