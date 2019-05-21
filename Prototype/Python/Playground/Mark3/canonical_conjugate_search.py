from collections import defaultdict
from partition import PartitionStack, Partition
from permutation import Permutation
from position_tracker import NaivePositionTracker
from schreier_sims import BaseChanger
from refinement_manager import get_refinement_manager
import ordering

#discriminator codes:
#ios: individulaise orbit sizes
#sci: split cell index
#scs: split cell size
#prs: post refinement size
#ros: refinement orbit sizes
#ups: unordered partition stabaliser lengths.
#oir: orbit image refiner with assiociated 'a' index

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
        #Mapping to the partition 1|2|3|4|5.. 
        self.default_partition = Partition([[i] for i in range(1, self.degree + 1)])
        self._updates_manager = None
        self._refinements_manager = None
        self._cur_position = None
        
        self._refinement_manager_factory = get_refinement_manager
        #This is what keeps track of the vertex discriminators.
        self._disc_manager = None
        
        self._canonical_map = None
        self._canonical_conjugate = None
        self._canonical_discrim = None
        self._canonical_partition = None
        #If you have a particualar type of path to map to. Note this would
        #probably perform better if I also had a way of giving the actual
        #refinement instances used to make the path.
        if best_path_type is not None:
            self._canonical_discrim = best_path_type
        self.stack = None
        self.search_phase = None
        #Tree position tracker to store traversal information.
        

    def initialise_partition_stack(self):
        size = self.degree
        self.stack = PartitionStack([0]*size,[-1]*size)
    
    def initialise_search_tree(self):
        self._cur_position = NaivePositionTracker()   

    def initialise_canonical_map(self):
        #self._canonical_map = self.group.identity
        self._canonical_map = None

    def initialise_canonical_conjugate(self):
        #self._canonical_conjugate = self.group    
        self._canonical_conjugate = None
    
    def initialise_updates_manager(self):
        self._updates_manager = UpdatesManager(self.stack)
            
    def initialise_discriminator_manager(self):
        self._disc_manager = DiscriminatorManager()
    
    def initialise_refinement_manager(self):
        if self._refinements_manager is None:
            self._refinements_manager = self._refinement_manager_factory(self.group_base_changer, self._updates_manager, self._disc_manager)    
    
    def set_refinement_manager_factory(self, _custom_refinement_manager):
        self._refinement_manager_factory = _custom_refinement_manager
    
    def conjugate_representative(self):
        if self._canonical_conjugate is None:
            self._search()
        return self._canonical_conjugate

    def coset_representative(self):
        if self._canonical_map is None:
            self._search()
        return self._canonical_map

    def process_leaf(self):
        #performance wise there should be a better way to do this part.
        cand = self.get_permutation(self.stack)
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
            if self._disc_manager.compare(self._canonical_discrim, default_comparison = True) == -1:#canon > current
                if _trace: print("~not maximal branch \n\t cur:{} \n\t can:{}".format(self._disc_manager.report(), self._canonical_discrim))               
                return False
        return True
    
    def individualise(self):
        index, cell = self._select_cell(self.stack[-1])
        # this could be better 
        # give it the whole thing (part) to decide what to do with it
        # performance issue. SOLVED?
        
        #Check items in cell and choose one from each orbit in the normaliser.
        #This is only efficient if we already have the normaliser is it better 
        #to check when we pop off? but cache the normaliser? Or check for updates 
        #and then retry?
        self._disc_manager.update(("sci", index), len(self.stack))
        self._disc_manager.update(("scs", len(cell)), len(self.stack))
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
        self.initialise_updates_manager()
        self.initialise_refinement_manager()
        
        #1Refine
        #1.5 if discrete Go#5
        
        #2Indivisualise
        #3Refine
        #4 If not discrete Go#2
                        
        
        #5Process leaf
        #6If can backtrack: backtrack Go#2
        
        #7return best
        self.search_phase = True
        while self.search_phase:
            if _trace:print("~~~~~~~~~~")
            if _trace:print("{} : {}".format(len(self.stack), self.stack[-1]))
            
            if not self.stack.discrete():
                if _debug:print("-refine attempt")    
                self.refine()
                if _trace:print("~post refine: {}".format(self.stack[-1]))            
            
                
            if not self.validify():
                #Check for early backtracking i.e. compare traces.
                self.backtrack()
            #Check for discrete.
            elif self.stack.discrete():
                self.process_leaf()
                self.backtrack()
                
            else:
                #Individualise
                self.individualise()

        return self._canonical_map
    
    def backtrack(self, new_height = None):
        if new_height is None:
            new_height = len(self.stack) - 1
        if _trace:before = len(self.stack) - 1         
        _, pop_to = self._cur_position.increment(new_height)
        if pop_to > -1:
            while len(self.stack) > pop_to:
                self.stack.pop()
            self._disc_manager.pop(len(self.stack))
            if _trace:print("~backtrack {} (heights: {} {})".format(self.stack[-1], before, len(self.stack)))
            self._updates_manager.multi_remove()
            self._extend_right()
        else:
            self.search_phase = False

    def _extend_right(self):
        split_index = self._cur_position.split_index()
        split_val = self._cur_position.split_value()
        self._updates_manager.single_add(split_index, split_val)
        if _trace:print("~extend {}".format(split_val)) 
    
    def _select_cell(self, part):
        return self._select_cell_smallest(part)
    
    def _select_cell_left(self, part):
        for index, cell in enumerate(part):
            if len(cell) > 1:
                return index, cell
    
    def _select_cell_smallest(self, part):
        size = self.degree + 1
        small = None
        ret = None
        for index, cell in enumerate(part):
            cand = len(cell)
            if cand < size and cand > 1:
                size = cand
                small = cell
                ret = index
        return ret, small
    
    def _select_cell_right(self, part):
        for index in range(len(part) -1, -1, -1):
            cell = part[index]
            if len(cell) > 1:
                return index, cell                
    
    def _update_best(self, cand):
        cand_group = None
        update = False
        more_work = False
        
        if self._canonical_discrim is not None:
            more_work = False
            result = self._disc_manager.compare(self._canonical_discrim, default_comparison = True)
            #canon is lt discrim
            if result == 1:
                if _trace:print("~update via branches \n\t before:{}\n\t after:{}".format(self._canonical_discrim, self._disc_manager.report()))
                update = True
            elif result == 0:#undecided
                more_work = True
            
            #result should never be -1 else we should have early termination
            if _asserts: assert(result != -1)
                
        if self._canonical_conjugate is not None:
            if more_work:
                #this is not nec. the best way to compare groups.
                #look to the PermGroup methods to improve conjugating.
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
        new_base = self._updates_manager.fix()
        self.normaliser_base_changer.change_base(new_base)        
        ret = []
        #ret_dict = dict()
        visited = set()
        if _order is not None: cell = sorted(cell, key = _order)
        if _debug: print("-ind cell {}".format(cell))
        orbit_sizes = []
        for ele in cell:
            if ele not in visited:
                orb = self._norm_orbit(ele)
                orb_size = len(orb)
                orbit_sizes.append(orb_size)
                if _debug: print("-ind orbit {}".format(orb))
                visited.update(orb)
                ret.append(ele)
        orbit_sizes.sort()
        self._disc_manager.update(("ios", orbit_sizes),len(self.stack))
        return ret
    
    def _norm_orbit(self, ele):
        ret = self.normaliser_base_changer.orbit(ele)
        return ret

    def _refine(self):
        self._refinements_manager.refine(self.stack)

class DiscriminatorManager():
    def __init__(self):
        self._discrim = []
        self._unchecked = 0
        self._disc_cache_flag = False
        self._disc_cache = []
    
    def report(self):
        return self._discrim
    
    def report_copy(self):
        return [[val for val in cell] for cell in self._discrim]
    
    def begin_caching(self):
        self._disc_cache = []
        self._disc_cache_flag = True
        
    def end_caching(self):
        self._disc_cache_flag = False
        
    def flush_cache(self, cur_height):
        if _debug: print("-flushing disc cache")
        self.end_caching()
        for val in self._disc_cache:
            self.update(val, cur_height)
    
    def update(self, value, cur_height = 0):
        if self._disc_cache_flag:
            self._disc_cache.append(value)
            return
            
        while len(self._discrim) < cur_height:
            self._discrim.append([])
        if _asserts: assert(len(self._discrim) == cur_height)
        self._discrim[cur_height - 1].append(value)

    def pop(self, new_height):
        while len(self._discrim) > new_height:
            self._discrim.pop()
            
        if _asserts: assert(len(self._discrim[-1]) > 0)        
        self._unchecked = min(self._unchecked, new_height - 1)    
    
    def compare(self, cand, start_level = None, default_comparison = False):
        #default comparison means we can cache previous comparisons.
        #return 0
        cur = self._discrim
        #can only compare till common size.
        limit = min(len(cand), len(cur))
        if start_level is None:
            #start_level = 0
            #try automatically infer the point checked to.
            if default_comparison:
                start_level = self._unchecked
            else:
                start_level = 0
            #self._unchecked = limit
        
        for h in range(start_level, limit): 
                                  
            cand_cells = cand[h]
            cur_cells = cur[h]
            cell_limit = min(len(cand_cells), len(cur_cells))
           
            for index in range(cell_limit):
                cand_cell = cand_cells[index]
                cur_cell = cur_cells[index]
                if cand_cell < cur_cell:
                    return 1
                elif cand_cell > cur_cell:
                    return -1
            
            #one of the cells is empty this never happens to a cell that will be added to.
            #if cell_limit == 0:
                ##cur is empty but cand is not
                #if len(cand_cells) != 0 and len(cur_cells) == 0:
                    #return 1
                 ##cand (canonical) is empty but cur is not
                #elif len(cand_cells) == 0 and len(cur_cells) != 0:
                    #return -1

            if h < limit - 1:
                #this seems dangerous if are not checking against the same 
                #disc as before.
                if default_comparison:
                    self._unchecked = h               
                if len(cand_cells) < len(cur_cells):
                    return 1
                elif len(cand_cells) > len(cur_cells):
                    return -1
            
        return 0
    

class UpdatesManager():
    def __init__(self, stack):
        self.degree = stack.degree
        self.num_ops = 0
        self.extensions = [cell for cell in stack[-1]]
        self.crit_ops = [-1] * len(stack)
        self.stack = stack
    
    def __len__(self):
        return len(self.crit_ops)
    
    def single_add(self,split_index, split_val):
        self.stack.extend(split_index, [split_val])
        self.num_ops += 1        
        self.extensions.append([split_val])        
        self.crit_ops.append(self.num_ops)
        
        if _asserts: assert(len(self.crit_ops) == len(self.stack))
        if _asserts: assert(len(self.extensions) == len(self.crit_ops)) 
    
    def multi_add(self,func):
        stack = self.stack        
        ret = stack.multi_extend(func)
        if ret:
            self.num_ops += 1        
            changes = stack.report_changes(len(self.extensions))
            self.extensions.extend(changes)        
            self.crit_ops.extend([self.num_ops] *len(changes))

        if _asserts: assert(len(self.extensions) == len(self.stack))   
        if _asserts: assert(len(self.extensions) == len(self.crit_ops))        
        return ret
    
    def multi_remove(self):
        stack = self.stack
        self.num_ops += 1
        while len(self.crit_ops) > len(stack):
            self.extensions.pop()
            self.crit_ops.pop()
        if _asserts: assert(len(self.crit_ops) == len(self.stack))  
        if _asserts: assert(len(self.extensions) == len(self.crit_ops))       
    
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
                
        #if len(self.crit_ops) == 0 or self.crit_ops[0] < lo:
            #lo = None
            
        return lo
    
    def last_pop_height(self, op_id):
        #now returning the height of the stack that is the top most unchanged
        return self._bin_search(op_id) + 1
    
    def report_changes(self, prev_op = None, last_pop = None):
        #last pop given as a stack height.
        if prev_op is None:
            prev_op = 0
        if last_pop is None:
            last_pop = self._bin_search(prev_op) + 1
        #should be a generator.
        #all the new ones
        return self.extensions[last_pop:], self.num_ops
    
    def fix_info(self, level = 0):
        return self.stack.fix_info(level)
    
    def fix(self):
        return self.stack.fix()
    
    def special_values(self):
        pass
    
    def special_levels(self):
        pass