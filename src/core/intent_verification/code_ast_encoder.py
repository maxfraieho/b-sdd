"""
Code AST Semantic Encoder.
Extracts structural execution signatures (functions, calls, assertions) using standard library ast.
Compliant with ADR-002 (Pure Stdlib Core).
100% Pure Python Standard Library.
"""
import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.core.dto.intent_verification import CodeASTSignaturesDTO

logger = logging.getLogger("CodeASTEncoder")


class _ASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_signatures: List[str] = []
        self.call_chains: List[str] = []
        self.assert_statements: List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        args = [arg.arg for arg in node.args.args]
        sig = f"{node.name}({', '.join(args)})"
        self.function_signatures.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.function_signatures.append(node.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        call_repr = ""
        if isinstance(node.func, ast.Name):
            call_repr = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_repr = node.func.attr

        # Check if arguments specify skill or function name (e.g. call_skill("name"))
        args_repr = []
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                args_repr.append(arg.value)

        full_call = f"{call_repr}({', '.join(args_repr)})" if args_repr else call_repr
        if full_call:
            self.call_chains.append(full_call)

        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert):
        # Unparse test condition if available (Python 3.9+)
        try:
            cond_str = ast.unparse(node.test)
        except Exception:
            cond_str = "assert"

        msg_str = ""
        if node.msg:
            try:
                msg_str = f", {ast.unparse(node.msg)}"
            except Exception:
                pass

        self.assert_statements.append(f"{cond_str}{msg_str}")
        self.generic_visit(node)


class CodeASTEncoder:
    """Extracts semantic structural signatures from code via pure Python AST."""

    def __init__(self):
        pass

    def encode_source(self, file_path: str, source_code: str) -> CodeASTSignaturesDTO:
        """Parses Python source code string into CodeASTSignaturesDTO."""
        try:
            tree = ast.parse(source_code, filename=file_path)
            visitor = _ASTVisitor()
            visitor.visit(tree)

            has_tests = file_path.startswith("tests/") or "test" in file_path.lower()

            return CodeASTSignaturesDTO(
                changed_files=[file_path],
                function_signatures=visitor.function_signatures,
                call_chains=visitor.call_chains,
                assert_statements=visitor.assert_statements,
                has_test_coverage=has_tests
            )
        except SyntaxError as e:
            logger.warning(f"SyntaxError in {file_path}: {e}")
            return CodeASTSignaturesDTO(
                changed_files=[file_path],
                function_signatures=[],
                call_chains=[],
                assert_statements=[],
                has_test_coverage=False
            )

    def encode_files(self, file_map: Dict[str, str]) -> CodeASTSignaturesDTO:
        """Combines AST signatures across multiple changed files."""
        all_changed: List[str] = list(file_map.keys())
        all_funcs: List[str] = []
        all_calls: List[str] = []
        all_asserts: List[str] = []
        has_tests = any(f.startswith("tests/") for f in all_changed)

        for path, code in file_map.items():
            if path.endswith(".py"):
                res = self.encode_source(path, code)
                all_funcs.extend(res.function_signatures)
                all_calls.extend(res.call_chains)
                all_asserts.extend(res.assert_statements)

        # Deduplicate while preserving order
        return CodeASTSignaturesDTO(
            changed_files=all_changed,
            function_signatures=list(dict.fromkeys(all_funcs)),
            call_chains=list(dict.fromkeys(all_calls)),
            assert_statements=list(dict.fromkeys(all_asserts)),
            has_test_coverage=has_tests
        )
