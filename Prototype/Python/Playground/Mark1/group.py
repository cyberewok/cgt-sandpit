class Permutation():
    def __init__(self, nums, size=0):
        if size==0:
            self.size=len(nums)
        else:
            self.size=size
        self.func=nums
    
    def _image(self, num):
        if num < 1 or num > self.size:
            raise ValueError("{} has no image as out of bounds.".format(num))
        else:
            return self.func[num-1]
    
    def _images(self, nums):
        return [self._image(num) for num in nums]
    
    def __add__(self, perm):
        if type(perm) is not type(self):
            raise TypeError("Incompatable types {} and {}".format(type(perm), type(self)))
        if perm.size != self.size:
            raise ValueError("Incompatable sizes {} and {}".format(perm.size, self.size))        
        return Permutation(perm._images(self.func))
    
    def __mul__(self, num):      
        return self._image(num)    
    
    def __str__(self):
        return str(self._cycle_notation())
    
    def _cycle_notation(self):
        ret=[]
        todo=list(range(1, self.size+1))
        while len(todo)>0:
            first=todo.pop(0)
            nex=self._image(first)
            if nex!=first:
                todo.remove(nex)
                cycle = [first, nex]
                nex=self._image(nex)               
                while nex!=first:
                    todo.remove(nex)
                    cycle.append(nex)
                    nex=self._image(nex)
                ret.append(cycle)
        return ret
                
            
        

#class Group():
 #   def __init__(self, generators):