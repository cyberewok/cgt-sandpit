from group import PermGroup as Group
from permutation import Permutation
import os

#File syntax -> name of method to process.
TAG_RECOG = {
    "Degree:" : "process_degree",
    "Order:" : "process_order",
    "Generators:" : "process_gens",
    "Symmetric normaliser order:" : "process_sym_norm_order",
    "Symmetric normaliser generators:" : "process_sym_norm_gens",
    "" : "process_EOF"
}

def read_group_file(file_name):
    input_file = open(file_name, 'r')
    gfr = GroupFileReader(input_file)
    info = gfr.read_all()
    input_file.close()
    return info.get_group()
    
def read_symmetric_normaliser_file(file_name):
    input_file = open(file_name, 'r')
    gfr = GroupFileReader(input_file)
    info = gfr.read_all()
    input_file.close()
    return info.get_group(), info.get_symmetric_normaliser()    

def read_group_folder(folder_name):
    folder = os.fsencode(folder_name)
    for file in os.listdir(folder):
        file_name = os.fsdecode(file)
        full_file_name = os.path.join(folder_name, file_name)
        yield(read_group_file(full_file_name))

def read_symmetric_normaliser_folder(folder_name):
    folder = os.fsencode(folder_name)
    for file in os.listdir(folder):
        file_name = os.fsdecode(file)
        full_file_name = os.path.join(folder_name, file_name)
        yield(read_symmetric_normaliser_file(full_file_name))



class GroupInformation():
    def __init__(self):
        self.degree = None
        self.gens = None
        self.order = None
        self.sym_norm_gens = None
        self.sym_norm_order = None
        self.norm = None
        self.parent = None
    
    def _make_group(self, gens, order = None):    
        if order is not None:
            ret = Group.fixed_order_group(gens, order)
        else:
            ret = Group(gens)
        return ret
    
    def get_group(self):
        return self._make_group(self.gens, self.order)
    
    def get_symmetric_normaliser(self):
        return self._make_group(self.sym_norm_gens, self.sym_norm_order)

class GroupFileReader():
    def __init__(self, input_file, info = None):
        self.file = input_file
        if info is None:
            info = GroupInformation()
        self.info = info
    
    def read_all(self):
        tag = self.consume_tag()
        while tag is not None:
            self.process_tag(tag)
            tag = self.consume_tag()
        return self.info
    
    def consume_line(self):
        return self.file.readline().strip()
    
    def consume_num(self):
        return int(self.consume_line())    
    
    def consume_tag(self):
        tag = self.consume_line()
        if len(tag) <= 1:
            return None
        return tag
    
    def process_tag(self, tag):
        process_func = getattr(self, TAG_RECOG[tag])
        process_func()
    
    def process_degree(self):
        self.degree = self.consume_num()
        self.info.degree = self.degree

    def process_order(self):
        self.info.order = self.consume_num()
    
    def process_gens(self):
        self.info.gens = self.consume_permutation_list()
    
    def process_sym_norm_order(self):
        self.info.sym_norm_order = self.consume_num()

    def process_sym_norm_gens(self):
        self.info.sym_norm_gens = self.consume_permutation_list()
    
    def process_EOF(self):
        pass
    
    def consume_permutation_list(self):
        line = [self.consume_line()]
        while line[-1][-1] != ']':
            line.append(self.consume_line())
        line = " ".join(line)
        ret = []
        cur_pos = 0
        cur_pos = line.find('(', cur_pos)
        while cur_pos > 0:
            perm, cur_pos = self.get_permutation(line, cur_pos)
            ret.append(perm)
            cur_pos = line.find('(', cur_pos)
        return ret
            
    def get_permutation(self, line, cur_pos):
        ret = []
        while line[cur_pos] == '(':
            cycle, cur_pos = self.get_cycle(line, cur_pos)
            ret.append(cycle)
            cur_pos = self.eat_white_space(line, cur_pos)
        ret = Permutation.read_cycle_form(ret, self.degree)
        return ret, cur_pos
    
    def eat_white_space(self, line, cur_pos):
        small = '!'
        large = '~'
        while cur_pos < len(line) and (line[cur_pos] < small or line[cur_pos] > large):
            cur_pos += 1
        return cur_pos
    
    def get_cycle(self, line, cur_pos):
        end = line.index(')', cur_pos)
        cycle = [int(val) for val in line[cur_pos+1:end].strip().split(',')]
        return cycle, end+1