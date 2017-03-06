import unittest
from partition import Partition, PartitionStack
from permutation import Permutation

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
    
    def test_pow(self):
        perm = Permutation.read_cycle_form([[1,2],[5,3]], 5)
        a = Partition([[1,2,3], [4,5]])
        b = a ** perm
        c = Partition([[1,5,2], [4,3]])
        d = b ** perm
        self.assertEqual(a,d)
        self.assertEqual(b,c)              
        self.assertNotEqual(a,c)                     
        self.assertNotEqual(b,d)        
    
    def test_extend(self):
        a = Partition([[1,2,3],[4,5],[8],[6,7]])        
        b = a.extend(3, [6]).extend(0, [1,2])
        c = Partition([[3],[5,4],[8],[7],[6],[1,2]])
        self.assertEqual(b,c)
        
    def test_discrete(self):
        a = Partition([[3],[1],[2]])
        b = Partition([[1,2],[3],[4]])
        self.assertTrue(a.discrete())
        self.assertFalse(b.discrete())
        
class TestPartitionStack(unittest.TestCase):
    def test_single_partition_stack(self):
        stack = PartitionStack([0,0,1,1,2,2],[-1,-1,0,0,0,0])
        part = Partition([[1,2],[3,4],[5,6]])
        self.assertEqual(stack[-1], part)
        self.assertEqual(stack, PartitionStack.single_partition_stack(part))
    
    def test_use_case(self):
        stack = PartitionStack([6,2,4,7,0,0,3,5,1,4],[1,1,0,2,-1,-1,0,4,0,0])
        self.assertEqual(len(stack), 8)
        self.assertEqual(stack[-1], Partition([[5,6],[9],[2],[7],[3,10],[8],[1],[4]]))
        self.assertEqual(stack[4][2], [2,4])
        self.assertEqual(stack[-1][4], [3,10])
        self.assertEqual(stack[-1][-1], [4])

    def test_get_item(self):
        a = PartitionStack([0,3,1,2,1],[-1,0,0,1,0])
        self.assertEqual(a[0], Partition([[1,2,3,4,5]]))
        self.assertEqual(a[1], Partition([[1,2],[3,4,5]]))
        self.assertEqual(a[2], Partition([[1,2],[3,5],[4]]))
        self.assertEqual(a[3], Partition([[1],[3,5],[4],[2]]))
        self.assertEqual(a[-1], Partition([[1],[3,5],[4],[2]]))
        self.assertEqual(a[:4], PartitionStack([0,3,1,2,1],[-1,0,0,1,0]))  
        self.assertEqual(a[:3], PartitionStack([0,0,1,2,1],[-1,-1,0,1,0]))  
        self.assertEqual(a[:2], PartitionStack([0,0,1,1,1],[-1,-1,0,0,0]))  
        self.assertEqual(a[:1], PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1])) 
        self.assertEqual(a[1,1], [3,4,5])     
        self.assertEqual(a[-1,3], [2]) 
        
    def test_multi_extend(self):
        base1 = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1])
        base1.extend(0,[3,4,5])
        base1.extend(1,[4])
        base1.extend(0,[2])
        self.assertEqual(base1[-1], Partition([[1],[5,3],[4],[2]]))
        base2 = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1])
        func_list = [1, 4, 6, 5, 6]
        func = lambda x: func_list[x-1]
        base2.multi_extend(func)
        self.assertEqual(base2[-1], Partition([[1],[5,3],[4],[2]]))
        
    def test_multi_extend_large(self):
        size = 14
        base = PartitionStack([0]*size,[-1]*size)
        base.extend(0,[4,5,6])
        base.extend(0,[7,8,9])
        base.extend(0,[10,11,12])
        self.assertEqual(base[-1], Partition([[1,2,3,13,14],[4,5,6],[7,8,9],[10,11,12]]))
        func_list = [1, 1, 10, 3, 4, 5, 77,77,77,7,7,1,2,10]
        func = lambda x: func_list[x-1]
        base.multi_extend(func)
        self.assertEqual(base[-1], Partition([[1,2],[4],[7,8,9],[12],[3,14],[13],[6],[5],[10,11]]))    
        
    def test_extend(self):
        base = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1])
        self.assertEqual(base[-1], Partition([[1,2,3,4,5]]))
        base.extend(0,[3,4,5])
        self.assertEqual(base[-1], Partition([[1,2],[3,4,5]]))
        base.extend(1,[4])
        self.assertEqual(base[-1], Partition([[1,2],[3,5],[4]]))
        base.extend(0,[2])
        self.assertEqual(base[-1], Partition([[1],[3,5],[4],[2]]))
        extention = base.extend(1,[5])
        self.assertEqual(extention[-1], Partition([[1],[3],[4],[2],[5]]))
        self.assertEqual(base[-1], Partition([[1],[3],[4],[2],[5]]))
        
        self.assertEqual(extention[0], Partition([[1,2,3,4,5]]))
        self.assertEqual(extention[1], Partition([[1,2],[3,4,5]]))
        self.assertEqual(extention[2], Partition([[1,2],[3,5],[4]]))
        self.assertEqual(extention[3], Partition([[1],[3,5],[4],[2]]))
        self.assertEqual(extention[4], Partition([[1],[3],[4],[2],[5]]))

        base = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1]) 
        base.extend(0, [])
        self.assertEqual(len(base[-1]), 1)
        base = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1]) 
        base.extend(0, [1,2,3,4,5])
        self.assertEqual(len(base[-1]), 1)
        
    def test_can_extend(self):
        base = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1]) 
        base.extend(0, [1,3,5])
        self.assertEqual(base[-1], Partition([[2,4],[1,3,5]]))
        self.assertFalse(base.can_extend(0,[2,4]))
        self.assertFalse(base.can_extend(0,[2,4,1,3]))
        self.assertFalse(base.can_extend(0,[]))
        self.assertFalse(base.can_extend(0,[5]))
        self.assertTrue(base.can_extend(0,[1,2,3]))
        self.assertTrue(base.can_extend(0,[4]))
    
    def test_valid_intersection(self):
        base = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1]) 
        base.extend(0, [1,3,5])
        self.assertEqual(base[-1], Partition([[2,4],[1,3,5]]))
        self.assertTrue(base._valid_intersection(1,[2,4]) is None)
        self.assertEqual(base._valid_intersection(1,[1,2,4,5]), [1,5])
        

    def test_discrete(self):
        base = PartitionStack([0,0,0,0,0],[-1,-1,-1,-1,-1])
        base.extend(0,[3,4,5])
        base.extend(1,[4])
        base.extend(0,[2])
        self.assertFalse(base.discrete())
        base.extend(1,[5])
        self.assertTrue(base.discrete())
        
    def test_fix(self):
        stack = PartitionStack([6,2,4,7,0,0,3,5,1,4],[1,1,0,2,-1,-1,0,4,0,0])
        self.assertEqual(stack.fix(), [7,8,1,9,4,2])
        
    def test_pop(self):
        stack = PartitionStack([6,2,4,7,0,0,3,5,1,4],[1,1,0,2,-1,-1,0,4,0,0])
        self.assertEqual(stack[-1], Partition([[5,6],[9],[2],[7],[3,10],[8],[1],[4]]))
        stack.pop()
        self.assertEqual(stack[-1], Partition([[5,6],[9],[2,4],[7],[3,10],[8],[1]]))
        self.assertEqual(stack, PartitionStack([6,2,4,2,0,0,3,5,1,4],[1,1,0,1,-1,-1,0,4,0,0]))
        stack.pop()
        self.assertEqual(stack[-1], Partition([[5,6],[1,9],[2,4],[7],[3,10],[8]]))
        stack.pop()
        self.assertEqual(stack[-1], Partition([[5,6],[1,9],[2,4],[7],[3,8,10]]))
        stack.pop()
        self.assertEqual(stack[-1], Partition([[3,5,6,8,10],[1,9],[2,4],[7]]))   
        stack.pop()
        self.assertEqual(stack[-1], Partition([[3,5,6,7,8,10],[1,9],[2,4]]))   
        stack.pop()
        self.assertEqual(stack[-1], Partition([[3,5,6,8,10,7],[1,9,2,4]]))   
        stack.pop()
        self.assertEqual(stack[-1], Partition([[1,2,3,4,5,6,7,8,9,10]]))   
        
        raised_error = False
        try:
            stack.pop()
        except IndexError:
            raised_error = True
        self.assertTrue(raised_error)
        
        self.assertEqual(stack[-1], Partition([[1,2,3,4,5,6,7,8,9,10]]))
        self.assertEqual(len(stack), 1)
        
    def test_pop_to_height(self):
        stack = PartitionStack([6,2,4,7,0,0,3,5,1,4],[1,1,0,2,-1,-1,0,4,0,0])
        self.assertEqual(stack[-1], Partition([[5,6],[9],[2],[7],[3,10],[8],[1],[4]]))  
        stack.pop_to_height(2)
        self.assertEqual(stack[-1], Partition([[3,5,6,8,10,7],[1,9,2,4]]))   
        stack.pop_to_height(1)
        self.assertEqual(stack[-1], Partition([[1,2,3,4,5,6,7,8,9,10]]))   
        
        raised_error = False
        try:
            stack.pop_to_height(2)
        except IndexError:
            raised_error = True
        self.assertTrue(raised_error)
        
        self.assertEqual(stack[-1], Partition([[1,2,3,4,5,6,7,8,9,10]]))
        self.assertEqual(len(stack), 1)
        
    def test_canonical_form(self):
        stack = PartitionStack([5,1,2,0,4,6,3],[1,0,1,-1,2,2,0])
        self.assertEqual(stack.canonical_form()[-1],Partition([[1],[3],[5],[2],[7],[4],[6]]))
        stack.pop()
        self.assertEqual(stack.canonical_form()[-1],Partition([[1],[3],[5,6],[2],[7],[4]]))
        self.assertEqual(stack.canonical_form()[-2],Partition([[1],[3,4],[5,6],[2],[7]]))
        self.assertEqual(stack.canonical_form()[-3],Partition([[1],[3,4],[5,6,7],[2]]))
        self.assertEqual(stack.canonical_form()[-4],Partition([[1,2],[3,4],[5,6,7]]))
        self.assertEqual(stack.canonical_form()[-5],Partition([[1,2],[3,4,5,6,7]]))
        self.assertEqual(stack.canonical_form()[-6],Partition([[1,2,3,4,5,6,7]]))
        
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPartition))
    suite.addTest(unittest.makeSuite(TestPartitionStack))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())