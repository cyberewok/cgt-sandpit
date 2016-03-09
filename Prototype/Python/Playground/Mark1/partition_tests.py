import unittest
from partition import Partition, PartitionStack

class TestPartition(unittest.TestCase):
    
    def test_init(self):
        a = Partition([[1,2,3],[5,4],[8],[6,7]])
        b = Partition([])
        c = Partition([[]])
        d = Partition([[3,2,1],[5,4],[8],[7,6]], True)
        e = Partition([[1,2,3],[4,5],[8],[6,7]], False)
        self.assertEqual(a,d)
        self.assertEqual(a,e)
        self.assertEqual(d,e)              
        self.assertNotEqual(b,c)                     
        self.assertNotEqual(a,b)
    
    def test_extend(self):
        a = Partition([[1,2,3],[4,5],[8],[6,7]])        
        b = a.extend(3, [6]).extend(0, [1,2])
        c = Partition([[3],[5,4],[8],[7],[6],[1,2]])
        self.assertEqual(b,c)
        
class TestPartitionStack(unittest.TestCase):
    def test_init(self):
        pass
    
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPartition))
    suite.addTest(unittest.makeSuite(TestPartitionStack))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())