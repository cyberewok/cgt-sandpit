from partition import Partition, PartitionStack
from collections import defaultdict

#oir: orbit image refiner with assiociated 'a' index

_trace = False
_debug = False
_stats = False
_asserts = True
_order = None

def get_refinement_manager(abstractions_manager, updates_manager, discriminator_manager):
    return get_default_manager(abstractions_manager, updates_manager, discriminator_manager)

def get_default_manager(abstractions_manager, updates_manager, discriminator_manager):
    return PureLeonRefinementManager(abstractions_manager, updates_manager, discriminator_manager)
    #return MemOrbRefinementManager(abstractions_manager, updates_manager, discriminator_manager)
    
def get_leon_manager(abstractions_manager, updates_manager, discriminator_manager):
    return PureLeonRefinementManager(abstractions_manager, updates_manager, discriminator_manager)

def get_member_manager(abstractions_manager, updates_manager, discriminator_manager):
    return MemOrbRefinementManager(abstractions_manager, updates_manager, discriminator_manager)

def get_identity_manager(abstractions_manager, updates_manager, discriminator_manager):
    return IdentityRefinementManager(abstractions_manager, updates_manager, discriminator_manager)

class RefinementManager():
    pass

class PureLeonRefinementManager():
    def __init__(self, abstractions_manager, updates_manager, discriminator_manager):
        self.updates_manager = updates_manager
        self.base_changer = abstractions_manager
        self.disc_manager = discriminator_manager
        #self.orb_refiner = OrbitStabaliser(self.base_changer, updates_manager, discriminator_manager)
        self.orb_refiner = OrbitImageSuperRefiner(self.base_changer, updates_manager, discriminator_manager)

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
    
    

class MemOrbRefinementManager():
    def __init__(self, abstractions_manager, updates_manager, discriminator_manager):
        self.updates_manager = updates_manager
        self.base_changer = abstractions_manager
        self.disc_manager = discriminator_manager
        self.mem_refiner = MemberRefinement(self.base_changer, updates_manager, discriminator_manager)
        self.orb_refiner = OrbitStabaliser(self.base_changer, updates_manager, discriminator_manager)

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

class OrbitalGraphTracker():
    #says what the current orbital graphs are.
    pass

class OrbitTracker():
    #says what the orbits for each level are for current stack.
    pass

class OrbitImageRefinement_INPROGRESS():
    def __init__(self, orb_stab, base_changer, updates_manager):
        self.orb_stab = orb_stab
        self.updates_manager = updates_manager
        self.base_changer = base_changer
        self.update_token = 0
    
    def refine(self, stack):
        #b be fix end. Go up the fundamental orbits till b is found let 'a' be 
        #the stab at this point.
        #find g such that g takes a to b
        #then apply g to each non-distinguishable set of orbits in fix till a
        #and extend by those images.
        
        #new_base_eles, heights = self.updates_manager.fix_info(prestack_height)
        cur_fix = self.updates_manager.fix()
        #if _debug: print("-fix: {}".format(cur_fix))
        self.base_changer.change_base(cur_fix)        
        b = cur_fix[-1]
        
        if _debug: print("-orbit image info {} {}".format(self.start_heights, self.orb_sizes))
        for stab in self.part_stabs:
            if stab is not None:
                func = stab.refinement_function()
                if self.updates_manager.multi_add(func):
                    self.disc_manager.update(stab.discriminator_info(), len(self.updates_manager))                
                    return True
        return False

class OrbitImageSuperRefiner():
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
        
        func, func_info = self._image_refine_func(stack)
        if func is not None:
            if self.updates_manager.multi_add(func):
                self.disc_manager.update(func_info, len(self.updates_manager))
                return True
                
        
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
        
    def _image_refine_func(self, stack):
        fix, heights = self.updates_manager.fix_info()
        if len(fix) < 2:
            return None, None
        else:
            b = fix[-1]
            
            orbits = self.base_changer.stabaliser_orbits()
            index_limit = min(len(orbits) - 1, len(fix) - 1)
            a = None
            crit_level = None
            for level in range(index_limit, -1, -1):
                if b in orbits[level]:
                    a = fix[level]
                    crit_index = level
            if a is None:
                return None, None
            
            image = fix[:crit_index] + [b]
            g = self.base_changer.element_from_image(image)
            
            crit_height = heights[crit_index]
            
            des_stab_index = None
            for stab_index, height in enumerate(self.start_heights):
                if height == crit_height:
                    des_stab_index = stab_index
            
            if _asserts: assert(des_stab_index is not None)
            
            stab = self.part_stabs[des_stab_index]
            if stab is not None:
                #G_a orbits are considered trivial for some reason
                to_permute = stab.undifferentiables_list()
            else:
                if _asserts:len(self.base_changer.orbits(crit_height))==stack.degree
                to_permute = [cell for cell in stack[-1]]
            
            lookup = dict()
            for index, cell in enumerate(to_permute):
                for ele in cell:
                    image = ele ** g
                    lookup[image] = index
            #print(to_permute)
            #input()
            func = lambda x: lookup[x]
            #print(fix)
            #print(orbits)
            #print(orbits[crit_index])
            #print("{} -> {}".format(a,b))
            #print(g)
            #print(self.base_changer.orbits(crit_index + 1))
            #print(heights[crit_index])
            
            #input()
            #go up the fundamental orbits
            return func, ("oir",crit_index)
        return None, None
    
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
    
    def undifferentiables_list(self):
        ret = []
        for eles in self.derived[-1]:
            cell = []
            for ele in eles:
                index = ele - 1
                cell.extend(self.partition[index])
            ret.append(cell)
        return ret
            
    #update with the current changes lazily?
    
    #advise on refinements if asked
    
    #tell if dominated by another??
    

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
    
class IdentityRefinementManager():
    def __init__(self, ab_man, up_man, disc_man):
        pass
    
    def refine(self, stack):
        return False
    
class OrbitalGraphRefiner():
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
        
        func, func_info = self._image_refine_func(stack)
        if func is not None:
            if self.updates_manager.multi_add(func):
                self.disc_manager.update(func_info, len(self.updates_manager))
                return True
                
        
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
        
    def _image_refine_func(self, stack):
        fix, heights = self.updates_manager.fix_info()
        if len(fix) < 2:
            return None, None
        else:
            b = fix[-1]
            
            orbits = self.base_changer.stabaliser_orbits()
            index_limit = min(len(orbits) - 1, len(fix) - 1)
            a = None
            crit_level = None
            for level in range(index_limit, -1, -1):
                if b in orbits[level]:
                    a = fix[level]
                    crit_index = level
            if a is None:
                return None, None
            
            image = fix[:crit_index] + [b]
            g = self.base_changer.element_from_image(image)
            
            crit_height = heights[crit_index]
            
            des_stab_index = None
            for stab_index, height in enumerate(self.start_heights):
                if height == crit_height:
                    des_stab_index = stab_index
            
            if _asserts: assert(des_stab_index is not None)
            
            stab = self.part_stabs[des_stab_index]
            if stab is not None:
                #G_a orbits are considered trivial for some reason
                to_permute = stab.undifferentiables_list()
            else:
                if _asserts:len(self.base_changer.orbits(crit_height))==stack.degree
                to_permute = [cell for cell in stack[-1]]
            
            lookup = dict()
            for index, cell in enumerate(to_permute):
                for ele in cell:
                    image = ele ** g
                    lookup[image] = index
            #print(to_permute)
            #input()
            func = lambda x: lookup[x]
            #print(fix)
            #print(orbits)
            #print(orbits[crit_index])
            #print("{} -> {}".format(a,b))
            #print(g)
            #print(self.base_changer.orbits(crit_index + 1))
            #print(heights[crit_index])
            
            #input()
            #go up the fundamental orbits
            return func, ("oir",crit_index)
        return None, None
    
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


class BlockSystemRefiner():
    pass