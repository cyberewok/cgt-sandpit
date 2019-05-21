from group import PermGroup

#This code needs cleaning up. This will be done if it is used as a test bed for
#any conjugacy things.

def backtrack_subgroup(super_group, group_property, cull_heuristic):
    size = len(super_group.identity)
    sbw = SimsBacktrackWorkhorse(super_group, group_property.check, cull_heuristic, size)
    gens = sbw.find_subgroup()
    return PermGroup(gens)

class SimsBacktrackWorkhorse():
    def __init__(self, super_group, prop_check, cull_heuristic, size):
        self.group = super_group
        self.size = size
        self.prop_check = prop_check
        self.cull_check = cull_heuristic
        self.base = self.group.base
        self.order = self.base + sorted(list(set(range(1, self.size + 1)) - set(self.base)))
        self.order_lookup = [None] * self.size
        for index, element in enumerate(self.order):
            self.order_lookup[element - 1] = index
        self.key = lambda x: self.order_lookup[x - 1]
        self.perm_key = lambda perm: [self.order_lookup[ele - 1] for ele in perm._func]
        self.cur_state = []
        self.cur_used = [False] * len(self.order)        
    
    def find_subgroup(self):
        double_coset_culling = False
        multi_level_popping =True
        actual_minimal_in_coset = True
        use_cull_heuristic = False
        print_internal_nodes = True
        print_leaf_nodes = True
        gens = []
        self.cur_state = []
        self.cur_used = [False] * len(self.order)
        finished = False
        count = 0
        coset_level = len(self.base)
        while not finished:
            count += 1
            #deal with this vertex
            if len(self.cur_state) < len(self.base):
                #internal vertex
                #if self.cull_heuristic(base, cur_state):
                #PermGroup.fixed_base_group(gens, cur_state)
                if print_internal_nodes:
                    print("{} (internal)".format(self.cur_state))
                if use_cull_heuristic:
                    if self.cull_check(self.base[0: len(self.cur_state)], self.cur_state):
                        if not self._across_level():
                            break
                        else:
                            coset_level = min(coset_level, len(self.cur_state))
                        continue                        
                if double_coset_culling:
                    if not self.minimal_double_coset(gens):
                        #print("Node contains no minimal elements.")
                        if not self._across_level():
                            break
                        else:
                            coset_level = min(coset_level, len(self.cur_state))
                        continue
                        
            else:
                #leaf
                leaf = self.group.base_image_member(self.cur_state)
                if print_leaf_nodes:
                    print(leaf)
                if actual_minimal_in_coset:
                    G = PermGroup(gens + [self.group.identity])
                    dcs = G*leaf*G
                    #print("double coset: {} Group: {} ({})  min: {} {} {}".format(dcs._list_elements(key = self.perm_key), [g for g in G._list_elements(key = self.perm_key)], len(G), dcs.minimal_rep(key=self.perm_key), dcs.minimal_rep(key=self.perm_key)==dcs.mid_rep, dcs.mid_minimal(key=self.perm_key)))
                    if dcs.mid_minimal(key=self.perm_key):
                        print("ACTUAL MINIMAL!")               
                if leaf != self.group.identity and self.prop_check(leaf):
                    print("FOUND ELEMENT!")                    
                    gens.append(leaf)
                    # found an element so pop till new coset
                    if multi_level_popping:
                        while coset_level < len(self.cur_state):
                            if not self._up_level():
                                break
                        if not self._across_level():
                            break
                        else:
                            coset_level = min(coset_level, len(self.cur_state))                        
                        continue
               
            #print("{}".format(self.cur_state))
            if len(self.cur_state) < len(self.base) and self._down_level():
                continue
            if self._across_level():
                coset_level = min(coset_level, len(self.cur_state))
                continue
            if len(self.cur_state) == 0:
                finished = True
        return gens
            
        
    def _down_level(self, start_index = 0):
        index = start_index
        while index < len(self.cur_used) and self.cur_used[index]:
            index += 1
        if index >= len(self.cur_used):
            return False
        self.cur_state.append(self.order[index])
        self.cur_used[index] = True
        return True

    def _across_level(self):
        if len(self.cur_state) < 1:
            return False
        ele = self.cur_state.pop()
        index = self.order_lookup[ele - 1]
        self.cur_used[index] = False
        if not self._down_level(index + 1):
            return self._across_level()
        return True

    def _up_level(self):
        if len(self.cur_state) < 1:
            return False
        ele = self.cur_state.pop()
        self.cur_used[self.order_lookup[ele - 1]] = False
        return True

    def minimal_double_coset(self, gens):
        return self.double_coset_1(self.base[0: len(self.cur_state)], self.cur_state,gens,key= self.key)
    
    def double_coset_1(self, base, image, gens, key = None):
        #base change (for now just recompute base but should do the proper algorithm)
        if len(image) == 0 or len(gens) == 0:
            return True
        G = PermGroup.fixed_base_group(gens, image[:-1])
        orb = G.orbit(image[-1], stab_level = len(base) - 1, key = key)
        #print("Orbit of {} is {} in {}".format(image[-1], orb, G._list_elements()))
        if image[-1] == orb[0]:
            return True
        return False    