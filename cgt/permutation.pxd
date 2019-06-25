cdef array_to_permutation_C(int*, size_t)

cdef class Permutation: 
    cdef size_t _degree
    cdef int* _func
    
    cdef _lt_help(Permutation self, Permutation other)
    cdef _lteq_help(Permutation self, Permutation other)
    cdef _eq_help(Permutation self, Permutation other)
    cpdef int _image(self, int num)
    cpdef Permutation _mul_helper_perm_level(self, Permutation other)    
    cpdef Permutation _inverse(self)
    cdef int cycle_size_C(self, int first)
    cdef int* element_cycle_C(self, int first, int size, reorder = *, cache = *)
    cpdef Permutation _fast_cycle_expo(self, int num)
    cpdef Permutation _fast_cycle_expo2(self, int num)  