import unittest
from cgt.permutation import Permutation
from cgt.group import PermGroup as Group
from cgt.io_perm import read_group_file, read_symmetric_normaliser_file
from cgt.io_perm import read_group_folder, read_symmetric_normaliser_folder
from cgt.io_perm import GroupFileReader
#import _path_tools
import _io_tools as pt

_fp = lambda x: pt.get_group(x)
_fps = lambda x: pt.get_groups(x)

class TestGroupInformation(unittest.TestCase):

    
    def test_small_read(self):
        file = _fp("55wp.txt")
        G = read_group_file(file)
        self.assertEqual(G.order(), 15625)
        self.assertEqual(G.degree, 125)
        G, N = read_symmetric_normaliser_file(file)
        self.assertEqual(G.order(), 15625)        
        self.assertEqual(N.order(), 312500)

class TestGroupFileReader(unittest.TestCase):
    
    def test_read_groups_folder(self):
        folder = _fps("AllSmallGroups10")
        count = 0
        for G in read_group_folder(folder):
            count += 1
            self.assertTrue(G.order() > 0)
        self.assertEqual(count, 17)

    def test_read_normaliser_folder(self):
        folder = _fps("AllSmallGroups10")
        count = 0
        for G, N in read_symmetric_normaliser_folder(folder):
            count += 1
            self.assertTrue(G.order() > 0)
            self.assertTrue(N.order() > 0)
        self.assertEqual(count, 17)
    
    def test_consume_line(self):
        file = _fp("55wp.txt")
        o_file = open(file, 'r')
        gfr = GroupFileReader(o_file)
        gfr.read_all()
        o_file.close()
        #self.assertFalse(best_group_act < best_group_search)
    
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGroupFileReader))
    suite.addTest(unittest.makeSuite(TestGroupInformation))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())