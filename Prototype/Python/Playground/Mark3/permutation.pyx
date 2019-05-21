from cython_macros cimport size_to_array_C, list_to_array_C 
from cython_macros cimport array_to_list_C, fill_array_C
from cpython.mem cimport PyMem_Malloc, PyMem_Free

cdef array_to_permutation_C(int* nums, size_t size):
    #Hacky way of bypassing the initialiser
    ret = Permutation(None)
    ret._func = nums
    ret._degree = size
    return ret

cdef class Permutation:
        
    def __cinit__(self, nums):

        if nums is not None:
            self._degree = len(nums)
            self._func = list_to_array_C(nums)
    
    def __dealloc__(self):
        PyMem_Free(self._func)

    @classmethod
    def read_cycle_form(cls, cycle_form, size = None):
        if size is None:
            size = max([max(cycle) for cycle in cycle_form])
            
        cdef int* nums = size_to_array_C(size)
        cdef int index
        for index in range(size):
            nums[index] = index + 1
        
        for cycle in cycle_form:
            first = cycle[0]
            last = cycle[-1]
            nums[last - 1] = first
            prev = first
            for num in cycle[1:]:
                nums[prev - 1] = num
                prev = num

        return array_to_permutation_C(nums, size)
    
    @classmethod
    def read_partitions(cls, part_a, part_b):
        cdef int* nums = size_to_array_C(len(part_a))
        cdef int index
        for index in range(len(part_a)):
            nums[part_a[index][0] - 1] = part_b[index][0]
        return array_to_permutation_C(nums, len(part_a))

    def __richcmp__(Permutation self, Permutation other, int op_type):
        #explicit type check
        if (not isinstance(self, Permutation)) or (not isinstance(other, Permutation)) or len(self) != len(other):
            return NotImplemented

        if op_type == 0:#<
            return self._lt_help(other)
        elif op_type == 1:#<=
            return self._lteq_help(other)
        elif op_type == 2:#==
            return self._eq_help(other)
        elif op_type == 3:#!=
            return not self._eq_help(other)
        elif op_type == 4:#>
            return not self._lteq_help(other)
        elif op_type == 5:#>=
            return not self._lt_help(other)
    
    cdef _lt_help(Permutation self, Permutation other):
        cdef int index
        for index in range(len(self)):
            if self._func[index] != other._func[index]:
                return self._func[index] < other._func[index]
            
        return False
    
    cdef _lteq_help(Permutation self, Permutation other):
        cdef int index
        for index in range(len(self)):
            if self._func[index] != other._func[index]:
                return self._func[index] < other._func[index]
            
        return True
        
    cdef _eq_help(Permutation self, Permutation other):
        cdef int index
        for index in range(len(self)):
            if self._func[index] != other._func[index]:
                return False

        return True    
    
    cpdef int _image(self, int num):
        return self._func[num-1]
        
    cpdef Permutation _mul_helper_perm_level(self, Permutation other):
        
        cdef int* ret = size_to_array_C(len(self))
        
        cdef int* left = self._func
        cdef int* right = other._func
        
        cdef int index
        for index in range(len(self)):
            ret[index] = right[left[index] - 1]

        return array_to_permutation_C(ret, len(self))
    
    def __mul__(self, perm):
        if (not isinstance(self, Permutation)) or (not isinstance(perm, Permutation)) or len(self) != len(perm):
            return NotImplemented
        return self._mul_helper_perm_level(perm)
    
    cpdef Permutation _inverse(self):
        cdef int* inverse = size_to_array_C(len(self))
        cdef int index, value

        for index in range(len(self)):
            value = self._func[index]
            inverse[value - 1] = index + 1

        return array_to_permutation_C(inverse, len(self))
        
    
    def __pow__(self, num, mod):
        
        if isinstance(num, Permutation):
            #num is the permutation
            if isinstance(self, int) and 0 < self <= len(num):
                return num._image(self)
            return NotImplemented
    
        elif num == -1:
            return self._inverse()
            
        elif isinstance(num, int) and num >= 0:
            return self._fast_cycle_expo(num)

        else:
            return NotImplemented
            #raise TypeError("Cannot compute exponent for type {} to the power of {}.".format(type(self), num))
    
    def __str__(self):
        return str(self.cycle_notation())#[1:-1]
    
    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return self._degree
    
    def __hash__(self):
        cdef int index, value, ret, offset
        ret = 1
        offset = 31
        for index in range(len(self)):
            value = self._func[index]
            ret += ret * offset + value
        return ret
    
    def trivial(self):
        cdef int ele
        for ele in range(1, len(self) + 1):
            if self._image(ele) != ele:
                return False
        return True
   
    cdef int cycle_size_C(self, int first):
        cdef int size, nex
        size = 1
        nex = self._image(first)
        while nex != first:
            size += 1
            nex = self._image(nex)
        return size

    cdef int* element_cycle_C(self, int first, int size, reorder = True, cache = False):
        cdef int* cycle
        cdef int cur, nex
        
        cycle = size_to_array_C(size)
        
        cur = 1
        nex = first
        for cur in range(size):
            cycle[cur] = nex
            nex = self._image(nex)
            cur += 1
        return cycle  
        
    
    def element_cycle(self, first, reorder = True, cache = False):
        cdef size = self.cycle_size_C(first)
        cdef int* cycle = self.element_cycle_C(first, size)
        ret = array_to_list_C(cycle, size)
        PyMem_Free(cycle)
        return ret
        

    def cycle_notation(self):
        ret = []
        cdef int* used = size_to_array_C(len(self))
        cdef int index, first
        
        fill_array_C(used, len(self), 0)
        
        for first in range(1, len(self)):
            if used[first - 1] == 0:
                cyc = self.element_cycle(first)
                if len(cyc) > 1:
                    ret.append(cyc)
                    for ele in cyc:
                        used[ele - 1] = 1

        PyMem_Free(used)
        return ret
    
    cpdef Permutation _fast_cycle_expo(self, int num):
        cdef int* ret
        cdef int* cyc
        cdef int ele, cyc_size, cyc_ele, cyc_index, cyc_image
        
        ret = size_to_array_C(len(self))
        fill_array_C(ret, len(self), 0)
        
        for ele in range(1, len(self) + 1):
            if ret[ele - 1] == 0:
            
                cyc_size = self.cycle_size_C(ele)
                cyc = self.element_cycle_C(ele, cyc_size)
                
                for cyc_index in range(cyc_size):
                    cyc_ele = cyc[cyc_index]
                    cyc_image = cyc[(cyc_index + num) % cyc_size]
                    ret[cyc_ele - 1] = cyc_image
                
                PyMem_Free(cyc)

        return array_to_permutation_C(ret, len(self))

    cpdef Permutation _fast_cycle_expo2(self, int num):
        cdef int* ret
        cdef int* cyc
        cdef int ele, cyc_size, cyc_ele, cyc_index, cyc_image
        
        ret = size_to_array_C(len(self))
        fill_array_C(ret, len(self), 0)
        
        for ele in range(1, len(self) + 1):
            #This needs a serious rewrite. Just find size of cycle to know off
            #set then keep ele and image that far apart during a trace.
            #If you want to use mem. Use stratch mem.
            if ret[ele - 1] == 0:
            
                cyc_size = self.cycle_size_C(ele)
                cyc = self.element_cycle_C(ele, cyc_size)
                
                for cyc_index in range(cyc_size):
                    cyc_ele = cyc[cyc_index]
                    cyc_image = cyc[(cyc_index + num) % cyc_size]
                    ret[cyc_ele - 1] = cyc_image
                
                PyMem_Free(cyc)

        return array_to_permutation_C(ret, len(self))

    
    @staticmethod
    def cycle_length_comparison(self, other):
        return NotImplemented
        num_cycles = len(self.cycle_notation())
        num_cycles_other = len(other.cycle_notation())
        if num_cycles != num_cycles_other:
            return num_cycles < num_cycles_other
        cycle_sizes = [len(cycle) for cycle in self.cycle_notation()]
        cycle_sizes_other = [len(cycle) for cycle in other.cycle_notation()]
        if cycle_sizes != cycle_sizes_other:
            return cycle_sizes > cycle_sizes_other
        return self.cycle_notation() < other.cycle_notation()    