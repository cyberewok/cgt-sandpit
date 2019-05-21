cdef void fill_array_C(int*, size_t, int)

cdef int* size_to_array_C(int)

cdef int* list_to_array_C(object)

cdef object array_to_list_C(int*, size_t)

cdef class Integer_Array:
    cdef int _size_limit
    cdef int _cur_size
    cdef int* _items
    
    cdef void double_size(self)
    cdef void append(self, int item)