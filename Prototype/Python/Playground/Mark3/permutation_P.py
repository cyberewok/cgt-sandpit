"""This module contains all support for permutations. Including operations,
equality checks and hashing."""

class Permutation():
    def __init__(self, nums):
        self._func = tuple(nums)
        self._cycle_form = None
        self._cycle_lookup = None
        self._cycle_position = None
    
    @classmethod
    def read_cycle_form(cls, cycle_form, size = None):
        if size is None:
            size = max([max(cycle) for cycle in cycle_form])
        nums = list(range(1, size + 1))    
        for cycle in cycle_form:
            first = cycle[0]
            last = cycle[-1]
            nums[last - 1] = first
            prev = first
            for num in cycle[1:]:
                nums[prev - 1] = num
                prev = num
        return cls(nums)
    
    @classmethod
    def read_partitions(cls, part_a, part_b):
        nums = [0] * len(part_a)
        for index in range(len(part_a)):
            nums[part_a[index][0] - 1] = part_b[index][0]
        return cls(nums)
            
    def _image(self, num):
        return self._func[num-1]
    
    def _images(self, nums):
        return [self._image(num) for num in nums]
    
    def __lt__(self, other):
        return self._func<other._func
    
    def __mul__(self, perm):
        if not isinstance(perm, self.__class__):
            return NotImplemented   
        return Permutation(perm._images(self._func))
    
    def __pow__(self, num):
        if num == -1:
            inverse = [-1 for _ in range(len(self))]
            for index, value in enumerate(self._func):
                inverse[value - 1] = index + 1
            return Permutation(inverse)
        elif isinstance(num,int) and num>=0:
            return self._fast_cycle_expo(num)
        else:
            raise TypeError("Cannot compute exponent for type {} to the power of {}.".format(type(self), num))
    
    #__xor__ = __pow__    
    
    def __rpow__(self, num):
        if isinstance(num, int):
            return self._image(num)
        raise TypeError("Cannot find image for types {} and {}.".format(type(num), type(self)))
    
    #__rxor__ = __rpow__     
    
    def __str__(self):
        return str(self.cycle_notation())#[1:-1]
    
    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return len(self._func)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._func == other._func
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other) 
    
    def __hash__(self):
        return hash(self._func)
    
    def trivial(self):
        #if self._cycle_form is not None:    
        #   return len(self._cycle_form) == 0
        #else:
        for ele in range(1, len(self)):
            if not self._image(ele) == ele:
                return False
        return True
    
    def _initialise_cycle_form(self):
        self._cycle_form = []
        self._cycle_lookup = [None] * len(self)
        self._cycle_position = [None] * len(self)
    
    def _precached_cycle(self, element, reorder):        
        element_index = element - 1
        cycle_index = self._cycle_lookup[element_index]
        if cycle_index is not None:
            cycle = self._cycle_form[cycle_index]
            if reorder:
                index = self._cycle_position[element_index]
                cycle = cycle[index:] + cycle[:index]
            return cycle
        
        if self._cycle_position[element_index] is not None:
            return [element]
        
        return None
    
    def _element_cycle_non_cached(self, first):        
        cycle = [first]
        nex = self._image(first)
        while nex != first:
            cycle.append(nex)
            nex = self._image(nex)
        return cycle   
    
    def _element_cycle_cached(self, first):
        cycle = [first]
        nex = self._image(first)
        singleton = True
        self._cycle_position[first - 1] = -1
        while nex != first:
            if singleton:
                cycle_index  = len(self._cycle_form)
                count = 0
                self._cycle_form.append(cycle)
                self._cycle_lookup[first - 1] = cycle_index
                self._cycle_position[first - 1] = count
                singleton = False
            
            count += 1            
            self._cycle_lookup[nex - 1] = cycle_index
            self._cycle_position[nex - 1] = count
            
            cycle.append(nex)
            nex = self._image(nex)
        
        return cycle        
    
    def element_cycle(self, first, reorder = True, cache = True):
        if cache and self._cycle_form is None:
            self._initialise_cycle_form()
        
        if cache:
            ret = self._precached_cycle(first, reorder)
            if ret is not None:
                return ret
        
        if cache:
            return self._element_cycle_cached(first)
        else:
            return self._element_cycle_non_cached(first)

    def cycle_notation(self):
        if self._cycle_form is None:
            self._initialise_cycle_form()        
        
        for first in range(1, len(self)):
            if self._cycle_position[first - 1] is not None:
                continue
            self.element_cycle(first)
    
        return self._cycle_form
    
    def _fast_cycle_expo(self, num):
        ret = [-1] * len(self)
        for ele in range(1, len(self) + 1):
            if ret[ele - 1] == -1:
                cyc = self.element_cycle(ele, reorder = False)
                for cyc_index, cyc_ele in enumerate(cyc):
                    cyc_image = cyc[(cyc_index + num) % len(cyc)]
                    ret[cyc_ele - 1] = cyc_image
        return Permutation(ret)
    
    @staticmethod
    def cycle_length_comparison(self, other):
        num_cycles = len(self.cycle_notation())
        num_cycles_other = len(other.cycle_notation())
        if num_cycles != num_cycles_other:
            return num_cycles < num_cycles_other
        cycle_sizes = [len(cycle) for cycle in self.cycle_notation()]
        cycle_sizes_other = [len(cycle) for cycle in other.cycle_notation()]
        if cycle_sizes != cycle_sizes_other:
            return cycle_sizes > cycle_sizes_other
        return self.cycle_notation() < other.cycle_notation()    