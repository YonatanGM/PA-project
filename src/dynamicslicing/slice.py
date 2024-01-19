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
        
    def get_relevant_lines(self, start_line: int, seen: List[int]=None) -> Set[int]:
        """
        Returns a set of line numbers that start_line is either data or control dependent on
        by traversing the data and control flow graphs.

        Parameters:
        start_line (int): The line number to start the slicing from.
        seen (List[int], optional): A list of line numbers that have been seen. Defaults to None.

        Returns:
        Set[int]: A set of line numbers that are relevant for the slicing criterion.
        """
        if seen is None:
            seen = []
        relevant_lines = {start_line}
        # Mark start_line as seen
        seen.append(start_line)
        # Loop through the lines that have a data or control flow edge to start_line
        for line in self.ddg.get(start_line, set()) | self.cdg.get(start_line, set()):
            if not line in seen:
            # Recursively find the lines that have a data or control flow edge to start_line and add them to the set
                relevant_lines |= self.get_relevant_lines(line, seen)
        return relevant_lines
        
    def end_execution(self):
        ast, iids = self._get_ast(self.source_path)
        wrapper = cst.MetadataWrapper(ast)
        
        try:
            comment_node = m.findall(wrapper, m.Comment(value="# slicing criterion"))[0]
            location_metadata = wrapper.resolve(meta.PositionProvider)
            criterion_line = location_metadata[comment_node].start.line
        except IndexError:
            print("slicing criterion not specified")
            return
            
        try:
            slice_me_func = m.findall(wrapper, m.FunctionDef(m.Name(value="slice_me")))[0].body
        except IndexError:
            return
        
        # Get the lines that are not relevant for the slicing criterion within the slice_me function,
        # by subtracting the set of relevant lines from the set of all lines in the function
        lines_to_remove = set(range(location_metadata[slice_me_func].start.line, location_metadata[slice_me_func].end.line+1))\
                            .difference(self.get_relevant_lines(criterion_line))
                            
        # write the sliced program
        sliced_code = remove_lines(ast.code, lines_to_remove)
        path = join(dirname(self.source_path), "sliced.py")
        with open(path, "w") as f:
#            f.write("a='{}{}{}'".format(self.get_relevant_lines(criterion_line), self.cdg, self.ddg))
            f.write(sliced_code)

