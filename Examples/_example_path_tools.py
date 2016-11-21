def add_path_examples():
    "Path adding for access from examples folder."
    import sys
    import os
    rel_path = os.path.join("Prototype", "Python", "Playground", "Mark1")
    abs_path = os.path.join(os.getcwd(), os.path.pardir,)
    des_path = os.path.realpath(os.path.join(abs_path,rel_path))
    sys.path.append(des_path)