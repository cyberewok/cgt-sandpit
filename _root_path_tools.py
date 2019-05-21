import sys
import os

DEPTH = 0

def add_sys_path(abs_path, rel_path):
    des_path = os.path.realpath(os.path.join(abs_path, rel_path))
    sys.path.append(des_path)

def root_path():
    abs_path = os.path.realpath(__file__)#os.getcwd()
    for _ in range(DEPTH + 1):
        abs_path = parent(abs_path)
    return abs_path

def examples_path():
    rel_path = os.path.join("Examples", "Mark2Examples")
    return rel_path

def mark2_path():
    rel_path = os.path.join("Prototype", "Python", "Playground", "Mark2")
    return rel_path    

def groups_path():
    rel_path = os.path.join("Groups")
    return rel_path
    
def parent(path):
    return os.path.join(path, os.path.pardir)

def groups_folder():
    des_path = os.path.realpath(os.path.join(root_path(), groups_path()))
    return des_path

def get_group(file_name):
    des_path = os.path.realpath(os.path.join(groups_folder(), file_name))
    return des_path

def get_groups(folder_name):
    des_path = os.path.realpath(os.path.join(groups_folder(), folder_name))
    return des_path  
    