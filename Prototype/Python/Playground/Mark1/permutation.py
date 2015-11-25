class Permutation():
    def __init__(self, nums):
        self.func=nums
        self._cycle_form=None
    
    def _image(self, num):
        if num < 1 or num > len(self):
            raise ValueError("{} has no image as out of bounds.".format(num))
        else:
            return self.func[num-1]
    
    def _images(self, nums):
        return [self._image(num) for num in nums]
    
    def __mul__(self, perm):
        if not isinstance(perm, self.__class__):
            raise TypeError("Cannot multiply types {} and {}.".format(type(perm), type(self)))     
        return Permutation(perm._images(self.func))
    
    def __pow__(self, num):
        if num == -1:
            inverse = [-1 for _ in range(len(self))]
            for index, value in enumerate(self.func):
                inverse[value - 1] = index + 1
            return Permutation(inverse)
        else:
            raise TypeError("Cannot find inverse for {} {}.".format(type(self), num))
        
    def __rpow__(self, num):
        if not isinstance(num, int):
            raise TypeError("Cannot find image for types {} and {}.".format(type(num), type(self)))
        return self._image(num)    
    
    def __str__(self):
        return str(self.cycle_notation())#[1:-1]
    
    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return len(self.func)
        
    def cycle_notation(self):
        if not self._cycle_form is None:
            return self._cycle_form
        ret = []
        todo = [0 for _ in range(len(self) + 1)]
        for first in range(1, len(todo)):
            if todo[first] == -1:
                continue
            nex = self._image(first)
            if nex != first:
                todo[first] = -1
                todo[nex] = -1
                cycle = [first, nex]
                nex = self._image(nex)               
                while nex != first:
                    todo[nex] = -1
                    cycle.append(nex)
                    nex = self._image(nex)
                ret.append(cycle)
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
    print((a * a**-1).func)
    print(c)
    print(c.func)
    

if __name__ == "__main__":
    a=Permutation([2,3,1,4])
    b=Permutation([2,1,4,3])
    c=Permutation([])
    main()