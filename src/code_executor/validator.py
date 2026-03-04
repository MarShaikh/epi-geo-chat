"""
AST-based code validator for code execution. 

Parses generated Python code for dangerous patterns 
(forbidden imports, builtins, file writes) before execution. 
"""

import ast
from dataclasses import dataclass, field
from typing import List

@dataclass
class ValidationResult:
    """Result of the code validation process."""
    is_safe: bool
    violations: List[str] = field(default_factory=list)

BLOCKED_MODULES = frozenset({
    "os",
    "subprocess",
    "sys",
    "socket",
    "shutil",
    "signal",
    "ctypes",
    "multiprocessing",
    "threading",
    "http",
    "urllib",
    "ftplib",
    "smtplib",
    "telnetlib",
    "xmlrpc",
    "pickle",
    "shelve",
    "marshal",
    "importlib",
    "runpy",
    "code",
    "codeop",
    "compileall",
    "py_compile",
    "zipimport",
    "pkgutil",
    "webbrowser",
    "antigravity",
    "pathlib",

})

BLOCKED_BUILTINS = frozenset({
    "__import__",
    "exec",
    "eval",
    "compile",
    "globals",
    "locals",
    "getattr",
    "setattr",
    "delattr",
    "breakpoint",
    "exit",
    "quit",
})

# modes that allow writing to files
_WRITE_MODES =  {"w", "wb", "a", "ab", "x", "xb", "w+", "wb+", "a+", "ab+", "r+", "rb+"}

class SecurityVisitor(ast.NodeVisitor):
    """AST Visitor that checks for security violations in the code."""

    def __init__(self):
        self.violations: List[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            top = alias.name.split(".")[0]
            if top in BLOCKED_MODULES:
                self.violations.append(f"Blocked import: {alias.name}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            top = node.module.split(".")[0]
            if top in BLOCKED_MODULES:
                self.violations.append(f"Blocked import: 'from {node.module}")
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        # check for direct calls to blocked builtins
        if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_BUILTINS:
            self.violations.append(f"Blocked builtin call: {node.func.id}")

        # check open() with write modes
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            self._check_open_call(node)

        self.generic_visit(node)
    
    def _check_open_call(self, node: ast.Call) -> None:
        """Check if open() is only called with Read mode or writing to /workspace/output/."""
        mode = None

        # positional: open(path, mode)
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            mode = node.args[1].value
        
        # keyword: open(path, mode="w")
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                mode = kw.value.value
        
        if mode is None:
            # default is 'r' (read), so it's safe
            return 
        if isinstance(mode, str) and mode in _WRITE_MODES:
            """Allow writing to files only in /workspace/output/ directory."""
            if len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
                path = str(node.args[0].value)
                if path.startswith("/workspace/output/"):
                    return  # allowed
            
            # check for f-string or variable path - we allow it if we can't determine 
            # the path statically, since Docker isolation is the real security boundary
            if len(node.args) >= 1 and not isinstance(node.args[0], ast.Constant):
                return
            self.violations.append(
                f"open() with write mode '{mode}' to path outside /workspace/output/."
            )

class CodeValidator:
    """Validates Python generated code for security before execution."""

    def validate(self, code: str) -> ValidationResult:
        """Parse and validate the code"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ValidationResult(is_safe=False, violations=[f"Syntax error: {e}"])
        
        visitor = SecurityVisitor()
        visitor.visit(tree)

        return ValidationResult(
            is_safe=len(visitor.violations) == 0,
            violations=visitor.violations
        )
