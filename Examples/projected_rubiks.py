if __name__ == '__main__':
    import sys
    abs_path = "C:\\Users\\admin-u5887726\\Google Drive\\Phd\\Programming\\cgt-sandpit\\Prototype\\Python\\Playground\\Mark1"
    sys.path.append(abs_path)

from permutation import Permutation
from group import PermGroup as Group



"""2d_rubiks_example"""
def get_gens(big_rectangle, small_rectangle):
    (W, H) = big_rectangle
    (w, h) = small_rectangle
    (w, h) = (w-1, h-1)
    grid = [list(range(s, s + W)) for s in range(1, H*W+1, W)]
    gens = []
    for row in range(H-h):
        for col in range(W-w):
            gen = []
            #top row
            for index in range(col, col + w):
                gen.append(grid[row][index])
            #right col
            for index in range(row, row + h):
                gen.append(grid[index][col + w])
            #bottom row
            for index in range(col + w, col, -1):
                gen.append(grid[row+h][index])
            #left col
            for index in range(row + h, row, -1):
                gen.append(grid[index][col])
            gens.append(gen)
    return [Permutation.read_cycle_form([gen],W*H) for gen in gens]

def get_group(big_rectangle, small_rectangle):
    return Group(get_gens(big_rectangle, small_rectangle))

def num_cosets(group, big_rectangle):
    (W,H) = big_rectangle
    return fac(W*H)//group.order()

def fac(x):
    if x<2:
        return 1
    return x*fac(x-1)

for size in range(3, 4):
    g = get_group((size,size),(2,2))
    num_elements = g.order()
    print("{}: {} ({} {})".format(size, num_cosets(g, (size,size)), num_elements, fac(size*size)))
            