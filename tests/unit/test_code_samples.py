"""
Tests for code samples in the code_samples/ directory.

Each sample is validated for:
1. Valid Python syntax (AST parse)
2. Security compliance (CodeValidator)
3. Required module-level docstring
4. Correct I/O path conventions
"""

import ast
import glob
import os

import pytest

# Locate code_samples/ relative to this file (tests/unit/ -> repo root)
REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SAMPLES_DIR = os.path.join(REPO_ROOT, "code_samples")
SAMPLE_FILES = sorted(glob.glob(os.path.join(SAMPLES_DIR, "**", "*.py"), recursive=True))


# ---------------------------------------------------------------------------
# Parametrised helpers
# ---------------------------------------------------------------------------

def _rel(filepath: str) -> str:
    """Return path relative to repo root for readable test IDs."""
    return os.path.relpath(filepath, REPO_ROOT)


def _source(filepath: str) -> str:
    with open(filepath, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filepath", SAMPLE_FILES, ids=[_rel(f) for f in SAMPLE_FILES])
def test_sample_files_exist(filepath):
    """Sanity check: at least one sample file must be discovered."""
    assert os.path.isfile(filepath), f"Expected file to exist: {filepath}"


@pytest.mark.parametrize("filepath", SAMPLE_FILES, ids=[_rel(f) for f in SAMPLE_FILES])
def test_syntax_valid(filepath):
    """All sample scripts must parse as valid Python."""
    source = _source(filepath)
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in {_rel(filepath)}: {e}")


@pytest.mark.parametrize("filepath", SAMPLE_FILES, ids=[_rel(f) for f in SAMPLE_FILES])
def test_passes_security_validator(filepath):
    """All sample scripts must pass the sandbox security validator."""
    from src.code_executor.validator import CodeValidator

    source = _source(filepath)
    result = CodeValidator().validate(source)
    assert result.is_safe, (
        f"{_rel(filepath)} failed security validation:\n"
        + "\n".join(result.violations)
    )


@pytest.mark.parametrize("filepath", SAMPLE_FILES, ids=[_rel(f) for f in SAMPLE_FILES])
def test_has_module_docstring(filepath):
    """All sample scripts must have a module-level docstring (used for RAG embeddings)."""
    source = _source(filepath)
    tree = ast.parse(source)
    docstring = ast.get_docstring(tree)
    assert docstring, (
        f"{_rel(filepath)} is missing a module-level docstring. "
        "Add a triple-quoted docstring at the top describing the task, inputs, and outputs."
    )


@pytest.mark.parametrize("filepath", SAMPLE_FILES, ids=[_rel(f) for f in SAMPLE_FILES])
def test_reads_from_correct_input_path(filepath):
    """All sample scripts must read from /workspace/input/data.json."""
    source = _source(filepath)
    assert "/workspace/input/data.json" in source, (
        f"{_rel(filepath)} does not read from /workspace/input/data.json. "
        "Scripts must use the standard sandbox input path."
    )


@pytest.mark.parametrize("filepath", SAMPLE_FILES, ids=[_rel(f) for f in SAMPLE_FILES])
def test_writes_to_correct_output_path(filepath):
    """All sample scripts must write outputs to /workspace/output/."""
    source = _source(filepath)
    assert "/workspace/output/" in source, (
        f"{_rel(filepath)} does not write to /workspace/output/. "
        "All outputs must be saved under /workspace/output/."
    )


@pytest.mark.parametrize("filepath", SAMPLE_FILES, ids=[_rel(f) for f in SAMPLE_FILES])
def test_uses_get_raster_asset_helper(filepath):
    """All sample scripts must define and use the get_raster_asset() helper."""
    source = _source(filepath)
    assert "def get_raster_asset" in source, (
        f"{_rel(filepath)} does not define get_raster_asset(). "
        "Use the standard helper to find raster assets dynamically."
    )
    assert "get_raster_asset(" in source.replace("def get_raster_asset(", ""), (
        f"{_rel(filepath)} defines get_raster_asset() but never calls it."
    )


def test_at_least_one_sample_per_category():
    """Ensure each expected task category has at least one sample."""
    categories = {"time_series", "spatial_maps", "statistics", "comparisons"}
    found = set()
    for fp in SAMPLE_FILES:
        rel = os.path.relpath(fp, SAMPLES_DIR)
        category = rel.split(os.sep)[0]
        found.add(category)
    missing = categories - found
    assert not missing, f"Missing code samples for categories: {missing}"
