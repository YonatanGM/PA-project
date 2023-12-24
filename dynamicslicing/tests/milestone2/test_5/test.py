# DYNAPYT: DO NOT INSTRUMENT


import dynapyt.runtime as _rt

_dynapyt_ast_ = "/Users/yonatan/Documents/Uni assignments/Program Analysis/project/dynamicslicing/tests/milestone2/test_5/test.py" + ".orig"
try:
    x = _rt._write_(_dynapyt_ast_, 0, 10, [lambda: x])
    t = y = _rt._write_(_dynapyt_ast_, 2, _rt._read_(_dynapyt_ast_, 1, lambda: x), [lambda: t, lambda: y])
    a, b = _rt._write_(_dynapyt_ast_, 3, (5, 2), [lambda: (a, b)])
    c = _rt._write_(_dynapyt_ast_, 6, _rt._read_(_dynapyt_ast_, 4, lambda: a) + _rt._read_(_dynapyt_ast_, 5, lambda: b), [lambda: c])
    d = _rt._write_(_dynapyt_ast_, 8, _rt._read_(_dynapyt_ast_, 7, lambda: c) * 2, [lambda: d])
    e = _rt._write_(_dynapyt_ast_, 10, _rt._read_(_dynapyt_ast_, 9, lambda: d) - 3, [lambda: e])
    total = _rt._write_(_dynapyt_ast_, 11, 0, [lambda: total])
    total += _rt._aug_assign_(_dynapyt_ast_, 13, lambda: total, 0, _rt._read_(_dynapyt_ast_, 12, lambda: a))
    total += _rt._aug_assign_(_dynapyt_ast_, 15, lambda: total, 0, _rt._read_(_dynapyt_ast_, 14, lambda: d)) # slicing criterion
    x = _rt._write_(_dynapyt_ast_, 16, [1, 2, 3, 4], [lambda: x])
    y = _rt._write_(_dynapyt_ast_, 19, _rt._sub_(_dynapyt_ast_, 18, _rt._read_(_dynapyt_ast_, 17, lambda: x), [slice(None, None, None)]), [lambda: y])
    y[0] += _rt._aug_assign_(_dynapyt_ast_, 22, lambda: _rt._sub_(_dynapyt_ast_, 21, _rt._read_(_dynapyt_ast_, 20, lambda: y), [0]), 0, 5)
    y[1] = _rt._write_(_dynapyt_ast_, 25, _rt._sub_(_dynapyt_ast_, 24, _rt._read_(_dynapyt_ast_, 23, lambda: x), [2]), [lambda: y[1]])
    my_dictionary = _rt._write_(_dynapyt_ast_, 26, {"name": "John Doe", "age": 30, "occupation": "Software Engineer"}, [lambda: my_dictionary])
    name = _rt._write_(_dynapyt_ast_, 29, _rt._sub_(_dynapyt_ast_, 28, _rt._read_(_dynapyt_ast_, 27, lambda: my_dictionary), ["name"]), [lambda: name])
    (f, g) = _rt._write_(_dynapyt_ast_, 32, (_rt._read_(_dynapyt_ast_, 30, lambda: c), _rt._read_(_dynapyt_ast_, 31, lambda: d)), [lambda: (f, g)])
    (g) = _rt._write_(_dynapyt_ast_, 34, _rt._read_(_dynapyt_ast_, 33, lambda: e), [lambda: (g)])
    [h, i] = _rt._write_(_dynapyt_ast_, 39, (_rt._sub_(_dynapyt_ast_, 36, _rt._read_(_dynapyt_ast_, 35, lambda: y), [1]), _rt._sub_(_dynapyt_ast_, 38, _rt._read_(_dynapyt_ast_, 37, lambda: y), [3])), [lambda: [h, i]])
except Exception as _dynapyt_exception_:
    _rt._catch_(_dynapyt_exception_)

