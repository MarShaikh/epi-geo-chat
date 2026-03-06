"""Tests for src.code_executor.validator — AST-based security validation."""

import pytest

from src.code_executor.validator import (
    CodeValidator,
    ValidationResult,
    BLOCKED_MODULES,
    BLOCKED_BUILTINS,
)


@pytest.fixture
def validator():
    return CodeValidator()


class TestValidCode:
    """Code that should pass validation."""

    def test_simple_print(self, validator):
        result = validator.validate("print('hello')")
        assert result.is_safe
        assert result.violations == []

    def test_allowed_imports(self, validator):
        code = """
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio
import geopandas
"""
        result = validator.validate(code)
        assert result.is_safe

    def test_open_read_mode(self, validator):
        code = 'data = open("/workspace/input/data.json").read()'
        result = validator.validate(code)
        assert result.is_safe

    def test_open_read_explicit_mode(self, validator):
        code = 'f = open("/workspace/input/data.json", "r")'
        result = validator.validate(code)
        assert result.is_safe

    def test_open_write_to_workspace_output(self, validator):
        code = 'f = open("/workspace/output/result.csv", "w")'
        result = validator.validate(code)
        assert result.is_safe

    def test_open_write_binary_to_workspace_output(self, validator):
        code = 'f = open("/workspace/output/plot.png", "wb")'
        result = validator.validate(code)
        assert result.is_safe

    def test_open_write_with_variable_path(self, validator):
        """Variable paths are allowed since Docker is the real security boundary."""
        code = """
output_path = "/workspace/output/result.csv"
f = open(output_path, "w")
"""
        result = validator.validate(code)
        assert result.is_safe

    def test_multiline_analysis_script(self, validator):
        code = """
import json
import numpy as np
import matplotlib.pyplot as plt

with open("/workspace/input/data.json") as f:
    data = json.load(f)

values = [item["properties"]["value"] for item in data["features"]]
plt.plot(values)
plt.savefig("/workspace/output/plot.png")
"""
        result = validator.validate(code)
        assert result.is_safe


class TestBlockedImports:
    """Code with blocked imports should be rejected."""

    @pytest.mark.parametrize("module", sorted(BLOCKED_MODULES))
    def test_blocked_direct_import(self, validator, module):
        result = validator.validate(f"import {module}")
        assert not result.is_safe
        assert any("Blocked import" in v for v in result.violations)

    @pytest.mark.parametrize("module", ["os", "subprocess", "socket", "shutil"])
    def test_blocked_from_import(self, validator, module):
        result = validator.validate(f"from {module} import something")
        assert not result.is_safe

    def test_blocked_submodule_import(self, validator):
        result = validator.validate("import os.path")
        assert not result.is_safe

    def test_blocked_from_submodule(self, validator):
        result = validator.validate("from os.path import join")
        assert not result.is_safe


class TestBlockedBuiltins:
    """Code with blocked builtin calls should be rejected."""

    @pytest.mark.parametrize("builtin", sorted(BLOCKED_BUILTINS))
    def test_blocked_builtin_call(self, validator, builtin):
        result = validator.validate(f"{builtin}('test')")
        assert not result.is_safe
        assert any("Blocked builtin" in v for v in result.violations)

    def test_exec_blocked(self, validator):
        result = validator.validate("exec('import os')")
        assert not result.is_safe

    def test_eval_blocked(self, validator):
        result = validator.validate("eval('1+1')")
        assert not result.is_safe


class TestFileWriteRestrictions:
    """Writing to paths outside /workspace/output/ should be blocked."""

    def test_write_to_root(self, validator):
        result = validator.validate('open("/etc/passwd", "w")')
        assert not result.is_safe

    def test_write_to_home(self, validator):
        result = validator.validate('open("/home/user/file.txt", "w")')
        assert not result.is_safe

    def test_write_to_tmp(self, validator):
        result = validator.validate('open("/tmp/evil.sh", "w")')
        assert not result.is_safe

    def test_append_mode_outside_workspace(self, validator):
        result = validator.validate('open("/tmp/log.txt", "a")')
        assert not result.is_safe


class TestSyntaxErrors:
    """Invalid Python should be caught."""

    def test_syntax_error(self, validator):
        result = validator.validate("def foo(")
        assert not result.is_safe
        assert any("Syntax error" in v for v in result.violations)

    def test_empty_code(self, validator):
        result = validator.validate("")
        assert result.is_safe

    def test_comment_only(self, validator):
        result = validator.validate("# just a comment")
        assert result.is_safe


class TestMultipleViolations:
    """Code with multiple violations should report all of them."""

    def test_multiple_blocked_imports(self, validator):
        code = """
import os
import subprocess
import socket
"""
        result = validator.validate(code)
        assert not result.is_safe
        assert len(result.violations) == 3

    def test_import_and_builtin_violations(self, validator):
        code = """
import os
exec("print('hi')")
"""
        result = validator.validate(code)
        assert not result.is_safe
        assert len(result.violations) == 2


class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_default_violations_empty(self):
        result = ValidationResult(is_safe=True)
        assert result.violations == []

    def test_with_violations(self):
        result = ValidationResult(is_safe=False, violations=["blocked import: os"])
        assert not result.is_safe
        assert len(result.violations) == 1
