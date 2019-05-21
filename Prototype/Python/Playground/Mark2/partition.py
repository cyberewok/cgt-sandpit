from permutation import Permutation
"""This module contains partition and partition stack support."""

class Partition():
    def __init__(self, ordered_partitions, sort_cells = True, checks = True):
        if sort_cells:
            self._cells = tuple([sorted(cell) for cell in ordered_partitions])
        else:
            self._cells = tuple(ordered_partitions)
        if checks:
            unique = set()
            for cell in self._cells:
                for ele in cell:
                    if ele in unique:
                        raise ValueError("Can not have duplicate elements in a partition.")
                    unique.add(ele)
            if len(unique) > 1:
                if min(unique) != 1:
                    raise ValueError("Can not have elements under one in partition.")
                if max(unique) > len(unique):
                    raise ValueError("Partition is missing numbers.")
        
    def __lt__(self, other):
        return NotImplemented
    
    def __pow__(self, perm):
        if isinstance(perm, Permutation):
            new_cells = [[num ** perm for num in cell] for cell in self._cells]
            return Partition(new_cells)
        raise TypeError("Cannot find image for types {} and {}.".format(type(self), type(perm))) 
    
    def __str__(self):
        element_list = [" ".join([str(num) for num in cell]) for cell in self._cells]
        return "[ {} ]".format(" | ".join(element_list))

    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return len(self._cells)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._cells == other._cells
        else:
            return False
        
    def __getitem__(self, i):
        return self._cells[i]
    
    def extend(self, index, split_cell, checks = True):
        index_cell = self._cells[index]
        index_set = set(index_cell)
        if checks:
            new_cell = sorted(list(set(split_cell) & index_set))
        else:
            new_cell = split_cell
        ret_cells = [cell for cell in self._cells]                    
        if len(new_cell) > 0 and len(new_cell) < len(index_cell):
            leftovers = sorted(list(index_set.difference(new_cell)))
            ret_cells[index] = leftovers
            ret_cells.append(new_cell)
        return Partition(ret_cells, False)

    def discrete(self):
        return max(len(cell) for cell in self._cells) == 1

class PartitionStack():
    def __init__(self, final_indices, split_indices):
        self._height = max(final_indices) + 1
        self._finals = final_indices #the cell num for each index in the top partition.
        self._parents = split_indices #the most immediate parent cell.
        self.degree = len(self._parents) #this is needed
    
    @classmethod
    def deep_copy(cls, stack):
        finals = list(stack._finals)
        splits = list(stack._parents)
        return cls(finals, splits)    
    
    @classmethod
    def single_partition_stack(cls, partition):
        size = sum([len(cell) for cell in partition])
        finals = [0] * size
        splits = [-1] * size
        for index, cell in enumerate(partition):
            for ele in cell:
                finals[ele - 1] = index
                splits[ele - 1] = 0 if index > 0 else -1
        return cls(finals, splits)
        
    def __lt__(self, other):
        return NotImplemented
    
    def __str__(self):
        return "{}|{}".format(self._finals, self._parents)
    
    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return self._height
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            same_finals = self._finals == other._finals
            same_parents = self._parents == other._parents
            return same_finals and same_parents
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            copy = self.deep_copy(self)
            stop_con = key.stop
            while copy._height > stop_con:
                copy.pop()
            return copy
        elif isinstance(key, int):
            cells = [[] for _ in range(self._height)]
            
            if key < 0:
                key = key + self._height
            
            if key < 0 or key >= self._height:
                raise IndexError(key)
            
            for enum, cell_index in enumerate(self._finals):
                element = enum + 1
                cells[cell_index].append(element)
        
            for cell in reversed(cells[key + 1:]):
                min_split = self._parents[cell[0] - 1]
                cells[min_split] += cell
        
            return Partition(cells[:key + 1])
        elif isinstance(key, tuple):
            #Place holder. Will be something more clever when partition stacks are improved.
            #Aim is for the whole partition not to be queered when all we want is one cell.
            return self[key[0]][key[1]]
        else:
            raise TypeError("{} not supported for indexing".format(type(key)))
    
    def __pow__(self, perm):
        
        if isinstance(perm, Permutation):        
            degree = len(self._parents)
            lookup = {(val + 1) : (val + 1) ** perm for val in range(degree)}
            new_fins = [self._finals[lookup[val + 1] - 1] for val in range(degree)]
            new_pars = [self._parents[lookup[val + 1] - 1] for val in range(degree)]
            return PartitionStack(new_fins, new_pars)
        raise TypeError("Cannot find image for types {} and {}.".format(type(self), type(perm))) 
        
    def multi_extend(self, func):
        changed = False
        split_cell_dicts = [dict() for _ in range(len(self))]
        for index in range(self.degree):
            cell_index = self._finals[index]
            element = index + 1
            element_value = func(element)
            if element_value in split_cell_dicts[cell_index]:
                split_cell_dicts[cell_index][element_value].append(element)
            else:
                split_cell_dicts[cell_index][element_value] = [element]
        for index, split_cell_dict in enumerate(split_cell_dicts):
            element_values = split_cell_dict.keys()            
            non_mins = sorted(element_values)[1:]
            for key in reversed(non_mins):
                changed = True
                split_cell = split_cell_dict[key]
                self.extend(index, split_cell, checks = False)
        return changed
    
    def extend(self, index, split_cell, checks = True):
        if checks:
            new_cell = self._valid_intersection(index, split_cell)
            if new_cell is None:
                return self
        else:
            new_cell = split_cell        
        
        for element in new_cell:
            self._finals[element - 1] = self._height
            self._parents[element - 1] = index
        self._height += 1

        return self
    
    def can_extend(self, index, split_cell):
        return self._valid_intersection(index, split_cell) is not None
    
    def cell_of(self, element, level = None):
        if level is None:
            return self._finals[element - 1]
        
    def _valid_intersection(self, index, split_cell):
        new_cell = [e for e in split_cell if self._finals[e - 1] == index]
        empty = len(new_cell) == 0  
        too_big = len(new_cell) == len([1 for x in self._finals if x==index])
        if empty or too_big:
            return None
        return new_cell
    
    def _fast_fix(self):
        ret_val = []
        cell_reps = [(False, None) for _ in range(self._height)]
        
        for enum, cell_index in enumerate(self._finals):
            element = enum + 1
            if cell_reps[cell_index][1] is None:    
                cell_reps[cell_index] = [True, element]
            else:
                cell_reps[cell_index][0] = False

        for sing, cell_rep in reversed(cell_reps):
            parent_index = self._parents[cell_rep - 1]
            if parent_index < 0:
                parent_sing = False                
            else:
                parent_sing, parent_rep = cell_reps[parent_index]
            if parent_sing:
                ret_val.append(parent_rep)
                cell_reps[parent_index][0] = False
            if sing:
                ret_val.append(cell_rep)
        
        ret_val.reverse()
        return ret_val
    
    def _fast_fix_with_info(self, start_height):
        ret_val = []
        ret_heights = []
        cell_reps = [(False, None) for _ in range(self._height)]
        
        for enum, cell_index in enumerate(self._finals):
            element = enum + 1
            if cell_reps[cell_index][1] is None:    
                cell_reps[cell_index] = [True, element]
            else:
                cell_reps[cell_index][0] = False

        for sing, cell_rep in reversed(cell_reps):
            if self._finals[cell_rep-1] + 1 <= start_height:
                break
            parent_index = self._parents[cell_rep - 1]
            if parent_index < 0:
                parent_sing = False                
            else:
                parent_sing, parent_rep = cell_reps[parent_index]
            if parent_sing:
                ret_val.append(parent_rep)
                ret_heights.append(self._finals[cell_rep - 1] + 1)
                cell_reps[parent_index][0] = False
            if sing:
                ret_heights.append(self._finals[cell_rep - 1] + 1)
                ret_val.append(cell_rep)
        
        ret_val.reverse()
        ret_heights.reverse()
        return ret_val, ret_heights
    
    def fix_info(self, start_height = 0):
        #returns fix and the heights the 
        #elements were introduced in only gives
        #the fix after the start_height
        return self._fast_fix_with_info(start_height)
    
    def fix(self):
        return self._fast_fix()
        #ret_val = []
        #cells = [[] for _ in range(self._height)]
        
        #for enum, cell_index in enumerate(self._finals):
            #element = enum + 1
            #cells[cell_index].append(element)

        #for cell in reversed(cells):
            #if len(cell) == 1:
                #element = cell[0]
                #parent_cell = cells[self._parents[element - 1]]
                #if len(parent_cell) == 1:
                    #ret_val = cell + parent_cell + ret_val
                #else:
                    #ret_val = cell + ret_val
                    
            #parent = self._parents[cell[0] - 1]
            #cells[parent] += cell

        #return ret_val
    
    def pop_to_height(self, new_height):
        if new_height > self._height:
            raise IndexError("The new height {} is greater than {}.".format(new_height, self._height))
        while self._height > new_height:
            self.pop()
        return self
    
    def pop(self):
        top_partition = self[-1]
        
        if self._height == 1:
            raise IndexError("pop from unitary stack")
            
        new_cell_index = self._parents[top_partition[-1][0] - 1]   
        new_parent_index = self._parents[top_partition[new_cell_index][0] - 1] 
        
        for element in top_partition[-1]:
            self._finals[element - 1] = new_cell_index
            self._parents[element - 1] = new_parent_index
            
        self._height -= 1    
        return self
    
    def discrete(self):
        #Only works for complete partition stacks.
        #cells = set()
        #for cell_id in self._finals:
        #    cells.add(cell_id)
        #return len(cells) == len(self._finals)
        #return max(self._finals) == len(self._finals) - 1
        return len(self._finals) == self._height
    
    def canonical_form(self):
        ordered_finals = sorted(zip(self._parents, self._finals), key = lambda x:(x[0],-1 * x[1]))
        con_parents = [parent for parent,_ in ordered_finals]
        con_finals = [final for _,final in ordered_finals]
        return PartitionStack(con_finals, con_parents)
    
    def signature(self):
        ret = []
        for part in self:
            end = part[-1]
            split = min((self._parents[val - 1] for val in end))
            ret.append((len(end), split))
        return ret
    
    def report_changes(self, prev_height = 1):
        ret = []
        for element, cell_index in enumerate(self._finals):
            element += 1
            if cell_index >= prev_height:
                insert_index = cell_index - prev_height 
                while len(ret) <= insert_index:
                    ret.append([])
                ret[insert_index].append(element)
        return ret