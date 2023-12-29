import libcst as cst
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union, Set
from dynapyt.utils.nodeLocator import get_node_by_location, get_parent_by_type, Location
import libcst.matchers as m
import libcst.metadata as meta
from .utils import remove_lines
from os.path import dirname, join


class Slice(BaseAnalysis):
#    def __init__(self, source_path):
#        pass
    def __init__(self, source_path):
        super().__init__()
        self.source_path = source_path
#        self.source_path = "/Users/yonatan/Documents/Uni assignments/Program Analysis/dynamicslicing/tests/milestone3/test_8/program.py.orig"
        self.definitions = {}
         # data dependency graph
        self.ddg = {}
        # control dependency graph
        self.cdg = {}
        #
        self.visited_branches = []
        # stores the line numbers of the code where conditional statements are executed
        self.conditional_lines_trace = []
    
#    @property
#    def last_conditional(self): # getter method
#        return self.conditional_lines_trace[-1] if self.conditional_lines_trace else None
    
    def write(
        self, dyn_ast: str, iid: int, old_vals: List[Callable], new_val: Any
    ) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        
        # not inside slice_me func
        if not get_parent_by_type(ast, location, m.FunctionDef(m.Name(value="slice_me"))):
            return
            
        node = get_node_by_location(ast, location)

        if m.matches(node, m.Assign()):
            for target in node.targets:
                if m.matches(target.target, m.Subscript() | m.Attribute()):
                    if target.target.value.value in self.definitions:
                        self.ddg.setdefault(location[1], set()).add(self.definitions[target.target.value.value])
                    self.definitions[target.target.value.value] = location[1]
                else:
#                    print(node)
                    for name in m.findall(target, m.Name()):
                        self.definitions[name.value] = location[1]
                    
        elif m.matches(node, m.AugAssign()):
            if m.matches(node.target, m.Subscript() | m.Attribute()):
                if node.target.value.value in self.definitions:
                    self.ddg.setdefault(location[1], set()).add(self.definitions[node.target.value.value])
                self.definitions[node.target.value.value] = location[1]
            else:
                for name in m.findall(node.target, m.Name()):
                    if node.target.value in self.definitions:
                        self.ddg.setdefault(location[1], set()).add(self.definitions[node.target.value])
                    self.definitions[node.target.value] = location[1]

    def read_identifier(self, dyn_ast: str, iid: int, val: Any) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        node = get_node_by_location(ast, location)
        # not inside slice_me func
        if not get_parent_by_type(ast, location, m.FunctionDef(m.Name(value="slice_me"))):
            return
        if node.value in self.definitions:
            self.ddg.setdefault(location[1], set()).add(self.definitions[node.value])
        
    def read_attribute(self, dyn_ast: str, iid: int, base: Any, name: str, val: Any) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        node = get_node_by_location(ast, location)
        if not get_parent_by_type(ast, location, m.FunctionDef(m.Name(value="slice_me"))):
            return
        if not get_parent_by_type(ast, location, m.Call(func=m.Attribute(value=m.Name(value=node.value.value)))):
            return
        # must be method call
        # print(node.attr.value)
        if node.value.value in self.definitions:
            self.ddg.setdefault(location[1], set()).add(self.definitions[node.value.value])
        self.definitions[node.value.value] = location[1]
        pass

    # add control flow dependency edges
#    def enter_control_flow(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
#        ast, iids = self._get_ast(dyn_ast)
#        location = iids.iid_to_location[iid]
#        node = get_node_by_location(ast, location)
#
#        if location[1] not in self.conditional_lines_trace:
#            self.conditional_lines_trace.append(location[1])
            
       
    def enter_control_flow(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        if iid in self.visited_branches:
            return
            
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        node = get_node_by_location(ast, location)
        
        wrapper = cst.MetadataWrapper(ast)
        position_metadata = wrapper.resolve(meta.PositionProvider)
        simple_statement_matcher = m.SimpleStatementLine(
            metadata=m.MatchMetadataIfTrue(
                meta.PositionProvider,
                lambda position: position.start.line in range(location[1], location[3]+1),
            )
        )

        if(m.matches(node, m.If() | m.While())):
            for statement in m.findall(wrapper, simple_statement_matcher):
                self.cdg.setdefault(position_metadata[statement].start.line, set()).add(location[1])
        elif(m.matches(node, m.While())):
            pass
        elif(m.matches(node, m.For())):
            pass
            
        self.visited_branches.append(iid)

    
    
    def lines_to_keep(self, s1: int, visited: List[int]=[]) -> Set[int]:
        lines = {s1}
        # also consider dataflow edges to nodes s1 is control dependent on
#        print(self.ddg.get(s1, set()) | self.cdg.get(s1, set()))
        visited.append(s1)
        for s2 in self.ddg.get(s1, set()) | self.cdg.get(s1, set()):
            if not s2 in visited:
                lines |= self.lines_to_keep(s2)
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
            slice_me_func = m.findall(wrapper, m.FunctionDef(m.Name(value="slice_me")))[0].body
#            print(slice_me_func)
        except IndexError:
            return
#        print(location[slice_me_func])
#        print(criterion_line)
   
        print(self.ddg)
        print(self.cdg)
#        print(self.lines_to_keep(criterion_line))
        lines_to_remove = set(range(location[slice_me_func].start.line, location[slice_me_func].end.line+1))\
                            .difference(self.lines_to_keep(criterion_line))

        sliced_code = remove_lines(ast.code, lines_to_remove)
#        print(self.lines_to_keep(criterion_line))
        dir = dirname(self.source_path)
        path = join(dir, "sliced.py")

        print(ast.code)
        print("___________________________________")
        print(sliced_code)

        with open(path, "w") as f:
            f.write(sliced_code)

