import libcst as cst
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union, Set
from dynapyt.utils.nodeLocator import get_node_by_location, get_parent_by_type, Location
import libcst.matchers as m
import libcst.metadata as meta
from .utils import remove_lines
from os.path import dirname, join

class SliceDataflow(BaseAnalysis):
    def __init__(self, source_path):
        super().__init__()
        self.source_path = source_path
        self.definitions = {}
        self.ddg = {}
        self.points_to = {}

    def write(
        self, dyn_ast: str, iid: int, old_vals: List[Callable], new_val: Any
    ) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        
        # not inside slice_me func
        if not get_parent_by_type(ast, location, m.FunctionDef(m.Name(value="slice_me"))):
            return
            
        node = get_node_by_location(ast, location)
        points_to_mutable = not isinstance(new_val, (int, float, str, bool, tuple))

        if m.matches(node, m.Assign()):
            for target in node.targets:
                if m.matches(target.target, m.Subscript() | m.Attribute()):
                    self.addEdge(target.target.value.value, location[1])
                    # consider aliases of the target, i.e, identifiers that point to the same object
                    # need to handle them in the same way as the target
                    for identifier in self.get_aliases(target.target.value.value):
                        # add data dependence edges from previous definitions to the current line
                        # update definition line numbers for the aliases
                        self.addEdge(identifier, location[1])
                    self.points_to.update({target.target.value.value: id(new_val)} if points_to_mutable else {})
                
                else:
                    for name in m.findall(target, m.Name()):
                        self.definitions[name.value] = location[1]
                        self.points_to.update({name.value: id(new_val)} if points_to_mutable else {})
                    
        elif m.matches(node, m.AugAssign()):
            if m.matches(node.target, m.Subscript() | m.Attribute()):
                self.addEdge(node.target.value.value, location[1])
                for identifier in self.get_aliases(node.target.value.value):
                    self.addEdge(identifier, location[1])
                self.points_to.update({node.target.value.value: id(new_val)} if points_to_mutable else {})
            else:
                for name in m.findall(node.target, m.Name()):
                    self.addEdge(node.target.value, location[1])
                    self.points_to.update({name.target.value: id(new_val)} if points_to_mutable else {})

    def read_identifier(self, dyn_ast: str, iid: int, val: Any) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        node = get_node_by_location(ast, location)
        # not inside slice_me func
        if not get_parent_by_type(ast, location, m.FunctionDef(m.Name(value="slice_me"))):
            return
        self.addEdge(node.value, location[1], update_definition=False)
        
    def read_attribute(self, dyn_ast: str, iid: int, base: Any, name: str, val: Any) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        location = iids.iid_to_location[iid]
        node = get_node_by_location(ast, location)
#        print(id(val))
        if not get_parent_by_type(ast, location, m.FunctionDef(m.Name(value="slice_me"))):
            return
        if not get_parent_by_type(ast, location, m.Call(func=m.Attribute(value=m.Name(value=node.value.value)))):
            return
        # must be method call
        # print(node.attr.value)
        self.addEdge(node.value.value, location[1])
        # handle aliases the same way
        for identifier in self.get_aliases(node.value.value):
            self.addEdge(identifier, location[1])
        pass

    def addEdge(self, identifier: str, to_line: int, *, update_definition: bool=True) -> None:
        if identifier in self.definitions:
            self.ddg.setdefault(to_line, set()).add(self.definitions[identifier])
        if update_definition:
            self.definitions[identifier] = to_line
            
    def get_aliases(self, identifier: str) -> List[str]:
        if identifier in self.points_to:
            return [key for key, value in self.points_to.items() if value == self.points_to[identifier] and key != identifier]
        else:
            return []
    
    def get_relevant_lines(self, start_line: int, seen: List[int]=None) -> Set[int]:
        """
        Returns a set of line numbers that start_line is either data dependent on
        by traversing the data flow graph.

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
        for line in self.ddg.get(start_line, set()):
            if not line in seen:
                # Recursively find the lines that have a data or control flow edge to start_line and add them to the set
                relevant_lines |= self.get_relevant_lines(line, seen)
        return relevant_lines
    
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
        except IndexError:
            return
            
        # Get the lines that are not relevant for the slicing criterion within the slice_me function,
        # by subtracting the set of relevant lines from the set of all lines in the function
        lines_to_remove = set(range(location[slice_me_func].start.line, location[slice_me_func].end.line+1))\
                            .difference(self.get_relevant_lines(criterion_line))

        modified_code = remove_lines(ast.code, lines_to_remove)
        
        dir = dirname(self.source_path)
        path = join(dir, "sliced.py")
        with open(path, "w") as f:
            f.write(modified_code)
