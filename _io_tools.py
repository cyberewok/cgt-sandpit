import sys
import os

DEPTH = 0

def add_sys_path(abs_path):
    sys.path.append(abs_path)

def root_path():
    abs_path = os.path.realpath(__file__)#os.getcwd()
    for _ in range(DEPTH + 1):
        abs_path = parent(abs_path)
    return abs_path

def examples_path():
    rel_path = os.path.join("Examples", "Mark2Examples")
    return rel_path

def mark3_examples_path():
    rel_path = os.path.join("Examples", "Mark3Examples")
    return rel_path

def mark2_path():
    rel_path = os.path.join("Prototype", "Python", "Playground", "Mark2")
    return rel_path

def mark3_path():
    rel_path = os.path.join("Prototype", "Python", "Playground", "Mark3")
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

def mark2_folder():
    des_path = os.path.realpath(os.path.join(root_path(), mark2_path()))
    return des_path

def add_mark2_sys_path():
    add_sys_path(mark2_folder())
    
def mark3_folder():
    des_path = os.path.realpath(os.path.join(root_path(), mark3_path()))
    return des_path

def add_mark3_sys_path():
    add_sys_path(mark3_folder())