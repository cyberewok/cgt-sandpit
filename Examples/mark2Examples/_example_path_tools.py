import sys
import os

def add_path_examples():
    "Path adding for access from examples folder."    
    rel_path = os.path.join("Prototype", "Python", "Playground", "Mark2")
    abs_path = parent(parent(os.getcwd()))
    des_path = os.path.realpath(os.path.join(abs_path,rel_path))
    sys.path.append(des_path)
    
def parent(path):
    return os.path.join(path, os.path.pardir)

add_path_examples()