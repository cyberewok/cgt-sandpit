"""This module contains partition and partition stack support."""

class Partition():
    def __init__(self, ordered_partitions, sort_cells = True):
        if sort_cells:
            self._cells = tuple([sorted(cell) for cell in ordered_partitions])
        else:
            self._cells = tuple(ordered_partitions)
        
    def __lt__(self, other):
        return NotImplemented
    
    def __pow__(self, num):
        return NotImplemented 
    
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
    
    def extend(self, index, split_cell, checks = True):
        index_cell = self._cells[index]
        index_set = set(index_cell)
        if checks:
            new_cell = sorted(list(set(split_cell) & index_set))
        else:
            new_cell = split_cell
        if len(new_cell) > 0:
            leftovers = sorted(list(index_set.difference(new_cell)))
            ret_cells = [cell for cell in self._cells]
            ret_cells[index] = leftovers
            ret_cells.append(new_cell)
        return Partition(ret_cells, False)

class PartitionStack():
    def __init__(self, final_indices, split_indices):
        self.height = max(final_indices)
        self.final_indices = final_indices
        self.split_indices = split_indices
    
    def __lt__(self, other):
        return NotImplemented
    
    def __str__(self):
        return NotImplemented
    
    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return self.height
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return NotImplemented
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other) 
        
    def cycle_notation(self):
        if not self._cycle_form is None:
            return self._cycle_form
        ret = []
        todo = [1 for _ in range(len(self) + 1)]
        for first in range(1, len(todo)):
            if todo[first] == 0:
                continue
            nex = self._image(first)
            if nex != first:
                todo[first] = 0
                todo[nex] = 0
                cycle = [first, nex]
                nex = self._image(nex)
                while nex != first:
                    todo[nex] = 0
                    cycle.append(nex)
                    nex = self._image(nex)
                ret.append(cycle)
        ret.sort(key = lambda x: (len(x), x))
        #if len(ret) == 0:
            #ret.append([])
        self._cycle_form = ret
        return ret
