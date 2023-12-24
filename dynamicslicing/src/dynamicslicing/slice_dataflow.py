import libcst as cst
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union, Set
from dynapyt.utils.nodeLocator import get_node_by_location, get_parent_by_type, Location
import libcst.matchers as m
import libcst.metadata as meta
from .utils import remove_lines

class SliceDataflow(BaseAnalysis):
#    def __init__(self, source_path):
#        with open(source_path, "r") as file:
#            source = file.read()
##        iid_object = IIDs(source_path)
#        ast, iids = self._get_ast(dyn_ast)
#        self.defs = {}
#        self.graph = {}

    def __init__(self):
        super().__init__()
        self.source_path = "/Users/yonatan/Documents/Uni assignments/Program Analysis/project/dynamicslicing/tests/milestone2/test_6/program.py.orig"
        self.definitions = {}
        self.graph = {}
       
#        ast, iids = self._get_ast(dyn_ast)

    def write(
        self, dyn_ast: str, iid: int, old_vals: List[Callable], new_val: Any
    ) -> Any:
        ast, iids = self._get_ast(dyn_ast)
#        print(dyn_ast)

        location = iids.iid_to_location[iid]
        if not get_parent_by_type(ast, location, m.FunctionDef(m.Name(value="slice_me"))):
            print("parent is not func def")
            return
        node = get_node_by_location(ast, location)

#        print(ast)
        if m.matches(node, m.Assign()):
            for target in node.targets:
                if m.matches(target.target, m.Subscript()):
                    if target.target.value.value in self.definitions:
                        self.graph.setdefault(location[1], set()).add(self.definitions[target.target.value.value])
                    self.definitions[target.target.value.value] = location[1]
#                elif object property:
#                    pass
                else:
                    for name in m.findall(target, m.Name()):
                        self.definitions[name.value] = location[1]
                    
        elif m.matches(node, m.AugAssign()):
            if m.matches(node.target, m.Subscript()):
                if node.target.value.value in self.definitions:
                    self.graph.setdefault(location[1], set()).add(self.definitions[node.target.value.value])
                self.definitions[node.target.value.value] = location[1]
#            elif object property:
#                pass
            else:
                for name in m.findall(node.target, m.Name()):
                    if node.target.value in self.definitions:
                        self.graph.setdefault(location[1], set()).add(self.definitions[node.target.value])
                    self.definitions[node.target.value] = location[1]

    def read(self, dyn_ast: str, iid: int, val: Any) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        node = get_node_by_location(ast, location)
        
        if not get_parent_by_type(ast, location, m.FunctionDef(m.Name(value="slice_me"))):
            print("parent is not func def")
            return

#        get_parent_by_type(comment_node, location, m.Fu)
#        print(node.value)
        # add edge to graph
        if node.value in self.definitions:
            self.graph.setdefault(location[1], set()).add(self.definitions[node.value])

        
    def read_subscript(
        self,
        dyn_ast: str,
        iid: int,
        base: Any,
        sl: List[Union[int, Tuple]],
        val: Any
    ) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        node = get_node_by_location(ast, location)
        

        
    def read_attribute(self, dyn_ast: str, iid: int, base: Any, name: str, val: Any) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        node = get_node_by_location(ast, location)
#        print(iid, base, name, val, node)
        pass


    def lines_to_keep(self, s1: int) -> Set[int]:
        lines = {s1}
        if s1 in self.graph:
            for s2 in self.graph[s1]:
                lines = lines.union(self.lines_to_keep(s2))
        return lines

    
    def end_execution(self):
        ast, iids = self._get_ast(self.source_path)
        wrapper = cst.MetadataWrapper(ast)
        
        try:
            comment_node = m.findall(wrapper, m.Comment(value="# slicing criterion"))[0]
            location = wrapper.resolve(meta.PositionProvider)
            criterion_line = location[comment_node].start.line
        except IndexError:
            print("slicing criterion not specified")
            return
            
        try:
            slice_me_func = m.findall(wrapper, m.FunctionDef(m.Name(value="slice_me")))[0]
        except IndexError:
            return
            
#        print(location[slice_me_func])
 
        lines_to_remove = set(range(location[slice_me_func].start.line, location[slice_me_func].end.line+1))\
                            .difference(self.lines_to_keep(criterion_line))

#        print(self.location_to_iid(self.source_path, Location(self.source_path, location.start.line, location.start.column, location.end.line, location.end.column)))
#        print(criterion_line)
        print(remove_lines(ast.code, lines_to_remove))
#        print(self.graph, self.lines_to_keep(criterion_line))

