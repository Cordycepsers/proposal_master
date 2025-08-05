"""
Python Code Analyzer Tool for the Automated RFP System.
Provides comprehensive code analysis including security, style, and performance checks.
"""
import ast
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging

try:
    import pylint.lint
    import pylint.reporters.text
    from pylint.lint import Run as PylintRun
    PYLINT_AVAILABLE = True
except ImportError:
    PYLINT_AVAILABLE = False

try:
    import bandit
    from bandit.core import manager
    BANDIT_AVAILABLE = True
except ImportError:
    BANDIT_AVAILABLE = False

try:
    import flake8.api.legacy as flake8
    FLAKE8_AVAILABLE = True
except ImportError:
    FLAKE8_AVAILABLE = False

from ..utils.tools import Tool

logger = logging.getLogger(__name__)


class PythonCodeAnalyzer(Tool):
    """Analyze Python code for quality, security, and style issues."""
    
    name = "python_code_analyzer"
    description = "Analyze Python code for quality, security, and style issues using AST, pylint, bandit, and flake8"
    parameters = {
        "file_path": {
            "type": "string", 
            "description": "Path to Python file or directory",
            "required": True
        },
        "check_type": {
            "type": "string", 
            "description": "Type of check (security/style/performance/all)",
            "required": False,
            "default": "all"
        },
        "include_ast": {
            "type": "boolean",
            "description": "Include AST-based structural analysis",
            "required": False,
            "default": True
        },
        "severity_threshold": {
            "type": "string",
            "description": "Minimum severity level to report (low/medium/high)",
            "required": False,
            "default": "medium"
        }
    }

    def execute(self, file_path: str, check_type: str = "all", 
                include_ast: bool = True, severity_threshold: str = "medium") -> Dict[str, Any]:
        """Execute code analysis."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {"error": f"File or directory not found: {file_path}"}
            
            results = {
                "file_path": str(file_path),
                "check_type": check_type,
                "severity_threshold": severity_threshold,
                "issues": [],
                "metrics": {},
                "summary": {
                    "total_issues": 0,
                    "by_severity": {"high": 0, "medium": 0, "low": 0},
                    "by_category": {}
                }
            }
            
            # Collect Python files to analyze
            python_files = self._get_python_files(file_path)
            if not python_files:
                return {"error": "No Python files found to analyze"}
            
            # Run different types of analysis
            for py_file in python_files:
                file_results = {"file": str(py_file), "issues": []}
                
                # AST-based structural analysis
                if include_ast:
                    ast_issues = self._analyze_with_ast(py_file, check_type)
                    file_results["issues"].extend(ast_issues)
                
                # Security analysis with Bandit
                if check_type in ["security", "all"] and BANDIT_AVAILABLE:
                    security_issues = self._analyze_security_bandit(py_file)
                    file_results["issues"].extend(security_issues)
                
                # Style analysis with Pylint
                if check_type in ["style", "all"] and PYLINT_AVAILABLE:
                    style_issues = self._analyze_style_pylint(py_file)
                    file_results["issues"].extend(style_issues)
                
                # Code quality with Flake8
                if check_type in ["style", "all"] and FLAKE8_AVAILABLE:
                    flake8_issues = self._analyze_with_flake8(py_file)
                    file_results["issues"].extend(flake8_issues)
                
                # Performance analysis
                if check_type in ["performance", "all"]:
                    perf_issues = self._analyze_performance(py_file)
                    file_results["issues"].extend(perf_issues)
                
                # Filter by severity threshold
                file_results["issues"] = self._filter_by_severity(
                    file_results["issues"], severity_threshold
                )
                
                if file_results["issues"]:
                    results["issues"].append(file_results)
            
            # Calculate summary statistics
            results["summary"] = self._calculate_summary(results["issues"])
            results["metrics"] = self._calculate_metrics(python_files)
            
            return results
            
        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

    def _get_python_files(self, path: Path) -> List[Path]:
        """Get list of Python files to analyze."""
        python_files = []
        
        if path.is_file() and path.suffix == '.py':
            python_files.append(path)
        elif path.is_dir():
            python_files.extend(path.rglob('*.py'))
        
        # Filter out common non-source files
        excluded_patterns = ['__pycache__', '.git', 'venv', 'env', '.pytest_cache', 'node_modules']
        python_files = [
            f for f in python_files 
            if not any(pattern in str(f) for pattern in excluded_patterns)
        ]
        
        return python_files

    def _analyze_with_ast(self, file_path: Path, check_type: str) -> List[Dict[str, Any]]:
        """Analyze code using Python's AST module."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            # Create AST visitor for different check types
            if check_type in ["security", "all"]:
                issues.extend(self._ast_security_checks(tree, file_path))
            
            if check_type in ["style", "all"]:
                issues.extend(self._ast_style_checks(tree, file_path))
            
            if check_type in ["performance", "all"]:
                issues.extend(self._ast_performance_checks(tree, file_path))
            
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "severity": "high",
                "message": f"Syntax error: {e.msg}",
                "line": e.lineno,
                "column": e.offset,
                "category": "syntax"
            })
        except Exception as e:
            logger.warning(f"AST analysis failed for {file_path}: {e}")
        
        return issues

    def _ast_security_checks(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Security-focused AST checks."""
        issues = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append({
                            "type": "dangerous_function",
                            "severity": "high",
                            "message": f"Use of dangerous function: {node.func.id}",
                            "line": node.lineno,
                            "category": "security"
                        })
                    elif node.func.id == 'input' and len(node.args) == 0:
                        issues.append({
                            "type": "unsafe_input",
                            "severity": "medium",
                            "message": "Raw input() without prompt - potential security risk",
                            "line": node.lineno,
                            "category": "security"
                        })
                
                # Check for subprocess calls
                elif isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and 
                        node.func.value.id == 'subprocess' and
                        node.func.attr in ['call', 'run', 'Popen']):
                        # Check if shell=True is used
                        for keyword in node.keywords:
                            if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant):
                                if keyword.value.value is True:
                                    issues.append({
                                        "type": "shell_injection_risk",
                                        "severity": "high",
                                        "message": "subprocess call with shell=True - potential command injection",
                                        "line": node.lineno,
                                        "category": "security"
                                    })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for imports of potentially dangerous modules
                dangerous_modules = ['pickle', 'cPickle', 'dill']
                for alias in node.names:
                    if alias.name in dangerous_modules:
                        issues.append({
                            "type": "dangerous_import",
                            "severity": "medium",
                            "message": f"Import of potentially unsafe module: {alias.name}",
                            "line": node.lineno,
                            "category": "security"
                        })
                self.generic_visit(node)
        
        visitor = SecurityVisitor()
        visitor.visit(tree)
        return issues

    def _ast_style_checks(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Style-focused AST checks."""
        issues = []
        
        class StyleVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check function naming convention
                if not node.name.islower() and '_' not in node.name:
                    if not node.name.startswith('_'):  # Allow private methods
                        issues.append({
                            "type": "naming_convention",
                            "severity": "low",
                            "message": f"Function name '{node.name}' should be lowercase with underscores",
                            "line": node.lineno,
                            "category": "style"
                        })
                
                # Check for functions without docstrings
                if not ast.get_docstring(node):
                    if not node.name.startswith('_'):  # Ignore private methods
                        issues.append({
                            "type": "missing_docstring",
                            "severity": "low",
                            "message": f"Function '{node.name}' missing docstring",
                            "line": node.lineno,
                            "category": "documentation"
                        })
                
                # Check function complexity (number of statements)
                statements = sum(1 for _ in ast.walk(node) if isinstance(_, ast.stmt))
                if statements > 20:
                    issues.append({
                        "type": "complex_function",
                        "severity": "medium",
                        "message": f"Function '{node.name}' has {statements} statements (consider refactoring)",
                        "line": node.lineno,
                        "category": "complexity"
                    })
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check class naming convention
                if not node.name[0].isupper():
                    issues.append({
                        "type": "naming_convention",
                        "severity": "low",
                        "message": f"Class name '{node.name}' should start with uppercase letter",
                        "line": node.lineno,
                        "category": "style"
                    })
                
                # Check for classes without docstrings
                if not ast.get_docstring(node):
                    issues.append({
                        "type": "missing_docstring",
                        "severity": "low",
                        "message": f"Class '{node.name}' missing docstring",
                        "line": node.lineno,
                        "category": "documentation"
                    })
                
                self.generic_visit(node)
        
        visitor = StyleVisitor()
        visitor.visit(tree)
        return issues

    def _ast_performance_checks(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Performance-focused AST checks."""
        issues = []
        
        class PerformanceVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Check for inefficient list operations in loops
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call):
                        if (isinstance(stmt.func, ast.Attribute) and
                            stmt.func.attr == 'append' and
                            isinstance(stmt.func.value, ast.Name)):
                            # Suggest list comprehension
                            issues.append({
                                "type": "inefficient_loop",
                                "severity": "low",
                                "message": "Consider using list comprehension instead of append in loop",
                                "line": node.lineno,
                                "category": "performance"
                            })
                
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Check for repeated expensive operations
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['len', 'str', 'int']:
                        # Check if called on the same variable multiple times
                        pass  # Would need more complex analysis
                
                self.generic_visit(node)
        
        visitor = PerformanceVisitor()
        visitor.visit(tree)
        return issues

    def _analyze_security_bandit(self, file_path: Path) -> List[Dict[str, Any]]:
        """Security analysis using Bandit."""
        if not BANDIT_AVAILABLE:
            return []
        
        issues = []
        try:
            # Create bandit manager
            b_mgr = manager.BanditManager(None, 'file')
            b_mgr.discover_files([str(file_path)])
            b_mgr.run_tests()
            
            # Extract issues
            for issue in b_mgr.get_issue_list():
                issues.append({
                    "type": "security_issue",
                    "severity": issue.severity.lower(),
                    "message": issue.text,
                    "line": issue.lineno,
                    "category": "security",
                    "test_id": issue.test_id,
                    "confidence": issue.confidence.lower()
                })
        
        except Exception as e:
            logger.warning(f"Bandit analysis failed for {file_path}: {e}")
        
        return issues

    def _analyze_style_pylint(self, file_path: Path) -> List[Dict[str, Any]]:
        """Style analysis using Pylint."""
        if not PYLINT_AVAILABLE:
            return []
        
        issues = []
        try:
            # Capture pylint output
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp_file:
                try:
                    # Run pylint with output to temp file
                    pylint_run = PylintRun([str(file_path), f'--output={tmp_file.name}'], exit=False)
                    
                    # Read and parse output
                    tmp_file.seek(0)
                    output = tmp_file.read()
                    
                    # Parse pylint messages
                    for line in output.split('\n'):
                        if ':' in line and any(severity in line for severity in ['E', 'W', 'C', 'R']):
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                line_num = parts[1].strip()
                                message = parts[3].strip()
                                severity = "medium" if line.startswith(('E', 'W')) else "low"
                                
                                issues.append({
                                    "type": "style_issue",
                                    "severity": severity,
                                    "message": message,
                                    "line": int(line_num) if line_num.isdigit() else 0,
                                    "category": "style"
                                })
                
                finally:
                    os.unlink(tmp_file.name)
        
        except Exception as e:
            logger.warning(f"Pylint analysis failed for {file_path}: {e}")
        
        return issues

    def _analyze_with_flake8(self, file_path: Path) -> List[Dict[str, Any]]:
        """Code quality analysis using Flake8."""
        if not FLAKE8_AVAILABLE:
            return []
        
        issues = []
        try:
            style_guide = flake8.get_style_guide()
            report = style_guide.check_files([str(file_path)])
            
            # Extract issues from report
            for error in report.get_statistics('E'):
                parts = error.split(' ', 2)
                if len(parts) >= 3:
                    count = parts[0]
                    code = parts[1]
                    message = parts[2] if len(parts) > 2 else "Style violation"
                    
                    issues.append({
                        "type": "style_violation",
                        "severity": "low",
                        "message": f"{code}: {message}",
                        "line": 0,  # Flake8 aggregates, no specific line
                        "category": "style",
                        "code": code,
                        "count": int(count)
                    })
        
        except Exception as e:
            logger.warning(f"Flake8 analysis failed for {file_path}: {e}")
        
        return issues

    def _analyze_performance(self, file_path: Path) -> List[Dict[str, Any]]:
        """Performance analysis."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check for common performance anti-patterns
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for inefficient string concatenation
                if '+=' in line and '"' in line:
                    issues.append({
                        "type": "inefficient_string_concat",
                        "severity": "low",
                        "message": "Consider using join() for string concatenation in loops",
                        "line": i,
                        "category": "performance"
                    })
                
                # Check for global variable usage
                if line.startswith('global '):
                    issues.append({
                        "type": "global_variable",
                        "severity": "medium",
                        "message": "Global variable usage may impact performance",
                        "line": i,
                        "category": "performance"
                    })
        
        except Exception as e:
            logger.warning(f"Performance analysis failed for {file_path}: {e}")
        
        return issues

    def _filter_by_severity(self, issues: List[Dict[str, Any]], threshold: str) -> List[Dict[str, Any]]:
        """Filter issues by severity threshold."""
        severity_order = {"low": 0, "medium": 1, "high": 2}
        threshold_level = severity_order.get(threshold, 1)
        
        return [
            issue for issue in issues
            if severity_order.get(issue.get("severity", "low"), 0) >= threshold_level
        ]

    def _calculate_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        summary = {
            "total_issues": 0,
            "by_severity": {"high": 0, "medium": 0, "low": 0},
            "by_category": {}
        }
        
        for file_result in issues:
            for issue in file_result.get("issues", []):
                summary["total_issues"] += 1
                
                severity = issue.get("severity", "low")
                if severity in summary["by_severity"]:
                    summary["by_severity"][severity] += 1
                
                category = issue.get("category", "other")
                summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        return summary

    def _calculate_metrics(self, python_files: List[Path]) -> Dict[str, Any]:
        """Calculate code metrics."""
        metrics = {
            "total_files": len(python_files),
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "average_file_size": 0
        }
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = len(content.split('\n'))
                metrics["total_lines"] += lines
                
                # Parse AST for functions and classes
                tree = ast.parse(content)
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                
                metrics["total_functions"] += len(functions)
                metrics["total_classes"] += len(classes)
                
            except Exception as e:
                logger.warning(f"Metrics calculation failed for {file_path}: {e}")
        
        if metrics["total_files"] > 0:
            metrics["average_file_size"] = metrics["total_lines"] // metrics["total_files"]
        
        return metrics
