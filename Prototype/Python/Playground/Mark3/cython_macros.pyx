from cpython.mem cimport PyMem_Malloc, PyMem_Free, PyMem_Realloc

cdef void fill_array_C(int* nums, size_t size, int fill):
    cdef int index
    for index in range(size):
        nums[index] = fill

cdef int* size_to_array_C(int size):
    ret = <int*> PyMem_Malloc(size * sizeof(int))
    
    if ret is NULL:
        raise MemoryError()
    
    return ret
    
#cdef int** size_to_ptr_array_C(int size):
    #ret = <int**> PyMem_Malloc(size * sizeof(int*))
    
    #if ret is NULL:
        #raise MemoryError()

    #return ret

cdef int* list_to_array_C(object nums):
    cdef int* ret = size_to_array_C(len(nums))
    cdef int index    
    
    for index in range(len(nums)):
        ret[index] = nums[index]
    return ret

cdef array_to_list_C(int* nums, size_t size):
    #Should this free the nums memory?
    ret = [None] * size
    cdef int index
    for index in range(size):
        ret[index] = nums[index]
    return ret

cdef class Integer_Array:
    #cdef int _size_limit
    #cdef int _cur_size
    #cdef int* _items
    
    def __cinit__(self, int size = 0, int capacity = 10):
        if capacity < size:
            capacity = size
            
        self._size_limit = capacity
        self._cur_size = size
        self._items = size_to_array_C(self._size_limit)
        
    def __dealloc__(self):
        PyMem_Free(self._items)
    
    cdef void double_size(self):
        self._size_limit *= 2
        self._items = <int*> PyMem_Realloc(self._items, self._size_limit * sizeof(int))    
    
    cdef void append(self, int item):
        if self._cur_size >= self.size_limit:
            self.double_size()
        self._items[self._cur_size] = item
        self._cur_size += 1
    
    def __len__(self):
        return self._cur_size
    
    def __getitem__(self, int index):
        return self.items[index]
    
    def __setitem__(self, int index, int item):
        self.items[index] = item

#cdef class Array_2D_C:
    #cdef int _size_limit
    #cdef int _cur_size
    #cdef int** _items
    
    #def __cinit__(self, int capacity = 10):
        #self._size_limit = capacity
        #self._cur_size = 0
        #self._items = size_to_ptr_array_C(self._size_limit)
        
    #def __dealloc__(self):
        #cdef int index
        #for index in range(self._cur_size):
            #PyMem_Free(self._items[index])
        #PyMem_Free(self._items)
    
    #cdef double(self):
        #self._size_limit *= 2
        #self._items = <int**> PyMem_Realloc(self._items, self._size_limit * sizeof(int*))    
    
    #cdef append(self, int* item):
        #if self._cur_size >= self.size_limit:
            #self.double()
        #self._items[self._cur_size] = item
        #self._cur_size += 1
    
    #def __len__(self):
        #return self._cur_size
    
    #def __getitem__(self, index):
        #return self.items[index]
