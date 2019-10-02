class CallReporter():
    def __init__(self, func_name, cls, attr_name):
        self.original = getattr(cls, func_name)
        self.history = []
        self.current = []
        setattr(cls, func_name, self.add_report(self.original))
        self.attr_name
        self.cls = cls
        self.func_name = func_name
    
    def get_history(self):
        return self.history      
    
    def reset(self, val = None):
        if val is None:
            val = []
        self.history.append(self.current)
        self.current = val
      
    def add_report(self, func):
        def new_func(inst_self, *args, **keywrds):
            self.current.append(getattr(inst_self, self.attr_name))
            ret =  func(inst_self, *args, **keywrds)
            return ret
        return new_func
    
    def close(self):
        self.reset()
        setattr(self.cls, self.func_name, self.original)        
        
    def __enter__(self):
        pass
    
    def __exit__(self, *args):
        self.close()
        
    def __del__(self, *args):
        self.close()


class CallResultCounter():
    def __init__(self, func_name, cls, res):
        self.original = getattr(cls, func_name)
        self.history = []
        self.current = 0
        setattr(cls, func_name, self.add_result_counter(self.original))
        self.cls = cls
        self.func_name = func_name
        self.res = res
    

    def get_history(self):
        return self.history    
    
    def reset(self, val = 0):
        self.history.append(self.current)
        self.current = val
      
    def add_result_counter(self, func):
        def new_func(*args, **keywrds):
            ret = func(*args, **keywrds)
            if self.res is ret:
                self.current += 1            
            return ret
        return new_func
    
    def close(self):
        self.reset()
        setattr(self.cls, self.func_name, self.original)        
        
    def __enter__(self):
        pass
    
    def __exit__(self, *args):
        self.close()
        
    def __del__(self, *args):
        self.close()

class CallCounter():
    def __init__(self, func_name, cls):
        self.original = getattr(cls, func_name)
        self.count_history = []
        self.count = 0
        setattr(cls, func_name, self.add_counter(self.original))
        self.cls = cls
        self.func_name = func_name
    
    def reset(self, val = 0):
        self.count_history.append(self.count)
        self.count = val
      
    def add_counter(self, func):
        def new_func(*args, **keywrds):
            self.count += 1
            return func(*args, **keywrds)
        return new_func
    
    def close(self):
        self.reset()
        setattr(self.cls, self.func_name, self.original)
    
    def get_history(self):
        return self.count_history
        
    def __enter__(self):
        pass
    
    def __exit__(self, *args):
        self.close()
        
    def __del__(self, *args):
        self.close()
        
class CallResultCollector():
    def __init__(self, func_name, cls):
        self.original = getattr(cls, func_name)
        self.history = []
        self.current = dict()
        setattr(cls, func_name, self.add_result_counter(self.original))
        self.cls = cls
        self.func_name = func_name
    
    def reset(self, val = None):
        if val is None:
            val = dict()
        self.history.append(self.current)
        self.current = val
      
    def add_result_counter(self, func):
        def new_func(*args, **keywrds):
            ret = func(*args, **keywrds)
            if ret in self.current:
                self.current[ret] += 1
            else:
                self.current[ret] = 1
            return ret
        return new_func
    
    def close(self):
        self.reset()
        setattr(self.cls, self.func_name, self.original)        
        
    def __enter__(self):
        pass
    
    def __exit__(self, *args):
        self.close()
        
    def __del__(self, *args):
        self.close()       
        
class AttributeManager():
    def __init__(self, instance, attr_id, replacement = None):
        if replacement is None:
            replacement = lambda *arg, **kw:None

        self.instance = instance
        self.attr_id = attr_id
        self.replace = replacement
        self.original = getattr(self.instance, self.attr_id)
        
    def enable(self, *args):
        setattr(self.instance, self.attr_id, self.original)   
        
    def disable(self, *args):
        val = self.replace
        if len(args) > 0:
            val = val(*args)
        setattr(self.instance, self.attr_id, val)
        
class InstanceManager():
    def __init__(self, instance, manager_arguments, options, default_options = None):
        if default_options is None:
            default_options = list(options)
        
        self.instance = instance
        self.managers = [AttributeManager(*([instance] + args)) for args in manager_arguments]
        self.options = options
        self.options_lookup = {op:man for op,man in zip(self.options, self.managers)}        
        self.default_options = default_options
        
    def change_default(self, new_default):
        for feat_id in new_default:
            if feat_id not in self.options_lookup:
                raise ValueError("Unknown option: {}".format(feat_id))
        self.default_options = new_default
    
    def apply_default(self):
        self.disable_all()
        self.enable_features(self.default_options)
    
    def disable_all(self):
        self._apply_options([False] * len(self.options))
        
    def enable_all(self):
        self._apply_options([True] * len(self.options))
    
    def disable_features(self, feat_list):
        for feat_id in feat_list:
            if feat_id not in self.options_lookup:
                raise ValueError("Unknown option: {}".format(feat_id))
            self.options_lookup[feat_id].disable()
    
    def enable_features(self, feat_list, args = None):
        for index, feat_id in enumerate(feat_list):
            if feat_id not in self.options_lookup:
                raise ValueError("Unknown option: {}".format(feat_id))
            if args is not None:
                arg = args[index]
                if arg is not None:
                    self.options_lookup[feat_id].enable(arg)                    
                    continue
            self.options_lookup[feat_id].enable()
    
    def _apply_options(self, vec):
        for manager, enable in zip(self.managers, vec):
            if enable:
                manager.enable()
            else:
                manager.disable()