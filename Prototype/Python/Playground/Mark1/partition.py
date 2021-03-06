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
            new_cells = []
            for cell in self._cells:
                new_cell = []
                for num in cell:
                    new_cell.append(num ** perm)
                new_cells.append(new_cell)
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
        self._parents = split_indices #the max height at which this element was put at end.
        self.base_size = len(self._parents)
    
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
    
    def __getitem__(self, index):
        cells = [[] for _ in range(self._height)]
        
        if index < 0:
            index = index + self._height
        
        for enum, cell_index in enumerate(self._finals):
            element = enum + 1
            cells[cell_index].append(element)

        for cell in reversed(cells[index + 1:]):
            min_split = self._parents[cell[0] - 1]
            cells[min_split] += cell

        return Partition(cells[:index + 1])
    
    def extend(self, index, split_cell, checks = True):
        if checks:
            new_cell = [e for e in split_cell if self._finals[e - 1] == index]
            empty = len(new_cell) == 0  
            too_big = len(new_cell) == len([1 for x in self._finals if x==index])
            if empty or too_big:
                return self
        else:
            new_cell = split_cell        
        
        for element in new_cell:
            self._finals[element - 1] = self._height
            self._parents[element - 1] = index
        self._height += 1

        return self
    
    def fix(self):
        ret_val = []
        cells = [[] for _ in range(self._height)]
        
        for enum, cell_index in enumerate(self._finals):
            element = enum + 1
            cells[cell_index].append(element)

        for cell in reversed(cells):
            if len(cell) == 1:
                element = cell[0]
                parent_cell = cells[self._parents[element - 1]]
                if len(parent_cell) == 1:
                    ret_val = cell + parent_cell + ret_val
                else:
                    ret_val = cell + ret_val
                    
            parent = self._parents[cell[0] - 1]
            cells[parent] += cell

        return ret_val
    
    def pop(self):
        top_partition = self[-1]
        
        new_cell_index = self._parents[top_partition[-1][0] - 1]   
        new_parent_index = self._parents[top_partition[new_cell_index][0] - 1] 
        
        for element in top_partition[-1]:
            self._finals[element - 1] = new_cell_index
            self._parents[element - 1] = new_parent_index
            
        self._height -= 1    
        return self
    
    def discrete(self):
        #cells = set()
        #for cell_id in self._finals:
        #    cells.add(cell_id)
        #return len(cells) == len(self._finals)
        #return max(self._finals) == len(self._finals) - 1
        return len(self._finals) == self._height