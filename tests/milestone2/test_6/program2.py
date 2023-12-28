# DYNAPYT: DO NOT INSTRUMENT


import dynapyt.runtime as _rt

_dynapyt_ast_ = "/Users/yonatan/Documents/Uni assignments/Program Analysis/project/dynamicslicing/tests/milestone2/test_6/program2.py" + ".orig"
try:
    class Person:
        def __init__(self, name):
            self.name = _rt._write_(_dynapyt_ast_, 2, _rt._read_(_dynapyt_ast_, 1, lambda: name), [lambda: self.name])

        def get_name(self):
            return _rt._attr_(_dynapyt_ast_, 28, _rt._read_(_dynapyt_ast_, 4, lambda: self), "name")

        def get_name_uppercase(self):
            return _rt._attr_(_dynapyt_ast_, 30, _rt._attr_(_dynapyt_ast_, 29, _rt._read_(_dynapyt_ast_, 6, lambda: self), "name"), "upper")()

        def get_greeting(self):
            return f"Hello, my name is {_rt._attr_(_dynapyt_ast_, 31, _rt._read_(_dynapyt_ast_, 8, lambda: self), 'name')}!"
        # Modify the name directly
        def set_name(self, new_name):
            self.name = _rt._write_(_dynapyt_ast_, 11, _rt._read_(_dynapyt_ast_, 10, lambda: new_name), [lambda: self.name])
            
    def dummy_function(name):
        return len(_rt._read_(_dynapyt_ast_, 13, lambda: name)) * 2
        
    def slice_me():
        p = _rt._write_(_dynapyt_ast_, 16, _rt._read_(_dynapyt_ast_, 15, lambda: Person)("Nobody"), [lambda: p])
        indefinite_pronouns = _rt._write_(_dynapyt_ast_, 17, ["Everybody", "Somebody", "Anybody"], [lambda: indefinite_pronouns])
        # Call the dummy function and assign the result to a variable
        dummy_result = _rt._write_(_dynapyt_ast_, 20, _rt._read_(_dynapyt_ast_, 18, lambda: dummy_function)(_rt._attr_(_dynapyt_ast_, 32, _rt._read_(_dynapyt_ast_, 19, lambda: p), "name")), [lambda: dummy_result])
        _rt._attr_(_dynapyt_ast_, 33, _rt._read_(_dynapyt_ast_, 21, lambda: indefinite_pronouns), "append")(_rt._read_(_dynapyt_ast_, 22, lambda: dummy_result))
        print(_rt._attr_(_dynapyt_ast_, 34, _rt._read_(_dynapyt_ast_, 23, lambda: p), "get_greeting")())
        # Modify the name using the setter method
        _rt._attr_(_dynapyt_ast_, 35, _rt._read_(_dynapyt_ast_, 24, lambda: p), "set_name")("John Doe")
        print(_rt._attr_(_dynapyt_ast_, 36, _rt._read_(_dynapyt_ast_, 25, lambda: p), "get_greeting")())
        return _rt._attr_(_dynapyt_ast_, 37, _rt._read_(_dynapyt_ast_, 26, lambda: p), "name") # slicing criterion
        
    _rt._read_(_dynapyt_ast_, 27, lambda: slice_me)()
except Exception as _dynapyt_exception_:
    _rt._catch_(_dynapyt_exception_)


