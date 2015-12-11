class Permutation():
    def __init__(self, nums):
        self._func = tuple(nums)
        self._cycle_form = None
    
    @staticmethod
    def read_cycle_form(cycle_form, size):
        nums = list(range(1, size + 1))    
        for cycle in cycle_form:
            first = cycle[0]
            last = cycle[-1]
            nums[last - 1] = first
            prev = first
            for num in cycle[1:]:
                nums[prev - 1] = num
                prev = num
        ret = Permutation(nums)
        return ret
    
    def _image(self, num):
        return self._func[num-1]
    
    def _images(self, nums):
        return [self._image(num) for num in nums]
    
    def __lt__(self, other):
        num_cycles = len(self.cycle_notation())
        num_cycles_other = len(other.cycle_notation())
        if num_cycles != num_cycles_other:
            return num_cycles < num_cycles_other
        cycle_sizes = [len(cycle) for cycle in self.cycle_notation()]
        cycle_sizes_other = [len(cycle) for cycle in other.cycle_notation()]
        if cycle_sizes != cycle_sizes_other:
            return cycle_sizes > cycle_sizes_other
        return self.cycle_notation() < other.cycle_notation()
    
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
        else:
            raise TypeError("Cannot find inverse for {} {}.".format(type(self), num))
    
    __xor__ = __pow__    
    
    def __rpow__(self, num):
        if not isinstance(num, int):
            raise TypeError("Cannot find image for types {} and {}.".format(type(num), type(self)))
        return self._image(num)    
    
    __rxor__ = __rpow__     
    
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

def main():
    print(a)
    print(b)
    print(a*b)
    print(1**b)
    print(a**-1)
    print(a**-1 * a)
    print(a * a**-1)
    print(1 ** a ** -1)
    print((a * a**-1)._func)
    print(c)
    print(c._func)
    

if __name__ == "__main__":
    a=Permutation([2,3,1,4])
    b=Permutation([2,1,4,3])
    c=Permutation([])
    main()