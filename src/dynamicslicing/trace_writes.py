import libcst as cst
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from typing import Any, Callable, List

# Implement a DynaPyt analysis to trace all writes by printing them to stdout.
class TraceWrites(BaseAnalysis):
    def write(
        self, dyn_ast: str, iid: int, old_vals: List[Callable], new_val: Any
    ) -> Any:
        print(new_val)
