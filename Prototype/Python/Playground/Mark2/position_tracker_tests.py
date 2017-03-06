import unittest
from position_tracker import PositionTracker, DynamicPositionTracker

class TestPositionTracker(unittest.TestCase):
    def test_init(self):
        pt = PositionTracker([0,0,0,0,0,3])
        self.assertEqual(pt._cur_state, [0,0,0,0,0,0])     
        
    def test_increment(self):
        pt = PositionTracker([3,2,0,0,1,5,0])
        self.assertEqual(pt._cur_state, [0,0,0,0,0,0,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,0,0,0,0,1,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,0,0,0,0,2,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,0,0,0,0,3,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,0,0,0,0,4,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,1,0,0,0,0,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,1,0,0,0,1,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,1,0,0,0,2,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,1,0,0,0,3,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [0,1,0,0,0,4,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [1,0,0,0,0,0,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [1,0,0,0,0,1,0])
        pt.increment()
        self.assertEqual(pt._cur_state, [1,0,0,0,0,2,0])
        pt.increment(1)
        self.assertEqual(pt._cur_state, [1,1,0,0,0,0,0])
        pt.increment(6)
        self.assertEqual(pt._cur_state, [1,1,0,0,0,1,0])
        pt.increment(5)
        self.assertEqual(pt._cur_state, [1,1,0,0,0,2,0])
        pt.increment(4)
        self.assertEqual(pt._cur_state, [2,0,0,0,0,0,0])
    
    def test_increment_boundry_case(self):
        pt = PositionTracker([0,4,4,0,4,0,0])
        self.assertEqual(pt._cur_state, [0,0,0,0,0,0,0])
        pt.increment(3)
        self.assertEqual(pt._cur_state, [0,0,1,0,0,0,0])
        pt.increment(0)
        self.assertEqual(pt._cur_state, [0,0,0,0,0,0,0])
        pt.increment(4)
        self.assertEqual(pt._cur_state, [0,0,0,0,1,0,0])
        pt.increment(5)
        self.assertEqual(pt._cur_state, [0,0,0,0,2,0,0])
        pt.increment(6)
        self.assertEqual(pt._cur_state, [0,0,0,0,3,0,0])

    def test_getindex(self):
        pt = PositionTracker([2,2,2])
        pt.increment(0)
        pt.increment(2)
        self.assertEqual(pt[0], 1)
        self.assertEqual(pt[1], 0)
        self.assertEqual(pt[2], 1)

    def test_str(self):
        pass
    
class TestDynamicPositionTracker(unittest.TestCase):
    def test_init(self):
        dpt = DynamicPositionTracker()
        
    def test_increment_one_level(self):
        dpt = DynamicPositionTracker()
        self.assertEqual(dpt._cur_state, [])
        dpt.add_level(0)
        dpt.add_level(4)
        self.assertEqual(dpt._cur_state, [0,0])
        dpt.add_level(2)
        dpt.add_level(1)
        dpt.add_level(0)
        dpt.add_level(5)
        self.assertEqual(dpt._cur_state, [0,0,0,0,0,0])
        dpt.increment()
        dpt.increment()
        dpt.increment()
        dpt.increment()
        self.assertEqual(dpt._cur_state, [0,0,0,0,0,4])
        dpt.increment()
        self.assertEqual(dpt._cur_state, [0,0,1])
        dpt.add_level(1)
        dpt.add_level(1)
        dpt.add_level(4)
        self.assertEqual(dpt._cur_state, [0,0,1,0,0,0])
        dpt.increment()
        dpt.increment()
        dpt.increment()
        self.assertEqual(dpt._cur_state, [0,0,1,0,0,3])
        dpt.increment()
        self.assertEqual(dpt._cur_state, [0,1])
        dpt.increment()
        self.assertEqual(dpt._cur_state, [0,2])
        dpt.increment()
        self.assertEqual(dpt._cur_state, [0,3])
        self.assertEqual(dpt.increment(), -1)
        self.assertEqual(dpt._cur_state, [])

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPositionTracker))
    suite.addTest(unittest.makeSuite(TestDynamicPositionTracker))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())