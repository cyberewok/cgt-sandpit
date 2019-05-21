import sys
import os

DEPTH = 4


#Consider changing this to just find io tools and not add to path. This will have
#less potentially suprising behavour.
def add_sys_path(abs_path):
    sys.path.append(abs_path)

def root_path():
    abs_path = os.path.realpath(__file__)#os.getcwd()
    for _ in range(DEPTH + 1):
        abs_path = parent(abs_path)
    return abs_path
    
def parent(path):
    return os.path.join(path, os.path.pardir)

add_sys_path(root_path())
#from io_tools import *