import unittest
from partition import PartitionStack, Partition
from refinement import Refinement
from refinement import _identity
from refinement import partition_stabaliser

class TestRefinements(unittest.TestCase):
    def test_refinement_init(self):
        fam = Refinement([_identity()])
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
        fam = Refinement([partition_stabaliser(Partition([[1,2],[3,4]]))])
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
        fam = Refinement([partition_stabaliser(stab)])
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
                
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRefinements))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())