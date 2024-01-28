# DYNAPYT: DO NOT INSTRUMENT


import dynapyt.runtime as _rt

_dynapyt_ast_ = "/Users/yonatan/Documents/Uni assignments/Program Analysis/dynamicslicing/tests/milestone3/test_5/program.py" + ".orig"
try:
    def slice_me():
        ages = _rt._write_(_dynapyt_ast_, 1, [0, 25, 50, 75, 100, 150], [lambda: ages])
        current_age = _rt._write_(_dynapyt_ast_, 3, _rt._read_(_dynapyt_ast_, 2, lambda: ages)[0], [lambda: current_age])
        while _rt._enter_while_(_dynapyt_ast_, 7, _rt._read_(_dynapyt_ast_, 4, lambda: current_age) < _rt._read_(_dynapyt_ast_, 5, lambda: ages)[-1]):
            current_age += _rt._aug_assign_(_dynapyt_ast_, 6, lambda: current_age, 0, 1)
        else:
            _rt._exit_while_(_dynapyt_ast_, 7)
        if _rt._enter_if_(_dynapyt_ast_, 12, _rt._read_(_dynapyt_ast_, 8, lambda: current_age) == _rt._read_(_dynapyt_ast_, 9, lambda: ages)[-1]):
            ages[-1] += _rt._aug_assign_(_dynapyt_ast_, 11, lambda: _rt._read_(_dynapyt_ast_, 10, lambda: ages)[-1], 0, 50)
            _rt._exit_if_(_dynapyt_ast_, 12)
        else:
            print("something went wrong")        
            _rt._exit_if_(_dynapyt_ast_, 12)
        return _rt._read_(_dynapyt_ast_, 13, lambda: ages) # slicing criterion
    
    _rt._read_(_dynapyt_ast_, 14, lambda: slice_me)()
except Exception as _dynapyt_exception_:
    _rt._catch_(_dynapyt_exception_)
