# DYNAPYT: DO NOT INSTRUMENT


import dynapyt.runtime as _rt

_dynapyt_ast_ = "/Users/yonatan/Documents/Uni assignments/Program Analysis/project/dynamicslicing/tests/milestone2/test_6/program.py" + ".orig"
try:
    class Person:
        def __init__(self, name):
            self.name = _rt._write_(_dynapyt_ast_, 2, _rt._read_(_dynapyt_ast_, 1, lambda: name), [lambda: self.name])
            self.lastname = _rt._write_(_dynapyt_ast_, 15, "ln", [lambda: self.lastname])
    
    def slice_me():
        p = _rt._write_(_dynapyt_ast_, 18, _rt._read_(_dynapyt_ast_, 17, lambda: Person)('Nobody'), [lambda: p])
        indefinite_pronouns = _rt._write_(_dynapyt_ast_, 19, ['Everybody', 'Somebody', 'Nobody', 'Anybody'], [lambda: indefinite_pronouns])
        indefinite_name = _rt._write_(_dynapyt_ast_, 23, _rt._read_(_dynapyt_ast_, 20, lambda: p).name in _rt._read_(_dynapyt_ast_, 22, lambda: indefinite_pronouns), [lambda: indefinite_name])
        p.name += _rt._aug_assign_(_dynapyt_ast_, 26, lambda: _rt._read_(_dynapyt_ast_, 24, lambda: p).name, 0, "first name")
        p.lastname = _rt._write_(_dynapyt_ast_, 27, "xx", [lambda: p.lastname])
        p = _rt._write_(_dynapyt_ast_, 33, _rt._read_(_dynapyt_ast_, 32, lambda: Person)('Me'), [lambda: p])
        p.lastname = _rt._write_(_dynapyt_ast_, 34, 'You', [lambda: p.lastname])
        return _rt._read_(_dynapyt_ast_, 35, lambda: p).name # slicing criterion
    
    _rt._read_(_dynapyt_ast_, 36, lambda: slice_me)()
except Exception as _dynapyt_exception_:
    _rt._catch_(_dynapyt_exception_)

