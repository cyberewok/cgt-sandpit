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
        