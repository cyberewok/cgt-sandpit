import unittest
from group import PermGroup as Group
from ordering import ordering_to_perm_key, ordering_to_key
from permutation import Permutation
from schreier_structure import DirectSchreierStructure, GraphSchreierStructure
from schreier_sims_randomised import RandomSchreierGenerator
from schreier_sims import get_schreier_structure

class TestSchreierStructure(unittest.TestCase):
    def test_random_element(self):
        degree = 10
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3],[4,5],[8,9]])
        b = cf([[3,4],[5,8],[9,10,2]])        
        struct = get_schreier_structure([a,b])
        for _ in range(100):
            self.assertTrue(struct.random_element() in struct)

class TestDirectSchreierStructure(unittest.TestCase):
    def sift_test(self, to_check, to_pass, structure):
        to_check = set(to_check)
        to_pass = set(to_pass)
        for g in to_check:
            if g in to_pass:
                siftee = structure.siftee(g)
                self.assertTrue(siftee.trivial())
            else:
                siftee = structure.siftee(g)
                if siftee is not None:    
                    self.assertFalse(siftee.trivial())
                    
    def image_works_test(self, image, struct):
        ele = struct.element_from_image(image)
        self.assertTrue(ele is not None)
        for index, image_cand in enumerate(image):
            self.assertEqual(struct.base_at_level(index)**ele, image_cand)
        self.assertTrue(ele in struct)      
                
    def test_init(self):
        ss = DirectSchreierStructure(10)
        ss = DirectSchreierStructure(2)
    
    def test_add_level(self):
        ss = DirectSchreierStructure(10)
        ss.add_level(1)
        self.assertEqual(ss.base_till_level(1), [1])
        self.assertEqual(ss.base_till_level(), [1])
        ss.add_level(2)
        self.assertEqual(ss.base_till_level(1), [1])
        self.assertEqual(ss.base_till_level(), [1,2])
        ss.add_level(3)
        ss.add_level(4)
        ss.add_level(5)
        ss.add_level(6)
        ss.add_level(7)
        self.assertEqual(ss.base_till_level(4), [1,2,3,4])
        self.assertEqual(ss.base_till_level(), [1,2,3,4,5,6,7])
        ss.add_level(8)
        ss.add_level(9)
        self.assertEqual(len(ss.stabaliser_orbit(0)), 1)
        self.assertEqual(len(ss.stabaliser_orbit(5)), 1)
        self.assertEqual(len(ss.stabaliser_orbit(8)), 1)
    
    def test_extend_level(self):
        degree = 10
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3],[4,5],[8,9]])
        b = cf([[3,4],[5,8],[9,10,2]])
        ss = DirectSchreierStructure(degree)
        ss.add_level(1)
        updated = ss.extend_level(b, 0, force_update = False)
        self.assertFalse(updated)
        updated = ss.extend_level(a, 0, force_update = False)
        self.assertTrue(updated)
        updated = ss.extend_level(cf([]), 0, force_update = False)
        self.assertFalse(updated)      
        updated = ss.extend_level(a**-1, 0, force_update = False)
        self.assertFalse(updated)
        reps = [x for x in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 3)
        self.assertEqual(ss.chain_generators[0], [a])
        self.assertEqual(set([1,2,3]) - ss.stabaliser_orbit(0), set())
        
        updated = ss.extend_level(b, 0, force_update = False)     
        self.assertTrue(updated)
        reps = [x for x in ss.schreier_graphs[0] if x is not None]
        #print(reps)
        self.assertEqual(len(reps), 8)
        self.assertEqual(ss.chain_generators[0], [a,b])
        self.assertEqual(set([1,2,3,4,5,8,9,10]) - ss.stabaliser_orbit(0), set())          
    
    def test_extend_level_edge_cases(self):
        #Doesn't really do anything at the momement
        degree = 15
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3],[4,5],[8,9]])
        b = cf([[3,4],[5,8],[14,15]])
        c = cf([[9,10,11,4],[14,13,12,8]])
        ss = DirectSchreierStructure(degree)
        ss.add_level(1)
        updated = ss.extend_level(b, 0, force_update = False)
        self.assertFalse(updated)
        updated = ss.extend_level(cf([]), 0, force_update = False)
        self.assertFalse(updated)      
        updated = ss.extend_level(a, 0, force_update = False)
        self.assertTrue(updated)
        reps = [x for x in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 3)
        self.assertEqual(set([1,2,3]) - ss.stabaliser_orbit(0), set())
        
        updated = ss.extend_level(b, 0, force_update = False)      
        self.assertTrue(updated)
        reps = [x for x in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 7)
        self.assertEqual(set([1,2,3,4,5,8,9]) - ss.stabaliser_orbit(0), set())
        
        updated = ss.extend_level(c, 0, force_update = False)      
        self.assertTrue(updated)
        reps = [x for x in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 13)
        self.assertEqual(set([1,2,3,4,5,8,9,10,11,12,13,14,15]) - ss.stabaliser_orbit(0), set()) 
        self.assertEqual(ss.chain_generators[0], [a,b,c])
        
    def test_sift_on_level(self):
        degree = 20
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3],[4,5],[8,9]])
        b = cf([[3,4],[5,8],[14,15]])
        c = cf([[9,10,11,4],[14,13,12,8]])
        ss = DirectSchreierStructure(degree)
        ss.add_level(2)
        ss.extend_level(a, 0)
        ss.extend_level(b, 0)
        ss.extend_level(c, 0)
        
        for i in [x for x in range(1, 16) if x not in [2,6,7]]:
            d = cf([[2,i]])        
            siftee = ss.sift_on_level(d,0)
            self.assertEqual(2**siftee, 2)
        
        for i in [6,7]:
            d = cf([[2,i]])        
            siftee = ss.sift_on_level(d,0)
            self.assertTrue(siftee is None)
            
    def test_sift(self):
        degree = 6
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3,4,5,6]])
        b = cf([[1,2]])
        S6 = Group([a,b])._list_elements()
        a = cf([[1,3,4,5,6]])
        b = cf([[1,4,6]])
        A5 = Group([a,b])._list_elements()
        rg = get_schreier_structure([a,b], order = 360)
        self.sift_test(S6, A5, rg)
    
    #def test_base_image_member(self):
        #cf  =Permutation.read_cycle_form
        #a = cf([[1, 2]],4)
        #b = cf([[1,2,3,4]], 4)
        #c = cf([[2,3]], 4)
        #e = cf([],4)
        #base, gens, c_gens, graphs = schreier_sims_algorithm_fixed_base([a,b],[1,2,3,4], e)
        #self.assertEqual(base_image_member(base,[1,3,2],graphs,e), c)
    
    def test_element_at_index(self):
        cf  = Permutation.read_cycle_form
        a = cf([[1, 2, 3,4,5]],5)
        b = cf([[1,2,3]], 5)
        e = cf([],5)
        ordering = [3,5,2,1,4]
        full_group = []
        ele_key = ordering_to_key(ordering)        
        perm_key = ordering_to_perm_key(ordering)
        struct = get_schreier_structure([a,b], base = ordering)
        for index in range(struct.order()):
            full_group.append(struct.element_at_index(index, key=ele_key))
        ordered_group = sorted(list(full_group), key = perm_key)
        #for x,y in zip(full_group, ordered_group):
            #print("{!s:<20} {!s:<20}".format(x,y))
        self.assertEqual(len(set(full_group)), struct.order())
        self.assertEqual(full_group, ordered_group)
        
    
    def test_memebership_index(self):
        cf  = Permutation.read_cycle_form
        a = cf([[1, 2, 3,4,5]],5)
        b = cf([[1,2,3]], 5)
        c = cf([[1,2]], 5)
        e = cf([],5)
        ordering = [3,5,2,1,4]#[1,2,3,4,5]#
        struct = get_schreier_structure([a,b], base = ordering)
        S5_struct = get_schreier_structure([a,c], base = ordering)
        real_group = []
        S5_group = []
        
        ele_key = ordering_to_key(ordering)        
        perm_key = ordering_to_perm_key(ordering)
        
        for index in range(S5_struct.order()):
            to_add = S5_struct.element_at_index(index, key=ele_key)
            index_check = S5_struct.membership_index(to_add, key=ele_key)
            self.assertEqual(index, index_check)
            #print("{}: {} {}".format(to_add, index, index_check))
            S5_group.append(to_add)
         
        self.assertEquals(len(set(S5_group)), 120)
        self.assertEquals(S5_group, sorted(S5_group, key = perm_key))
        
        prev = None
        for index in range(struct.order()):
            to_add = struct.element_at_index(index, key=ele_key)
            index_check = struct.membership_index(to_add, key=ele_key)
            self.assertEqual(index, index_check)
            real_group.append(to_add)
            if prev is not None:
                index_beg = S5_struct.membership_index(prev, key=ele_key)
                index_end = S5_struct.membership_index(to_add, key=ele_key)
                self.assertTrue(index_beg < index_end)
                
            prev = to_add
            
             
        self.assertEquals(len(set(real_group)), 60)
        self.assertEquals(real_group, sorted(real_group, key = perm_key))
        
        for ele in S5_group:
            cand_index = struct.membership_index(ele, key=ele_key)
            if ele in struct:
                #print("{}: {} {}?".format(cand_index, ele, real_group[cand_index]))
                self.assertTrue(ele in real_group)
                self.assertEquals(real_group[cand_index], ele)
            else:
                a_ele = struct.element_at_index(cand_index, key = ele_key)
                c_ele = a_ele
                pre_ele = a_ele
                if cand_index + 1 < struct.order():
                    c_ele = struct.element_at_index(cand_index + 1, key = ele_key)
                if cand_index > 0:
                    pre_ele = struct.element_at_index(cand_index - 1, key = ele_key)
                
                pre = S5_struct.membership_index(pre_ele, key=ele_key)
                a = S5_struct.membership_index(a_ele, key=ele_key)
                b = S5_struct.membership_index(ele, key=ele_key)
                c = S5_struct.membership_index(c_ele, key=ele_key)
                
                self.assertFalse(ele in real_group)
                #print("{} {} {}: {}".format(pre_ele, a_ele, c_ele, ele))
                #print("{} {} {}: {}".format(pre,a,c,b))
                self.assertTrue(pre <= b <= c)
                self.assertTrue(pre <= a <= c )
        
    def test_element_from_image(self):
        cf  = lambda x:Permutation.read_cycle_form(x, 5)
        a = cf([[1, 2, 3,4,5]])
        b = cf([[1,2,3]])
        c = cf([[1,2]])
        e = cf([])
        cand_base = [3,5,2,1,4]
        cyc_struct = get_schreier_structure([a], base = cand_base)
        self.image_works_test([4], cyc_struct)
        A5_struct = get_schreier_structure([a,b], base = cand_base)
        self.image_works_test([1,2,3], A5_struct)
        self.image_works_test([3,5,1], A5_struct)
        #print(A5_struct.element_from_image([3,5,1]))
        S5_struct = get_schreier_structure([a,c], base = cand_base)
        self.image_works_test([1,2,3], S5_struct)
        self.image_works_test([3,4,5,1], S5_struct)
    
    def rand_element(self):
        pass

class TestGraphSchreierStructure(unittest.TestCase):
    def sift_test(self, to_check, to_pass, structure):
        to_check = set(to_check)
        to_pass = set(to_pass)
        for g in to_check:
            if g in to_pass:
                siftee = structure.siftee(g)
                self.assertTrue(siftee.trivial())
            else:
                siftee = structure.siftee(g)
                if siftee is not None:    
                    self.assertFalse(siftee.trivial())
                    
    def image_works_test(self, image, struct):
        ele = struct.element_from_image(image)
        self.assertTrue(ele is not None)
        for index, image_cand in enumerate(image):
            self.assertEqual(struct.base_at_level(index)**ele, image_cand)
        self.assertTrue(ele in struct)      
                
    def test_init(self):
        ss = GraphSchreierStructure(10)
        ss = GraphSchreierStructure(2)
    
    def test_add_level(self):
        ss = GraphSchreierStructure(10)
        ss.add_level(1)
        self.assertEqual(ss.base_till_level(1), [1])
        self.assertEqual(ss.base_till_level(), [1])
        ss.add_level(2)
        self.assertEqual(ss.base_till_level(1), [1])
        self.assertEqual(ss.base_till_level(), [1,2])
        ss.add_level(3)
        ss.add_level(4)
        ss.add_level(5)
        ss.add_level(6)
        ss.add_level(7)
        self.assertEqual(ss.base_till_level(4), [1,2,3,4])
        self.assertEqual(ss.base_till_level(), [1,2,3,4,5,6,7])
        ss.add_level(8)
        ss.add_level(9)
        self.assertEqual(len(ss.stabaliser_orbit(0)), 1)
        self.assertEqual(len(ss.stabaliser_orbit(5)), 1)
        self.assertEqual(len(ss.stabaliser_orbit(8)), 1)
    
    def test_internal_extend_level_single(self):
        degree = 10
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        ss = GraphSchreierStructure(degree)
        ss.add_level(1)
        reps = [x for x,_,_ in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 1)        
        updated, front = ss._extend_level_single(cf([[1,2,3],[4,5]]), 0)
        self.assertTrue(updated)
        self.assertEqual(front, [2,3])
        reps = [x**n for x,n,_ in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 3)
    
    def test_extend_level(self):
        degree = 10
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3],[4,5],[8,9]])
        b = cf([[3,4],[5,8],[9,10,2]])
        ss = GraphSchreierStructure(degree)
        ss.add_level(1)
        updated = ss.extend_level(b, 0)
        self.assertFalse(updated)
        updated = ss.extend_level(a, 0)
        self.assertTrue(updated)
        updated = ss.extend_level(cf([]), 0)
        self.assertFalse(updated)      
        updated = ss.extend_level(a**-1, 0)
        self.assertFalse(updated)
        reps = [x**n for x,n,_ in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 3)
        self.assertEqual(ss.chain_generators[0], [a])
        self.assertEqual(set([1,2,3]) - ss.stabaliser_orbit(0), set())
        
        updated = ss.extend_level(b, 0)      
        self.assertTrue(updated)
        reps = [x**n for x,n,_ in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 8)
        self.assertEqual(ss.chain_generators[0], [a,b])
        self.assertEqual(set([1,2,3,4,5,8,9,10]) - ss.stabaliser_orbit(0), set())          
    
    def test_extend_level_edge_cases(self):
        #Doesn't really do anything at the momement
        degree = 15
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3],[4,5],[8,9]])
        b = cf([[3,4],[5,8],[14,15]])
        c = cf([[9,10,11,4],[14,13,12,8]])
        ss = GraphSchreierStructure(degree)
        ss.add_level(1)
        updated = ss.extend_level(b, 0)
        self.assertFalse(updated)
        updated = ss.extend_level(cf([]), 0)
        self.assertFalse(updated)      
        updated = ss.extend_level(a, 0)
        self.assertTrue(updated)
        reps = [x**n for x,n,_ in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 3)
        self.assertEqual(set([1,2,3]) - ss.stabaliser_orbit(0), set())
        
        updated = ss.extend_level(b, 0)      
        self.assertTrue(updated)
        reps = [x**n for x,n,_ in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 7)
        self.assertEqual(set([1,2,3,4,5,8,9]) - ss.stabaliser_orbit(0), set())
        
        updated = ss.extend_level(c, 0)      
        self.assertTrue(updated)
        reps = [x**n for x,n,_ in ss.schreier_graphs[0] if x is not None]
        self.assertEqual(len(reps), 13)
        self.assertEqual(set([1,2,3,4,5,8,9,10,11,12,13,14,15]) - ss.stabaliser_orbit(0), set()) 
        self.assertEqual(ss.chain_generators[0], [a,b,c])
        
    def test_sift_on_level(self):
        degree = 20
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3],[4,5],[8,9]])
        b = cf([[3,4],[5,8],[14,15]])
        c = cf([[9,10,11,4],[14,13,12,8]])
        ss = GraphSchreierStructure(degree)
        ss.add_level(2)
        ss.extend_level(a, 0)
        ss.extend_level(b, 0)
        ss.extend_level(c, 0)
        
        for i in [x for x in range(1, 16) if x not in [2,6,7]]:
            d = cf([[2,i]])        
            siftee = ss.sift_on_level(d,0)
            self.assertEqual(2**siftee, 2)
        
        for i in [6,7]:
            d = cf([[2,i]])        
            siftee = ss.sift_on_level(d,0)
            self.assertTrue(siftee is None)
            
    def test_sift(self):
        degree = 6
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        a = cf([[1,2,3,4,5,6]])
        b = cf([[1,2]])
        S6 = Group([a,b])._list_elements()
        a = cf([[1,3,4,5,6]])
        b = cf([[1,4,6]])
        A5 = Group([a,b])._list_elements()
        rg = RandomSchreierGenerator([a,b], group_order = 360)
        rg.complete_till_level(degree)        
        self.sift_test(S6, A5, rg.structure)
    
    #def test_base_image_member(self):
        #cf  =Permutation.read_cycle_form
        #a = cf([[1, 2]],4)
        #b = cf([[1,2,3,4]], 4)
        #c = cf([[2,3]], 4)
        #e = cf([],4)
        #base, gens, c_gens, graphs = schreier_sims_algorithm_fixed_base([a,b],[1,2,3,4], e)
        #self.assertEqual(base_image_member(base,[1,3,2],graphs,e), c)
    
    def test_element_at_index(self):
        cf  = Permutation.read_cycle_form
        a = cf([[1, 2, 3,4,5]],5)
        b = cf([[1,2,3]], 5)
        e = cf([],5)
        ordering = [3,5,2,1,4]
        full_group = []
        ele_key = ordering_to_key(ordering)        
        perm_key = ordering_to_perm_key(ordering)
        struct = get_schreier_structure([a,b], base = ordering)
        for index in range(struct.order()):
            full_group.append(struct.element_at_index(index, key=ele_key))
        ordered_group = sorted(list(full_group), key = perm_key)
        #for x,y in zip(full_group, ordered_group):
            #print("{!s:<20} {!s:<20}".format(x,y))
        self.assertEqual(len(set(full_group)), struct.order())
        self.assertEqual(full_group, ordered_group)
        
    
    def test_memebership_index(self):
        cf  = Permutation.read_cycle_form
        a = cf([[1, 2, 3,4,5]],5)
        b = cf([[1,2,3]], 5)
        c = cf([[1,2]], 5)
        e = cf([],5)
        ordering = [3,5,2,1,4]#[1,2,3,4,5]#
        struct = get_schreier_structure([a,b], base = ordering)
        S5_struct = get_schreier_structure([a,c], base = ordering)
        real_group = []
        S5_group = []
        
        ele_key = ordering_to_key(ordering)        
        perm_key = ordering_to_perm_key(ordering)
        
        for index in range(S5_struct.order()):
            to_add = S5_struct.element_at_index(index, key=ele_key)
            index_check = S5_struct.membership_index(to_add, key=ele_key)
            self.assertEqual(index, index_check)
            #print("{}: {} {}".format(to_add, index, index_check))
            S5_group.append(to_add)
         
        self.assertEquals(len(set(S5_group)), 120)
        self.assertEquals(S5_group, sorted(S5_group, key = perm_key))
        
        prev = None
        for index in range(struct.order()):
            to_add = struct.element_at_index(index, key=ele_key)
            index_check = struct.membership_index(to_add, key=ele_key)
            self.assertEqual(index, index_check)
            real_group.append(to_add)
            if prev is not None:
                index_beg = S5_struct.membership_index(prev, key=ele_key)
                index_end = S5_struct.membership_index(to_add, key=ele_key)
                self.assertTrue(index_beg < index_end)
                
            prev = to_add
            
             
        self.assertEquals(len(set(real_group)), 60)
        self.assertEquals(real_group, sorted(real_group, key = perm_key))
        
        for ele in S5_group:
            cand_index = struct.membership_index(ele, key=ele_key)
            if ele in struct:
                #print("{}: {} {}?".format(cand_index, ele, real_group[cand_index]))
                self.assertTrue(ele in real_group)
                self.assertEquals(real_group[cand_index], ele)
            else:
                a_ele = struct.element_at_index(cand_index, key = ele_key)
                c_ele = a_ele
                pre_ele = a_ele
                if cand_index + 1 < struct.order():
                    c_ele = struct.element_at_index(cand_index + 1, key = ele_key)
                if cand_index > 0:
                    pre_ele = struct.element_at_index(cand_index - 1, key = ele_key)
                
                pre = S5_struct.membership_index(pre_ele, key=ele_key)
                a = S5_struct.membership_index(a_ele, key=ele_key)
                b = S5_struct.membership_index(ele, key=ele_key)
                c = S5_struct.membership_index(c_ele, key=ele_key)
                
                self.assertFalse(ele in real_group)
                #print("{} {} {}: {}".format(pre_ele, a_ele, c_ele, ele))
                #print("{} {} {}: {}".format(pre,a,c,b))
                self.assertTrue(pre <= b <= c)
                self.assertTrue(pre <= a <= c )
        
    def test_element_from_image(self):
        cf  = lambda x:Permutation.read_cycle_form(x, 5)
        a = cf([[1, 2, 3,4,5]])
        b = cf([[1,2,3]])
        c = cf([[1,2]])
        e = cf([])
        cand_base = [3,5,2,1,4]
        cyc_struct = get_schreier_structure([a], base = cand_base)
        self.image_works_test([4], cyc_struct)
        A5_struct = get_schreier_structure([a,b], base = cand_base)
        self.image_works_test([1,2,3], A5_struct)
        self.image_works_test([3,5,1], A5_struct)
        #print(A5_struct.element_from_image([3,5,1]))
        S5_struct = get_schreier_structure([a,c], base = cand_base)
        self.image_works_test([1,2,3], S5_struct)
        self.image_works_test([3,4,5,1], S5_struct)
            
    

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDirectSchreierStructure))
    suite.addTest(unittest.makeSuite(TestGraphSchreierStructure))
    suite.addTest(unittest.makeSuite(TestSchreierStructure))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())