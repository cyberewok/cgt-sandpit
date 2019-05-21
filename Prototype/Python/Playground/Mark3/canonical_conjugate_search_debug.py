from _debug_tools import InstanceManager
import canonical_conjugate_search as _ccs

#_orb = ["_orbit_refine"]
#_cul = ["compare_discriminator", lambda x,y,z:0]
_ind = ["_norm_orbit_reps", lambda _,x:x]
_ref = ["_refine"]
#_mem = ["_member_refine"]

#_cls_manager_arguments = [_orb, _cul, _ind, _ref, _mem]
#_cls_options = ["orb", "cul", "ind", "ref", "mem"]
#_cls_defaults = ["orb", "cul", "ind", "ref", "mem"]
_cls_manager_arguments = [_ind, _ref]
_cls_options = ["ind", "ref"]
_cls_defaults = ["ind", "ref"]

def get_class_manager(cls):
    return InstanceManager(cls, _cls_manager_arguments, _cls_options, _cls_defaults)

_tra = ["_trace", True]
_deb = ["_debug", True]
_sta = ["_stats", True]
_pkg_manager_arguments = [_tra, _deb, _sta]
_pkg_options = ["tra", "deb", "sta"]
_pkg_defaults = ["sta"]

def get_package_manager(pkg):
    return ConjugateSearchManager(pkg, _pkg_manager_arguments, _pkg_options, _pkg_defaults)

class ConjugateSearchManager(InstanceManager):

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
    
    def disable_features(self, feat_list):
        for feat_id in feat_list:
            if feat_id not in self.options_lookup:
                raise ValueError("Unknown option: {}".format(feat_id))
            self.options_lookup[feat_id].enable()
    
    def enable_features(self, feat_list):
        for index, feat_id in enumerate(feat_list):
            if feat_id not in self.options_lookup:
                raise ValueError("Unknown option: {}".format(feat_id))
            self.options_lookup[feat_id].disable()
    
    def disable_all(self):
        self._apply_options([True] * len(self.options))
        
    def enable_all(self):
        self._apply_options([False] * len(self.options))    
    
    def perm_reorder(self, perm):
        perm = perm ** -1
        cand = lambda x: x**perm
        setattr(self.instance, "_order", cand)
    
    def perm_reorder_reset(self):
        setattr(self.instance, "_order", None)
    
    