from collections import defaultdict
from partition import PartitionStack, Partition
from permutation import Permutation
from position_tracker import NaivePositionTracker
from schreier_sims import BaseChanger
import ordering

#discriminator codes:
#ios: individulaise orbit sizes
#sci: split cell index
#scs: split cell size
#prs: post refinement size
#ros: refinement orbit sizes


_trace = False
_debug = False
_stats = False
_asserts = True
_order = None

#should take out non moved points and relable. Would save so much work.

def canonical_conjugate(group, normaliser = None, parent = None):
    if normaliser is None:
        normaliser = group
    nccs = NaiveCanonicalConjugateSearch(group, normaliser)
    ret = nccs.conjugate_representative()
    return ret

def canonical_map(group, normaliser = None, parent = None):    
    if normaliser is None:
        normaliser = group
    nccs = NaiveCanonicalConjugateSearch(group, normaliser)
    ret = nccs.coset_representative()
    return ret

def canonical_map_from_automorphisms(normaliser):
    nccs = NaiveCanonicalConjugateSearch(_, normaliser, from_automorphism_group = True)
    ret = nccs.coset_representative()
    return ret

def _canonical_all(group, normaliser, best = None):
    nccs = NaiveCanonicalConjugateSearch(group, normaliser, best)
    ret_map = nccs.coset_representative()
    ret_group = nccs.conjugate_representative()
    ret_path = nccs._canonical_discrim
    return ret_group, ret_map, ret_path

def _reduced_tree(group, normaliser, best = None):
    nccs = NaiveCanonicalConjugateSearch(group, normaliser)
    ret = []
    old_func = nccs.process_leaf
    def new_func(*args):
        if best is not None:
            if nccs._stack_compareOLD(args[-1], best) == 0:        
                ret.append(args[-1][-1])
        else:        
            ret.append(args[-1][-1])
        return old_func(*args)
    nccs.process_leaf = new_func
    ret_map = nccs.coset_representative()
    return ret, nccs.default_partition, group
    

class NaiveCanonicalConjugateSearch():
    def __init__(self, G, N, best_path_type = None, from_automorphism_group = False):
        self.normaliser = N
        self.normaliser_base_changer = BaseChanger(N)
        self.group = N
        self.group_base_changer = self.normaliser_base_changer
        
        if not from_automorphism_group:
            self.group = G
            self.group_base_changer = BaseChanger(G)
                        
        self.degree = G.degree
        self.default_partition = Partition([[i] for i in range(1, self.degree + 1)])
        self._updates_controller = None
        self._orbit_refiner = None
        self._canonical_map = None
        self._canonical_conjugate = None
        self._canonical_discrim = None
        self._canonical_partition = None
        if best_path_type is not None:
            self._canonical_discrim = best_path_type
        self.stack = None
        self._cur_height = None        
        #Tree position tracker to store traversal information.
        self._cur_position = None
        
        self._disc_manager = None
        

    def initialise_partition_stack(self):
        size = self.degree
        self.stack = PartitionStack([0]*size,[-1]*size)
        self._discrim = [[]]
        self._unchecked = 0
        self._disc_cache_flag = False
        self._disc_cache = []
    
    def initialise_search_tree(self):
        self._cur_height = 0
        self._cur_position = NaivePositionTracker()   

    def initialise_canonical_map(self):
        #self._canonical_map = self.group.identity
        self._canonical_map = None

    def initialise_canonical_conjugate(self):
        #self._canonical_conjugate = self.group    
        self._canonical_conjugate = None
    
    def initialise_updates_controller(self):
        self._updates_controller = UpdatesController()
        
    def initialise_refiners(self):
        self._orbit_refiner = OrbitStabaliser(self.group_base_changer, self._updates_controller, self._disc_manager)
    
    def initialise_discriminator_manager(self):
        self._disc_manager = DiscriminatorManager()
    
    def conjugate_representative(self):
        if self._canonical_conjugate is None:
            self._search()
        return self._canonical_conjugate

    def coset_representative(self):
        if self._canonical_map is None:
            self._search()
        return self._canonical_map

    def process_leaf(self, stack):
        #performance wise there should be a better way to do this part.
        cand = self.get_permutation(stack)
        self._update_best(cand)
        if _trace:print("~cand group gens: {}".format((self.group ** cand).canonical_generators()))
    
    def get_permutation(self, stack):
        pre = stack[-1]
        #image = stack.canonical_form()[-1]
        image = self.default_partition
        cand = Permutation.read_partitions(pre, image)
        if _trace:print("~processing leaf {} ({})".format(cand, image))
        return cand
    
    def validify(self):
        #return True
        #checking if valid
        if self._canonical_discrim is not None:
            if self._disc_manager.compare_discriminator(self._canonical_discrim) == 1:#canon > current
                if _trace: print("~not maximal branch \n\t cur:{} \n\t can:{}".format(self._discrim, self._canonical_discrim))               
                return False                
            #if self.compare_discriminator(self._canonical_discrim, self._discrim) == 1:#canon > current
            #    if _trace: print("~not maximal branch \n\t cur:{} \n\t can:{}".format(self._discrim, self._canonical_discrim))               
            #    return False
        return True
    
    def individualise(self, stack):
        index, cell = self._select_cell(stack[-1])
        # this could be better 
        # give it the whole thing (part) to decide what to do with it
        # performance issue.
        
        #Check items in cell and choose one from each orbit in the normaliser.
        self._disc_manager.update_discriminator(("sci", index), self._cur_height)
        self._disc_manager.update_discriminator(("scs", len(cell)), self._cur_height)
        #self.update_discriminator(("sci", index))
        #self.update_discriminator(("scs", len(cell)))
        sub_cell = self._norm_orbit_reps(cell)
        self._cur_position.add_level(index, sub_cell, len(self.stack))
        
        if _trace:print("~individualise {} (savings: {})".format(sub_cell, len(cell) - len(sub_cell)))         
        self._extend_right()
       
        
    def refine(self):
        #try refinement functions and keep track of height and cur_position
        self._refine()
    
    def _search(self):
        self.initialise_partition_stack()
        self.initialise_search_tree()
        self.initialise_canonical_map()
        self.initialise_canonical_conjugate()
        self.initialise_discriminator_manager()
        self.initialise_updates_controller()
        self.initialise_refiners()
        
        #1Refine
        #1.5 if discrete Go#5
        
        #2Indivisualise
        #3Refine
        #4 If not discrete Go#2
                        
        
        #5Process leaf
        #6If can backtrack: backtrack Go#2
        
        #7return best
        
        while self._cur_height > -1:
            if _trace:print("~~~~~~~~~~")
            if _trace:print("{} : {}".format(self._cur_height, self.stack[-1]))
            
            if not self.stack.discrete():
                #if _debug:print("~refineAttept")    
                self.refine()

            if _trace:print("~post refine: {}".format(self.stack[-1]))            
            
            #Check for discrete.
            if self.stack.discrete():
                self.process_leaf(self.stack)
                self.backtrack()
                #self.refine()
            elif not self.validify():
                #Check for early backtracking
                self.backtrack()
                #self.refine()
            else:
                #Individualise
                self.individualise(self.stack)

                #Check for refinment till probably irriducible
                #self.refine()

        return self._canonical_map
    
    def backtrack(self, new_height = None):
        if new_height is None:
            new_height = self._cur_height
        if _trace:before = self._cur_height         
        self._cur_height, pop_to = self._cur_position.increment(new_height)    
        if pop_to > -1:
            while len(self.stack) > pop_to:
                self.stack.pop()
            self._disc_manager.pop_discriminator(self._cur_height + 1)
            #self.pop_discriminator(self._cur_height + 1)
            if _trace:print("~backtrack {} (heights: {} {})".format(self.stack[-1], before, self._cur_height))
            self._updates_controller.multi_remove(self.stack)
            self._extend_right()

    def _extend_right(self):
        index = self._cur_height
        split_index = self._cur_position.split_index()
        split_val = self._cur_position.split_value()
        self.stack.extend(split_index, [split_val])
        self._updates_controller.single_add(self.stack, split_index, split_val)      
        self._cur_height += 1
        if _trace:print("~extend {}".format(split_val)) 
    
    def _select_cell(self, part):
        for index, cell in enumerate(part):
            if len(cell) > 1:
                return index, cell
    
    def _update_best(self, cand):
        cand_group = None
        update = False
        more_work = False
        
        if self._canonical_discrim is not None:
            more_work = False
            result = self._disc_manager.compare_discriminator(self._canonical_discrim)
            #result = self.compare_discriminator(self._canonical_discrim, self._discrim)
            #canon is lt discrim
            if result == -1:
                if _trace:print("~update via branches \n\t before:{}\n\t after:{}".format(self._canonical_discrim, self._disc_manager.report()))
                #if _trace:print("~update via branches \n\t before:{}\n\t after:{}".format(self._canonical_discrim, self._discrim))
                update = True
            elif result == 0:#undecided
                more_work = True
                
        if self._canonical_conjugate is not None:
            if more_work:
                #this is bad.                
                cand_group = self.group ** cand                
                if cand_group < self._canonical_conjugate:
                    update = True
        else:
            update = True
        
        if update:
            if cand_group is None:
                cand_group = self.group ** cand
            self._canonical_discrim = self._disc_manager.report_copy()
            #self._canonical_discrim = [[val for val in cell] for cell in self._discrim]
            self._canonical_conjugate = cand_group
            self._canonical_map = cand
            self._canonical_partition = PartitionStack.deep_copy(self.stack)
            if _trace:print("~update")
    
    def _norm_orbit_reps(self, cell):
        #change base so we can determine the orbits.
        #for each ele in cell is that ele a min of an orbit?
        #for each ele in cell is that ele a min rep from the cell of an orbit?
        new_base = self.stack.fix()
        self.normaliser_base_changer.change_base(new_base)        
        ret = []
        #ret_dict = dict()
        visited = set()
        if _order is not None: cell = sorted(cell, key = _order)
        if _debug: print("~ind cell {}".format(cell))
        orbit_sizes = []
        for ele in cell:
            if ele not in visited:
                orb = self._norm_orbit(ele)
                orb_size = len(orb)
                orbit_sizes.append(orb_size)
                if _debug: print("~ind orbit {}".format(orb))
                visited.update(orb)
                ret.append(ele)
                #if orb_size in ret_dict:
                    #ret_dict[orb_size].append(ele)
                #else:
                    #ret_dict[orb_size] = [ele]
        
        #best_len = float("inf")
        #best_key = None
        #for key in ret_dict:
            #size_cand = len(ret_dict[key])
            
            #if (size_cand,key) < (best_len,best_key):
                #best_len = size_cand
                #best_key = key
        
        #ret = ret_dict[best_key]
        orbit_sizes.sort()
        #this whole dict speed up thing with only choosing best size slows down everything.
        #should tweek it. 
        self._disc_manager.update_discriminator(("ios", orbit_sizes),self._cur_height)
        #self.update_discriminator(("ios", orbit_sizes))
        #self.update_discriminator(("ibk", (-1 * best_len, key)))
        return ret
    
    def _norm_orbit(self, ele):
        ret = self.normaliser_base_changer.orbit(ele)
        return ret        
    
    def _group_orbits(self):
        new_base = self.stack.fix()
        if _trace:print("~group base change {}".format(new_base))        
        self.group_base_changer.change_base(new_base)
        ret = self.group_base_changer.orbits()
        return ret

    def _group_stable(self):
        return self.group_base_changer.discrete()
        

    def _refine(self):
        #hardcode the size refinement.
        #in future think about orbit graph refinements.
        self.group_base_changer.change_base(self.stack.fix())
        #need way better criterior. Actually a very narrow refinement.
        #use for regular or big last orbit only. Think about structuring the
        #search so the last orbit is big as possible.
        before = 0
        after = 1
        self._disc_manager.begin_discriminator_caching()
        #self._begin_discriminator_caching()
        count = 0
        while not self.stack.discrete() and before < after:
            count += 1
            before = len(self.stack)
            if self._group_stable():
                self._member_refine()
            #use properly.
            else:
                self._orbit_refine()
            #for func in self._orbit_refiner.refinement_functions(self.stack):
                #self._apply_refinement_function(func)
            after = len(self.stack)
        self._disc_manager.end_discriminator_caching()            
        #self._end_discriminator_caching()            
        self._disc_manager.update_discriminator(("aft", len(self.stack)), self._cur_height) 
        #self.update_discriminator(("aft", len(self.stack))) 
        if count > 1:
            self._disc_manager.flush_discriminator_cache(self._cur_height)      
            #self._flush_discriminator_cache()      
    
    def _member_refine_applicable(self, fix, end, size):
        if len(fix) <= size:
            return False
        return fix[-1] in end
    
    def _member_refine_from_element(self, g, fix):
        
        val_lookup = dict()
        fix_lookup = {ele:index for index, ele in enumerate(fix)}
        cyc_note = g.cycle_notation()
        
        self._disc_manager.update_discriminator(("mrs", sorted([len(cyc) for cyc in cyc_note])),self._cur_height)          
        for cycle in cyc_note:
            best_val = None
            best_index = None
            for index, ele in enumerate(cycle):#get element with best fix position from cycle
                if ele in fix_lookup:
                    cand_val = fix_lookup[ele]
                    if best_val is None or cand_val < best_val:
                        best_val = cand_val
                        best_index = index
            if best_val is not None:
                for index, ele in enumerate(cycle[best_index:] + cycle[:best_index]):
                    val_lookup[ele] = (0,index)#order by distance from best
            else:
                for ele in cycle:
                    val_lookup[ele] = (1,len(cycle))#no element from fix so use cycle len
        func = lambda x:val_lookup[x] if x in val_lookup else (3,0)
        
        #if _debug:print("~multi extend func: {}".format([(ele, func(ele)) for ele in range(1, self.degree + 1)]))
        self._apply_refinement_function(func)
        #self.stack.multi_extend(func)        
        
    
    def _member_refine(self):
        if _debug:print("~refine (member) attempt")
        if _stats: ret = tuple([0])
        #get fix.
        fix = self.stack.fix()
        self.group_base_changer.change_base(fix)
        orbits = self.group_base_changer.stabaliser_orbits()
        end = orbits[-1]
        size = len(orbits)
        if self._member_refine_applicable(fix, end, size):
            image = fix[:size - 1] + [fix[-1]]
            if _debug:print("~image: {}".format(image))            
            g = self.group_base_changer.element_from_image(image)
            if _trace:print("~perm refine: {}".format(g))
            #individualise on G if a memeber is in fix in the order of the g cycle.
            self._member_refine_from_element(g, fix)
            if _stats:
                ret = []
                for cyc in g.cycle_notation():
                    ret.append(len(cyc))
                ret = tuple(sorted(ret))
        #check it against the last orbit stabaliser list.
        #use the permutation found.
        
        #changed = True
        #while changed:
            #before = len(self.stack)
            #orbits = self._group_orbits()
            #self._orbit_size_refinement(orbits)
            #after = len(self.stack)
            #changed = before < after
            #if changed:
                #if _stats:ret = True
                #if _trace:print("~refined ({})".format(orbits))
        if _stats:return ret
    
    def _orbit_refine(self):
        if _stats: ret = False        
        changed = True
        while changed:
            before = len(self.stack)
            orbits = self._group_orbits()
            self._disc_manager.update_discriminator(("ros", sorted([len(orb) for orb in orbits])), self._cur_height) 
            self._orbit_size_refinement(orbits)
            after = len(self.stack)
            changed = before < after
            if changed:
                if _stats:ret = True
                if _trace:print("~refined (orbits: {})".format(orbits))
        if _stats:return ret
    
    def _orbit_size_refinement(self, orbits):
        ele_to_size = dict()
        for orbit in orbits:
            for ele in orbit:
                ele_to_size[ele] = len(orbit)
        func = lambda x:ele_to_size[x]
        self._apply_refinement_function(func)
        self.stack.multi_extend(func)
    
    #def _begin_discriminator_caching(self):
        #self._disc_cache = []
        #self._disc_cache_flag = True
    
    #def _end_discriminator_caching(self):
        #self._disc_cache_flag = False
        
    #def _flush_discriminator_cache(self):
        #self._end_discriminator_caching()
        #for val in self._disc_cache:
            #self.update_discriminator(val)
    
    #def update_discriminator(self, value):
        #if self._disc_cache_flag:
            #self._disc_cache.append(value)
            #return
            
        #while len(self._discrim) <= self._cur_height:
            #self._discrim.append([])
        #if _asserts: assert(len(self._discrim) == self._cur_height + 1)
        #self._discrim[self._cur_height].append(value)

    #def pop_discriminator(self, new_height):
        #while len(self._discrim) > new_height:
            #self._discrim.pop()
        #self._unchecked = min(self._unchecked, new_height - 1)
    
    def compare_discriminator(self, cand, other, start_level = None):
        pass
        ##return 0
        #limit = min(len(cand), len(other))        
        #if start_level is None:
            ##start_level = 0
            ##try automatically infer the point checked to.
            #start_level = self._unchecked
            ##self._unchecked = limit
        
        #for h in range(start_level, limit):
            #self._unchecked = h 
            #cand_cells = cand[h]
            #other_cells = other[h]
            #cell_limit = min(len(cand_cells), len(other_cells))
           
            #for index in range(cell_limit):
                #cand_cell = cand_cells[index]
                #other_cell = other_cells[index]
                #if cand_cell < other_cell:
                    #return -1
                #elif cand_cell > other_cell:
                    #return 1

            #if h < limit - 1:
                #if len(cand_cells) < len(other_cells):
                    #return -1
                #elif len(cand_cells) > len(other_cells):
                    #return 1
            
        #return 0

    def _apply_refinement_function(self, func):
        self.stack.multi_extend(func)
        self._updates_controller.multi_add(self.stack)
        
    def _stack_compare_OLD(self, cand, other, start_level = None):
        #return 0
        if start_level is None:
            start_level = 0
        limit = min(len(cand), len(other))
        for h in range(start_level, limit):
            cand_cells = cand[h]
            other_cells = other[h]
            if len(cand_cells) != len(other_cells):
                raise ValueError("Incompatible partition stacks for comparison.")
            for index in range(len(cand_cells)):
                cand_cell = cand_cells[index]
                other_cell = other_cells[index]
                if len(cand_cell) < len(other_cell):
                    return 1
                elif len(cand_cell) > len(other_cell):
                    return -1
        return 0

class DiscriminatorManager():
    
    def __init__(self):
        self._discrim = [[]]
        self._unchecked = 0
        self._disc_cache_flag = False
        self._disc_cache = []
    
    def report(self):
        return self._discrim
    
    def report_copy(self):
        return [[val for val in cell] for cell in self._discrim]
    
    def begin_discriminator_caching(self):
        self._disc_cache = []
        self._disc_cache_flag = True
        
    def end_discriminator_caching(self):
        self._disc_cache_flag = False
        
    def flush_discriminator_cache(self, cur_height):
        self.end_discriminator_caching()
        for val in self._disc_cache:
            self.update_discriminator(val, cur_height)
    
    def update_discriminator(self, value, cur_height = 0):
        if self._disc_cache_flag:
            self._disc_cache.append(value)
            return
            
        while len(self._discrim) <= cur_height:
            self._discrim.append([])
        if _asserts: assert(len(self._discrim) == cur_height + 1)
        self._discrim[cur_height].append(value)

    def pop_discriminator(self, new_height):
        while len(self._discrim) > new_height:
            self._discrim.pop()
        self._unchecked = min(self._unchecked, new_height - 1)    
    
    def compare_discriminator(self, cand, start_level = None):
        #return 0
        other = self._discrim
        limit = min(len(cand), len(other))        
        if start_level is None:
            #start_level = 0
            #try automatically infer the point checked to.
            start_level = self._unchecked
            #self._unchecked = limit
        
        for h in range(start_level, limit):
            self._unchecked = h 
            cand_cells = cand[h]
            other_cells = other[h]
            cell_limit = min(len(cand_cells), len(other_cells))
           
            for index in range(cell_limit):
                cand_cell = cand_cells[index]
                other_cell = other_cells[index]
                if cand_cell < other_cell:
                    return -1
                elif cand_cell > other_cell:
                    return 1

            if h < limit - 1:
                if len(cand_cells) < len(other_cells):
                    return -1
                elif len(cand_cells) > len(other_cells):
                    return 1
            
        return 0    
    

class UpdatesController():
    def __init__(self):
        self.num_ops = 0
        self.cur_height = 1
        self.extensions = []
        self.crit_ops = []
    
    def __len__(self):
        return self.cur_height
    
    def single_add(self,stack,split_index = None,split_val = None):
        self.num_ops += 1        
        self.extensions.append([split_val])        
        self.crit_ops.append(self.num_ops)
        self.cur_height = len(stack)
    
    def multi_add(self,stack):
        self.num_ops += 1        
        changes = stack.report_changes(self.cur_height)
        self.extensions.extend(changes)        
        self.crit_ops.extend([self.num_ops] *len(changes))
        self.cur_height = len(stack)
        
    def multi_remove(self,stack):
        self.num_ops += 1
        while self.cur_height > len(stack):
            self.extensions.pop()
            self.crit_ops.pop()
            self.cur_height -= 1
    
    def _bin_search(self, op_id):
        lo = 0
        hi = len(self.crit_ops)
        #lo<=des<hi
        while lo < hi - 1:
            mid = (hi + lo)//2
            if self.crit_ops[mid] <= op_id:
                lo = mid
            else:
                hi = mid
        return lo
    
    def last_pop_height(self, op_id):
        offset = self.cur_height - (len(self.extensions) - 1)
        #now returning the height of the stack that is the top most unchanged
        return self._bin_search(op_id) + offset
        
    
    def report_changes(self, prev_op = None, last_pop = None):
        #last pop given as a stack height.
        offset = self.cur_height - (len(self.extensions) - 1)
        if prev_op is None:
            prev_op = 1
        if last_pop is None:
            last_pop = self._bin_search(prev_op)
        else:
            #now it an index again
            last_pop -= offset
        #should be a generator.
        #all the new ones
        return self.extensions[last_pop + 1:], self.num_ops

class OrbitStabaliser():
    def __init__(self, base_changer, update_controller, discriminator_manager):
        self.disc_manager = discriminator_manager
        self.update_controller = update_controller
        self.base_changer = base_changer
        self.part_stabs = []
        self.start_heights = []
        self.cur_fix = []
        self.update_token = 0
        self.cur_height = 1
    
    def __len__(self):
        return self.cur_height

    def refinement_functions(self, stack):
        self._update(stack)
        #self._disc_manager.update_discriminator(("ros", sorted([len(orb) for orb in orbits])), self._cur_height)
        for stab in self.part_stabs:
            if stab is not None:
                self.disc_manager.update_discriminator(stab.discriminator_info())
                yield stab.refinement_function()
    
    def _update(self, stack):
        #this is the last height of stack that is retained.
        prestack_height = self.update_controller.last_pop_height(self.update_token)
        
        #pop redundant stabs
        while len(self.start_heights) > 0 and self.start_heights[-1] > prestack_height:
            self.start_heights.pop()
            self.part_stabs.pop()
            self.cur_fix.pop()
        
        #revert surviving stabs
        for stab in self.part_stabs:
            if stab is not None:
                stab.pop_to(prestack_height)
        
        #create stabs
        new_base, heights = stack.fix_info(prestack_height)
        self.cur_fix.extend(new_base)
        self.start_heights.extend(heights)
        self.base_changer.change_base(self.cur_fix)
        
        prev_orbs = None
        added = []
        for fix_index in range(len(self.cur_fix) - len(new_base), len(self.cur_fix)): 
            fix_val, fix_height = self.cur_fix[fix_index], self.start_heights[fix_index]        
            orbs = self.base_changer.orbits(fix_index + 1)
            to_add = None
            
            if self._valid_orbs(orbs, prev_orbs):
                to_add = UnorderedPartitionStabaliser(Partition(orbs))
                added.append(to_add)
            
            self.part_stabs.append(to_add)
        
        #Let stabs catchup
        changes, self.update_token = self.update_controller.report_changes(None, 1)
        for enum, end in enumerate(changes):
            height = enum + 2
            if height <= prestack_height:
                for add in added:
                    add.add_level(end)
            else:
                for stab in self.part_stabs:
                    if stab is not None:
                        stab.add_level(end)
            
        #update cur_height
        self.cur_height = len(stack)
    
    def _valid_orbs(self, orbs, prev):
        if len(orbs) == 1:
            return False
        #INEFFICIENT
        #should know the degree and check for it top
        if max(len(orb) for orb in orbs) == 1:
            return False
        #if prev is not None:
            #if len(prev) == len(orbs):
                #return False
        return True
    

class UnorderedPartitionStabaliser():
    def __init__(self, part):
        self.degree = len(part)
        self.partition = part
        self.derived = PartitionStack([0] * self.degree, [-1] * self.degree)
        self.derived_sizes = []
        self._initialise_current_partition()
        self.element_lookup = [None] * (max(max(cell) for cell in part) + 1)        
        self._initialise_lookup()
        self.can_info = ("ups",tuple(sorted([len(cell) for cell in part])))

    def _initialise_lookup(self):
        for index, cell in enumerate(self.partition):
            for element in cell:
                self.element_lookup[element] = index + 1
    
    def _initialise_current_partition(self):
        func = lambda cell_num: len(self.partition[cell_num - 1])
        self.derived.multi_extend(func)
        self.derived_sizes.append(len(self.derived))
        #self.derived_indices.append(len(self.derived) - 1)
        #self.top_index = 0

    def add_level(self, end_cell):
        #choose to do low mem hi processing. This is prob a mistake. Specially without a sparse partition stack multi extend.
        affected = defaultdict(int)
        
        for ele in end_cell:
            cell_num = self.element_lookup[ele]
            affected[cell_num] += 1
    
        func = lambda cell_num: 0 if cell_num not in affected else affected[cell_num]
        
        self.derived_sizes.append(len(self.derived))
        self.derived.multi_extend(func)
    
    #def add_level_OLD(self, split_cell, end_cell):
        #affected = dict()
        
        #for tmp_index, cell in enumerate([split_cell, end_cell]):
            
            #for ele in cell:
                #cell_num = self.element_lookup[ele]
                #if cell_num not in affected:
                    #affected[cell_num] = [0,0]
                #affected[cell_num][tmp_index] += 1
        
        #func = lambda cell_num: (0,0) if cell_num not in affected else tuple(affected[cell_num])
        
        #self.derived_sizes.append(len(derived))        
        #self.derived.multi_extend(func)
    
    def pop_to(self, level):
        while len(self.derived_sizes) + 1 > level:
            self.remove_level()
        
    
    def remove_level(self):
        #does the multi extend always give exactly one refinement? NO.
        #need instead to keep track of indices
        pop_to = self.derived_sizes.pop()
        while len(self.derived) > pop_to:
            self.derived.pop()
    
    def discriminator_info(self):
        return self.can_info
    
    def refinement_function(self):
        func = lambda ele:self.derived.cell_of(self.element_lookup[ele])
        return func
    
    def __len__(self):
        return len(self.derived_sizes)
    
    #update with the current changes lazily?
    
    #advise on refinements if asked
    
    #tell if dominated by another??
    


class UnorderedPartitionStabaliserOLD():
    def __init__(self, partition):
        self.partition = partition
        self.degree = len(partition)
        self.element_lookup = None
        self.initialise_lookup()
        self.top_index = 0
        self.derived = None
        self.derived_indices = None
        self.initialise_derived()
        self.left_derived = None
        self.left_derived_indices = None    
 
    def initialise_lookup(self):
        self.element_lookup = [None] * (len(self.partition) + 1)
        for index, cell in enumerate(self.partition):
            for element in cell:
                self.element_lookup[element] = index + 1
        
    def initialise_derived(self):
        self.derived = PartitionStack([0]*self.degree, [-1]*self.degree)
        self.derived_indices = []
        func = lambda element: len(self.partition[element - 1])
        self.derived.multi_extend(func)
        self.derived_indices.append(len(self.derived) - 1)
        self.top_index = 0
    
    def cell_extend(self, cell):    
        split_cell = cell
        counts = [0]*self.degree
        for ele in cell:
            cand_derived = self.element_lookup[ele]
            counts[cand_derived - 1] += 1 
            
        def int_func(element):
            return counts[element - 1]
        
        self.derived.multi_extend(int_func)
        self.derived_indices.append(len(self.derived) - 1)
        self.top_index += 1
        
    def pop_to_height(self, new_top_index):
        if self.top_index <= new_top_index:
            raise IndexError("{} new height larger than {}.".format(new_top_index, self.top_index))
        while self.top_index > new_top_index:
            self.derived_indices.pop()
            limit = self.derived_indices[-1]
            self.top_index -= 1
            self.derived.pop_to_height(limit + 1)
    
    def _full_extension(self, stack, i, j):
        cell_union_indices = self.derived[-1,j]
        cell_union = []
        for ele in cell_union_indices:
            cell_union += self.partition[ele - 1]        
        if stack is not None:
            stack.extend(i, cell_union)
        return stack
    
    def extension_functions(self, left, *args):
        for i in range(len(left)):
            unions = self.derived[-1]
            for j in range(len(unions)):
                cell_union = []
                for ele in unions[j]:
                    cell_union += self.partition[ele - 1]
                if left.can_extend(i, cell_union):
                    func = lambda stack : self._full_extension(stack,i,j)
                    func._info = [self.__class__,i,j]
                    return func, func
        return None