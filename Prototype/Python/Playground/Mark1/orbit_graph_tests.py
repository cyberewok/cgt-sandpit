import unittest
from orbit_graph import OrbitGraph
from group import PermGroup
from permutation import Permutation

class TestOrbitGraph(unittest.TestCase):
    def test_klien4(self):
        a = Permutation.read_cycle_form([[1,2],[3,4]],4)
        b = Permutation.read_cycle_form([[1,3],[2,4]],4)
        G = PermGroup([a,b])
        oG = OrbitGraph(G,(1,2))
        self.assertTrue(tuple(sorted(oG.edges)) == ((1,2),(2,1),(3,4),(4,3)))
        self.assertTrue(oG.ad_list == [[2],[1],[4],[3]])
                
    def test_cyclic6(self):
        b = Permutation.read_cycle_form([[1,2,3,4,5,6]],6)
        G = PermGroup([b])
        oG = OrbitGraph(G,(1,2))
        self.assertTrue(tuple(sorted(oG.edges)) == ((1,2),(2,3),(3,4),(4,5),(5,6),(6,1)))
        self.assertTrue(oG.ad_list == [[2],[3],[4],[5],[6],[1]])
        

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOrbitGraph))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())