"""Static analysis helpers built on the ast module (used by our config linter and codegen)."""
import ast
import operator

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul}


def _is_number(node):
    return (isinstance(node, ast.Constant) and isinstance(node.value, (int, float, complex))
            and not isinstance(node.value, bool))


class _ConstantFolder(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if _is_number(node.left) and _is_number(node.right) and type(node.op) in _OPS:
            value = _OPS[type(node.op)](node.left.value, node.right.value)
            return ast.copy_location(ast.Constant(value=value), node)
        return node


def fold_constants(source):
    """Fold +, - and * between numeric literals and return the resulting source code."""
    tree = _ConstantFolder().visit(ast.parse(source))
    return ast.unparse(ast.fix_missing_locations(tree))


class _LiteralCollector(ast.NodeVisitor):
    def __init__(self):
        self.numbers = []
        self.strings = []

    def visit_Constant(self, node):
        if _is_number(node):
            self.numbers.append(node.value)
        elif isinstance(node.value, str):
            self.strings.append(node.value)


def number_literals(source):
    """Numeric literals (int, float, complex; not bool) in source order."""
    c = _LiteralCollector()
    c.visit(ast.parse(source))
    return c.numbers


def string_literals(source):
    """String literals (not bytes) in source order."""
    c = _LiteralCollector()
    c.visit(ast.parse(source))
    return c.strings


def names_used(source):
    """Sorted set of variable names that are read (loaded) in the source."""
    names = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            names.add(node.id)
    return sorted(names)
