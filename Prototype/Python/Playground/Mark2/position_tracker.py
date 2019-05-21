class PositionTracker():
    def __init__(self, mods):
        self.mods = []
        for ele in mods:
            if ele is None or ele < 1:
                self.mods.append(1)
            else:
                self.mods.append(ele)
        self._height = len(mods)
        self._cur_state = [0] * self._height
    
    def increment(self, index = None):#incrementor function for the naive traversal
        if index is None:
            index = self._height - 1
        sig = self._height - 1
        while sig > index:
            self._cur_state[sig] = 0            
            sig -= 1
        while sig >= 0 and (self._cur_state[sig] + 1) % self.mods[sig] == 0:
            self._cur_state[sig] = 0
            sig -= 1
        if sig >= 0:
            self._cur_state[sig] += 1
        #else:
           # raise StopIteration("Can not increment further.")
        return sig
    
    def min_changed_index(self):
        for index, val in enumerate(self._cur_state):
            if val > 0:
                return index
        return self._height - 1
            
    
    def __getitem__(self, key):
        return self._cur_state[key]
    
    def __str__(self):
        return str(self._cur_state)

class DynamicPositionTracker(PositionTracker):
    def __init__(self):
        super().__init__([])
    
    def add_level(self, level_size):
        self._cur_state.append(0)
        self.mods.append(max(level_size,1))
        self._height += 1
    
    def pop_level(self):
        self._cur_state.pop()
        self.mods.pop()
        self._height -= 1        

    def increment(self, index = None):
        if index is None:
            index = self._height - 1
        sig = self._height - 1
        while sig > index:
            self._cur_state[sig] = 0            
            sig -= 1
            self.pop_level()
        while sig >= 0 and (self._cur_state[sig] + 1) % self.mods[sig] == 0:
            self._cur_state[sig] = 0
            sig -= 1
            self.pop_level()
        if sig >= 0:
            self._cur_state[sig] += 1
        #else:
           # raise StopIteration("Can not increment further.")
        return sig
    
class NaivePositionTracker():
    def __init__(self):
        self._orbit_reps = []#lists of elements from each split cell iterate over.
        self._cur_state = []#index of current element in each split cell
        self._mods = []#number of elements in each split cell
        self._cell_indices = []#index of each split cell
        self._stack_heights = []#height of the stack for each split
    
    def add_level(self, cell_index, cell, height):
        self._cur_state.append(0)
        self._mods.append(max(len(cell),1))
        self._orbit_reps.append(cell)
        self._cell_indices.append(cell_index)
        self._stack_heights.append(height)     
    
    def pop_level(self):
        self._cur_state.pop()
        self._mods.pop()
        self._orbit_reps.pop()
        self._cell_indices.pop()
        self._stack_heights.pop()             
    
    def increment(self, new_height = None):#incrementor function for the naive traversal
        ret = -1
        sig = len(self._cur_state) - 1
        if new_height is None:
            new_height = self._stack_heights[sig]
        while self._stack_heights[sig] > new_height:
            self.pop_level()
            sig -= 1
        while sig >= 0 and (self._cur_state[sig] + 1) % self._mods[sig] == 0:
            self.pop_level()
            sig -= 1
            
        if sig >= 0:
            self._cur_state[sig] += 1
            ret = self._stack_heights[sig]
            
        return sig, ret
    
    def split_index(self):
        return self._cell_indices[-1]
        
    def split_value(self):
        return self._orbit_reps[-1][self._cur_state[-1]]
        