from typing import List
import libcst as cst
from libcst._flatten_sentinel import FlattenSentinel
from libcst._nodes.statement import BaseStatement, If, SimpleStatementLine, EmptyLine
from libcst._removal_sentinel import RemovalSentinel
from libcst.metadata import (
    ParentNodeProvider,
    PositionProvider,
)
import libcst.matchers as m


class OddIfNegation(m.MatcherDecoratableTransformer):
    """
    Negate the test of every if statement on an odd line.
    """
    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        PositionProvider,
    )

    def leave_If(self, original_node: If, updated_node: If) -> BaseStatement | FlattenSentinel[BaseStatement] | RemovalSentinel:
        location = self.get_metadata(PositionProvider, original_node)
        if location.start.line % 2 == 0:
            return updated_node
        negated_test = cst.UnaryOperation(
            operator=cst.Not(),
            expression=updated_node.test,
        )
        return updated_node.with_changes(
            test=negated_test,
        )

        
class StatementRemover(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (
        PositionProvider,
    )
    def __init__(self, lines_to_remove: List[int]):
#        super().__init__()
        self.lines_to_remove = lines_to_remove

    def on_leave(self, original_node: cst.CSTNode, updated_node: cst.CSTNode) -> cst.CSTNode | RemovalSentinel | FlattenSentinel[BaseStatement]:
        location = self.get_metadata(PositionProvider, original_node)
        if isinstance(updated_node, EmptyLine | SimpleStatementLine | cst.If | cst.For | cst.While):
            if location.start.line in self.lines_to_remove:
                return RemovalSentinel.REMOVE
        return updated_node
        

def negate_odd_ifs(code: str) -> str:
    syntax_tree = cst.parse_module(code)
    wrapper = cst.metadata.MetadataWrapper(syntax_tree)
    code_modifier = OddIfNegation()
    new_syntax_tree = wrapper.visit(code_modifier)
    return new_syntax_tree.code

def remove_lines(code: str, lines_to_remove: List[int]) -> str:
    syntax_tree = cst.parse_module(code)
    wrapper = cst.metadata.MetadataWrapper(syntax_tree)
    code_modifier = StatementRemover(lines_to_remove)
    new_syntax_tree = wrapper.visit(code_modifier)
    return new_syntax_tree.code
    
