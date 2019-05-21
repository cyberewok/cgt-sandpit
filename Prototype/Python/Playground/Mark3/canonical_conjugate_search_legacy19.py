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
#ups: unordered partition stabaliser lengths.

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
    
    def initialise_refinements_manager(self):
        self._refinements_manager = RefinementsManager(self.group_base_changer, self._updates_manager, self._disc_manager)
    
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
        self.initialise_refinements_manager()
        
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


class RefinementsManager():
    def __init__(self, base_changer, updates_manager, discriminator_manager):
        self.updates_manager = updates_manager
        self.base_changer = base_changer
        self.disc_manager = discriminator_manager
        self.mem_refiner = MemberRefinement(base_changer, updates_manager, discriminator_manager)
        self.orb_refiner = OrbitStabaliser(base_changer, updates_manager, discriminator_manager)

    def _group_stable(self):
        return self.base_changer.discrete()    
            
    def refine(self, stack):
        #in future think about orbit graph refinements.
        self.base_changer.change_base(self.updates_manager.fix())
        #need way better criterior. Actually a very narrow refinement.
        #use for regular or big last orbit only. Think about structuring the
        #search so the last orbit is big as possible.
        before = 0
        after = 1
        self.disc_manager.begin_caching()
        count = 0
        while not stack.discrete() and before < after:
            count += 1
            before = len(stack)
            if self._group_stable():
                self.mem_refiner.refine(stack)
            self.orb_refiner.refine(stack)
            after = len(stack)
        self.disc_manager.end_caching()
        self.disc_manager.update(("aft", len(stack)), len(stack))
        if count > 1 or stack.discrete():
            self.disc_manager.flush_cache(len(stack))
            if _debug: print("-new disc: {}".format(self.disc_manager.report()))
            #if _debug: print("-refined!")
            return True
        return False

class MemberRefinement():
    def __init__(self, base_changer, updates_manager, discriminator_manager):
        self.disc_manager = discriminator_manager
        self.updates_manager = updates_manager
        self.base_changer = base_changer
        self.update_token = 0
        self.cur_height = 1
    
    def refine(self, stack):
        return self._member_refine(stack)
        
    def _member_refine_applicable(self, fix, end, size):
        if len(fix) <= size:
            return False
        return fix[-1] in end
    
    def _member_refine_from_element(self, g, fix, stack):
        val_lookup = dict()
        fix_lookup = {ele:index for index, ele in enumerate(fix)}
        cyc_note = g.cycle_notation()
        
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
        self.disc_manager.update(("mrs", sorted([len(cyc) for cyc in cyc_note])),len(self.updates_manager))          
        ret = self.updates_manager.multi_add(func)
        if ret:
            self.disc_manager.update(("mrs", sorted([len(cyc) for cyc in cyc_note])),len(self.updates_manager))                      
        return ret
        #self.stack.multi_extend(func)        

    def _member_refine(self, stack):
        if _debug:print("-refine (member) attempt")
        if _stats: ret = tuple([0])
        #get fix.
        fix = self.updates_manager.fix()
        self.base_changer.change_base(fix)
        orbits = self.base_changer.stabaliser_orbits()
        end = orbits[-1]
        size = len(orbits)
        ret = False
        if self._member_refine_applicable(fix, end, size):
            image = fix[:size - 1] + [fix[-1]]
            if _debug:print("-image: {}".format(image))            
            g = self.base_changer.element_from_image(image)
            if _trace:print("~perm refine: {}".format(g))
            #individualise on G if a memeber is in fix in the order of the g cycle.
            ret = self._member_refine_from_element(g, fix, stack)
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
        return ret

class OrbitStabaliserNaive():
    def _orbit_refine(self):
        if _stats: ret = False        
        changed = True
        while changed:
            before = len(self.stack)
            orbits = self._group_orbits()
            self._disc_manager.update(("ros", sorted([len(orb) for orb in orbits])), self._cur_height) 
            self._orbit_size_refinement(orbits)
            after = len(self.stack)
            changed = before < after
            if changed:
                if _stats:ret = True
                if _trace:print("~refined (orbits: {})".format(orbits))
        if _stats:return ret
    
    def _group_orbits(self):
        new_base = self._updates_manager.fix()
        if _trace:print("~group base change {}".format(new_base))        
        self.group_base_changer.change_base(new_base)
        ret = self.group_base_changer.orbits()
        return ret    
    
    def _orbit_size_refinement(self, orbits):
        ele_to_size = dict()
        for orbit in orbits:
            for ele in orbit:
                ele_to_size[ele] = len(orbit)
        func = lambda x:ele_to_size[x]
        self._apply_refinement_function(func)
        self.stack.multi_extend(func)

class OrbitStabaliser():
    def __init__(self, base_changer, updates_manager, discriminator_manager):
        self.disc_manager = discriminator_manager
        self.updates_manager = updates_manager
        self.base_changer = base_changer
        self.part_stabs = []
        self.start_heights = []
        self.orb_sizes = []
        self.update_token = 0
        self.cur_height = 1
        self._initialise_top_orbit()
    
    def _initialise_top_orbit(self):   
        orbs = self.base_changer.orbits(level = 0)
        if _debug: print("-considering orbs {}".format(orbs))
        if self._valid_orbs(orbs, self.updates_manager.degree):
            stab = UnorderedPartitionStabaliser(Partition(orbs))
            self.part_stabs.append(stab)
            self.start_heights.append(-1)
            self.orb_sizes.append(len(orbs))
    
    def __len__(self):
        return self.cur_height

    def refine(self, stack):
        self._update(stack)
        if _debug: print("-orbit stab info {} {}".format(self.start_heights, self.orb_sizes))
        for stab in self.part_stabs:
            if stab is not None:
                func = stab.refinement_function()
                if self.updates_manager.multi_add(func):
                    self.disc_manager.update(stab.discriminator_info(), len(self.updates_manager))                
                    return True
        return False
    
    def _update(self, stack):
        #this is the last height of stack that is retained.
        prestack_height = self.updates_manager.last_pop_height(self.update_token)
        
        #pop redundant stabs
        while len(self.start_heights) > 0 and self.start_heights[-1] > prestack_height:
            if _debug: print("-popping orbit stabs to {}".format(prestack_height))
            self.start_heights.pop()
            self.part_stabs.pop()
            self.orb_sizes.pop()
        
        #revert surviving stabs
        for stab in self.part_stabs:
            if stab is not None:
                stab.pop_to(prestack_height)
        
        #create stabs
        new_base_eles, heights = self.updates_manager.fix_info(prestack_height)
        cur_fix = self.updates_manager.fix()
        if _debug: print("-fix: {}".format(cur_fix))
        self.start_heights.extend(heights)
        self.base_changer.change_base(cur_fix)
        
        added = []
        for fix_index in range(len(cur_fix) - len(new_base_eles), len(cur_fix)): 
            fix_val, fix_height = cur_fix[fix_index], self.start_heights[fix_index]        
            orbs = self.base_changer.orbits(fix_index + 1)
            if _debug: print("-considering orbits: {}".format(orbs))
            to_add = None
            
            if self._valid_orbs(orbs, stack.degree):
                if _debug: print("-orbit is valid: {}".format(self.orb_sizes))                
                to_add = UnorderedPartitionStabaliser(Partition(orbs))
                added.append(to_add)
            
            self.orb_sizes.append(len(orbs))
            self.part_stabs.append(to_add)
        
        #Let stabs catchup
        changes, self.update_token = self.updates_manager.report_changes(None, 0)
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
    
    def _valid_orbs(self, orbs, degree):

        
        #one orbit
        if len(orbs) == 1:
            return False
        
        #Same orbs as a level above
        if len(self.orb_sizes) > 0 and self.orb_sizes[-1] == len(orbs):
            return False        
        
        #all singles
        if len(orbs) == degree:
            return False
        
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
        while len(self.derived_sizes) > level:
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