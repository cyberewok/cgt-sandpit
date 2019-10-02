import unittest
from cgt.permutation import Permutation
from cgt.partition import PartitionStack
from cgt.group import PermGroup as Group
from cgt.schreier_sims import BaseChanger
from cgt.canonical_conjugate_search import NaiveCanonicalConjugateSearch
from cgt.refinement_manager import OrbitStabaliser
from cgt.canonical_conjugate_search import DiscriminatorManager, UpdatesManager
from cgt.canonical_conjugate_search import canonical_conjugate
from cgt.canonical_conjugate_search import canonical_map
from cgt.canonical_conjugate_search import _canonical_all
#import cgt.canonical_conjugate_search_debug as _debug
_ccsd = _debug.get_class_manager(NaiveCanonicalConjugateSearch)

from cgt.io_perm import read_symmetric_normaliser_file, read_symmetric_normaliser_folder
import _path_tools
import cgt._io_tools as _iot
from cgt._debug_tools import CallCounter

_file_path = lambda x: _iot.get_group(x)
_folder_path = lambda x: _iot.get_groups(x)

class TestNaiveCanonicalSearch(unittest.TestCase):

    def smallest_in_range(self, cands, group):
        best = group.identity, group
        for cand in cands:
            conj = group ** cand
            if conj < best[1]:
                best = cand, conj
        return best
    
    def leaf_check(self, group, norm):
        _ccsd.disable_all()
        _ccsd.enable_features(["ind"])
        size = group.degree
        c = CallCounter("process_leaf", NaiveCanonicalConjugateSearch)
        def fac(x):
            if x < 1:
                return 1
            return x * fac(x - 1)
        canonical_map(group, norm)        
        self.assertTrue(fac(size) / norm.order(), c.count)
        _ccsd.apply_default()
        
    
    def leaf_invarience_check(self, cands, G, N):
        searcher = NaiveCanonicalConjugateSearch(G, N)
        searcher_group = searcher.conjugate_representative()
        parts = searcher._canonical_partition
        
        for cand in cands:
            conj = parts ** cand
            perm = searcher.get_permutation(conj)
            cand_group = G**perm
            self.assertEqual(cand_group, searcher_group)
            #self.assertEqual(cand_group, G)
            #self.assertEqual(cand_group.canonical_generators(), searcher_group.canonical_generators())
            
    
    def chain_check(self, group, norm = None, depth = 2, mods = None):
        if norm is None:
            norm = group
        prev = None
        for _ in range(depth):
            can_map = canonical_map(group, norm)
            can_group = group ** can_map
            can_norm = norm ** can_map
            if prev is not None:
                pass
                self.assertEqual(prev.canonical_generators(), can_group.canonical_generators())
            prev = can_group
            if mods is not None:
                for mod in mods:
                    mod.reset()            
            
    def light_conjugate_test(self, cands, group, norm, mods = None):
        _ccsd.enable_all()
        best_group = canonical_conjugate(group, norm)
        if mods is not None:
            for mod in mods:
                mod.reset()  
        for cand in cands:
            conj = group ** cand
            conj_norm = norm ** cand
            best_group_cand = canonical_conjugate(conj, conj_norm)
            gens = best_group_cand.generators
            for gen in gens:
                self.assertTrue(gen in best_group)
            if mods is not None:
                for mod in mods:
                    mod.reset()
        _ccsd.apply_default()        
            
       #print(best_group.generators)
    
    #def test_canonical_conjugate_small(self):
        ##this is a bad test as it ttests for smallest in range not smallest.
        #_ccsd.disable_all()
        #_ccsd.enable_features(["ind"])
        #size = 6
        #cf = lambda x: Permutation.read_cycle_form(x, size)
        #a = cf([[2,4,5,6]])
        #b = cf([[1,2]])
        #c = cf([list(range(1, size + 1))])
        #test_group = Group.fixed_base_group([a],list(range(1, size + 1)))
        #S6 = Group([b,c])
        #best_group_act = self.smallest_in_range(S6._list_elements(), test_group)[1]
        #best_group_search = canonical_conjugate(test_group, test_group)
        #self.assertFalse(best_group_act < best_group_search)
        #self.assertFalse(best_group_search < best_group_act)
        #self.assertEqual
        #(
            #list(best_group_search.canonical_generators()),
            #list(best_group_act.canonical_generators())
        #)
        #_ccsd.apply_default()


    def test_canonical_conjugate_small2(self):
        size = 6
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[2,4,5,6]])
        b = cf([[1,2]])
        c = cf([list(range(1, size + 1))])
        test_group = Group.fixed_base_group([a],list(range(1, size + 1)))
        S6 = Group([b,c])
        self.light_conjugate_test(S6._list_elements()[17:19], test_group, test_group)
        self.chain_check(test_group)
    
    def test_canonical_conjugate_K4(self):
        size = 6
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[2,4],[5,6]])
        b = cf([[2,5],[4,6]])
        c = cf([[1,2]])
        d = cf([list(range(1, size + 1))])
        test_group = Group.fixed_base_group([a,b],list(range(1, size + 1)))
        S6 = Group([c,d])
        self.light_conjugate_test(S6._list_elements()[47:47], test_group, test_group)
        self.chain_check(test_group)
   
    def test_very_small(self):
        size = 5
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[2,3,4]])
        G = Group.fixed_base_group([a],[])
        N = Group.fixed_base_group([a],[])
        #print(G._list_elements())
        #print(N._list_elements())
        self.leaf_check(G,N)
        size = G.degree
        b = cf([[3,5,4,1]])
        self.light_conjugate_test([a], G, N)
        self.chain_check(G, N)
        #c = CallCounter("process_leaf", NaiveCanonicalConjugateSearch)        
        #self.light_conjugate_test([a], G, N, mods = [c])
        #self.chain_check(G, N, mods = [c])
    
    def test_osg10(self):
        file = _file_path("osg10test1.txt")        
        G, N = read_symmetric_normaliser_file(file)
        
        #print(G._list_elements())
        #print(N._list_elements())
        size = G.degree
        cf = lambda x: Permutation.read_cycle_form(x, size)
        c = CallCounter("process_leaf", NaiveCanonicalConjugateSearch)        
        a = cf([[2,5,3]])
        self.light_conjugate_test([a], G, N, mods = [c])
        self.chain_check(G, N, mods = [c])
        #print(c.count_history)

    def test_osg10_leaf(self): 
        file = _file_path("osg10test1.txt")        
        G, N = read_symmetric_normaliser_file(file)
        self.leaf_check(G,N)

    
    def test_C8_leaf_invarience(self):
        _ccsd.apply_default()            
        _ccsd.disable_features(["ind"])
        size = 8
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[1,3,5,7]])
        file = _file_path("AllSmallGroups10/8_1.txt")        
        G, N = read_symmetric_normaliser_file(file)
        self.leaf_invarience_check(N._list_elements(), G, N)
        #self.leaf_invarience_check(N._list_elements(), G**a, N**a)
        _ccsd.apply_default()        
    
    #def test_osg1
    
    
    def test_canonical_chain_small(self):
        size = 6
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[2,4,5,6]])
        b = cf([[1,2]])
        c = cf([list(range(1, size + 1))])
        test_group = Group.fixed_base_group([a],list(range(1, size + 1)))
        S6 = Group([b,c])
        self.light_conjugate_test(S6._list_elements()[17:19], test_group, test_group)        
        
    
    def test_wp33(self):
        #enable_cull()
        file = _file_path("wp33.txt")        
        G, N = read_symmetric_normaliser_file(file)
        size = G.degree
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[2,5,3]])
        self.chain_check(G,N)
        self.light_conjugate_test([a], G, N)
        
    def test_12_4(self):
        #enable_cull()
        file = _file_path("AllSmallGroups96/12_4.txt")        
        G, N = read_symmetric_normaliser_file(file)
        size = G.degree
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[2,5,3]])
        self.chain_check(G,N)
        self.light_conjugate_test([a], G, N)    
        
    #def test_wp103(self):
        #file = _file_path("wp103.txt")        
        #G, N = read_symmetric_normaliser_file(file)
        #size = G.degree
        #cf = lambda x: Permutation.read_cycle_form(x, size)
        #a = cf([[2,5,3]])
        #self.light_conjugate_test([a], G, N) 
        
    def test_all_small_groups_7(self):
        folder = _folder_path("AllSmallGroups7")
        tups = read_symmetric_normaliser_folder(folder)
        prev = 0
        for G, N in tups:
            size = G.degree
            if G.order() > prev:
                count = 1
            else:
                count += 1
            prev = G.order()
            #print("{}, {}-{}".format(size,G.order(), count))
            cf = lambda x: Permutation.read_cycle_form(x, size)
            a = cf([list(range(1,size,max(size//7, 2)))])
            self.light_conjugate_test([a], G, N)
            self.chain_check(G,N)
        
        
        
    def test_all_small_groups_10(self):
        folder = _folder_path("AllSmallGroups10")
        tups = read_symmetric_normaliser_folder(folder)
        prev = 0
        for G, N in tups:
            size = G.degree
            if G.order() > prev:
                count = 1
            else:
                count += 1
            prev = G.order()
            #print("{}, {}-{}".format(size,G.order(), count))
            cf = lambda x: Permutation.read_cycle_form(x, size)    
            a = cf([])
            c = cf([[2,min(size, 5),1]])
            b = cf([list(range(1,size,max(size//7, 2)))])
            d = cf([[1,2]])
            to_check = [a,b,c,d]
            #to_check = [b]            
            self.light_conjugate_test(to_check, G, N)
            self.chain_check(G,N)  
            
    
    def test_all_small_groups_10_random(self):
        folder = _folder_path("AllSmallGroups10")
        tups = read_symmetric_normaliser_folder(folder)
        prev = 0
        for G, N in tups:
            size = G.degree
            if G.order() > prev:
                count = 1
            else:
                count += 1
            prev = G.order()
            #print("{}, {}-{}".format(size,G.order(), count))
            cf = lambda x: Permutation.read_cycle_form(x, size)    
            a = cf([])
            c = cf([[2,min(size, 5),1]])
            b = cf([list(range(1,size,max(size//7, 2)))])
            d = cf([[1,2]])
            e = cf([list(range(1,size + 1))])
            to_check = [a,d,e]
            rand_limit = 5
            s_n = Group.fixed_base_group([d,e])
            randoms = [s_n._rand_element() for _ in range(rand_limit)]
            to_check.extend(randoms)
            #to_check = [b]            
            self.light_conjugate_test(to_check, G, N)
            self.chain_check(G,N)
            
    def test_all_small_groups_20_random(self):
        folder = _folder_path("AllSmallGroups10")
        #folder = _folder_path("AllSmallGroups10")        
        tups = read_symmetric_normaliser_folder(folder)
        prev = 0
        for G, N in tups:
            size = G.degree
            if G.order() > prev:
                count = 1
            else:
                count += 1
            prev = G.order()
            #print("{}, {}-{}".format(size,G.order(), count))
            cf = lambda x: Permutation.read_cycle_form(x, size)    
            a = cf([])
            c = cf([[2,min(size, 5),1]])
            b = cf([list(range(1,size,max(size//7, 2)))])
            d = cf([[1,2]])
            e = cf([list(range(1,size + 1))])
            to_check = [a,d,e]
            rand_limit = 5
            s_n = Group.fixed_base_group([d,e])
            randoms = [s_n._rand_element() for _ in range(rand_limit)]
            to_check.extend(randoms)
            #to_check = [b]            
            self.light_conjugate_test(to_check, G, N)
            self.chain_check(G,N) 
    
    def partition_stabaliser_test(self):
        #[1,2,3],[4,5,6],[7,8,9]
        #[1,2,3]
        #[1][4,5,6][7,8,9][2,3]
        #[1][2,3]
        pass
    

class TestUpdatesManager(unittest.TestCase):
    def test_len(self):
        degree = 5
        ps = PartitionStack([0] * degree, [-1] * degree)
        uc = UpdatesManager(ps)
        self.assertEqual(len(uc), 1)
        ps = PartitionStack([0,1,2],[-1,0,0])
        uc = UpdatesManager(ps)
        self.assertEqual(len(uc), 3)
        
    def test_multi_add(self):
        degree = 5
        ps = PartitionStack([0] * degree, [-1] * degree)
        uc = UpdatesManager(ps)
        self.assertTrue(uc.multi_add(lambda x: 2 if x in [1,3] else 1))
        self.assertEqual(ps, PartitionStack([1,0,1,0,0],[0,-1,0,-1,-1]))
        self.assertEqual(len(uc),2)
        self.assertTrue(uc.multi_add(lambda x: x if x <= 3 else 0))
        self.assertEqual(len(uc),4)
        self.assertFalse(uc.multi_add(lambda x: x if x <= 2 else 0))
        self.assertEqual(len(uc),4)
        self.assertEqual(ps, PartitionStack([1,2,3,0,0],[0,0,1,-1,-1]))
    
    def test_single_add(self):
        degree = 5
        ps = PartitionStack([0] * degree, [-1] * degree)
        uc = UpdatesManager(ps)
        uc.single_add(0,3)
        self.assertEqual(ps, PartitionStack([0,0,1,0,0],[-1,-1,0,-1,-1]))
        uc.single_add(0,5)
        self.assertEqual(ps, PartitionStack([0,0,1,0,2],[-1,-1,0,-1,0])) 
    
    def test_full_run(self):
        degree = 5
        ps = PartitionStack([0] * degree, [-1] * degree)
        uc = UpdatesManager(ps)
        self.assertTrue(uc.multi_add(lambda x: 2 if x in [1,3] else 1))
        self.assertEqual(ps, PartitionStack([1,0,1,0,0],[0,-1,0,-1,-1]))
        self.assertEqual(uc.report_changes(0),([[1,3]],1))
        self.assertTrue(uc.multi_add(lambda x: x if x <= 3 else 0))
        self.assertFalse(uc.multi_add(lambda x: x if x <= 2 else 0))
        self.assertEqual(ps, PartitionStack([1,2,3,0,0],[0,0,1,-1,-1]))
        self.assertEqual(uc.report_changes(0),([[1,3],[2],[3]],2))
        self.assertEqual(uc.report_changes(1),([[2],[3]],2))
        self.assertEqual(uc.report_changes(2),([],2))
        self.assertEqual(uc.report_changes(None,1),([[1,3],[2],[3]],2))
        self.assertEqual(uc.report_changes(None,2),([[2],[3]],2))
        self.assertEqual(uc.report_changes(None,3),([[3]],2))
        self.assertEqual(len(uc), 4)
        ps.pop()
        uc.multi_remove()
        self.assertEqual(len(uc), 3)        
        uc.single_add(1, 3)
        self.assertEqual(len(uc), 4)
        self.assertEqual(uc.last_pop_height(0),1)
        self.assertEqual(uc.last_pop_height(1),2)
        self.assertEqual(uc.last_pop_height(2),3)
        self.assertEqual(uc.last_pop_height(3),3)
        self.assertEqual(uc.last_pop_height(4),4)        
        #single add
        #multi remove
        #len
        #fix
        #fix_info
        #report_changes

class TestOrbitStabaliser(unittest.TestCase):
    def full_run_through(self, G):
        ps = PartitionStack([0] * G.degree, [-1] * G.degree)
        bc = BaseChanger(G)
        dm = DiscriminatorManager()
        uc = UpdatesManager(ps)
        a = OrbitStabaliser(bc,uc,dm)
        #is trasitive
        self.assertEqual(len(bc.orbits()), 1)
        self.assertFalse(a.refine(ps))
        uc.multi_add(lambda x: 1 if x in [1] else 2)
        bc.change_base(uc.fix())
        self.assertEqual(len(bc.orbits()), 5)
        self.assertTrue(a.refine(ps))
        
    def test_wp33_full_run(self):
        file = _file_path("wp33.txt")        
        G, N = read_symmetric_normaliser_file(file)
        size = G.degree
        self.full_run_through(G)        
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[2,5,3]])
        
    
    
def all_tests_suite():
    _ccsd.apply_default()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNaiveCanonicalSearch))
    suite.addTest(unittest.makeSuite(TestOrbitStabaliser))
    suite.addTest(unittest.makeSuite(TestUpdatesManager))
    #suite.addTest(TestNaiveCanonicalSearch("test_all_small_groups_10"))
    #suite.addTest(TestNaiveCanonicalSearch("test_very_small"))
    #suite.addTest(TestNaiveCanonicalSearch("test_osg10"))
    #suite.addTest(TestNaiveCanonicalSearch("test_osg10_leaf"))
    #suite.addTest(TestNaiveCanonicalSearch("test_C8_leaf_invarience"))
    #suite.addTest(TestOrbitStabaliser("test_wp33_full_run"))
    #suite.addTest(TestUpdatesManager("test_full_run"))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())