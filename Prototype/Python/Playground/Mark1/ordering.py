def ordering_to_key(ordering):
    rev = [None] * (len(ordering) + 1)
    for index, value in enumerate(ordering): 
        rev[value] = index
    return lambda x: rev[x]
    
def ordering_to_perm_key(ordering, key = None):
    if key is None:
        key = ordering_to_key(ordering)
    return lambda perm: [key(index ** perm) for index in ordering]