import subprocess
import tempfile
import os
from typing import Dict, Any, List
from pathlib import Path
import json


class CodeQualityAnalyzer:
    def __init__(self):
        self.issues = []
        self.warnings = 0
        self.errors = 0
    
    def analyze_diff(self, diff_content: str, file_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.issues = []
        self.warnings = 0
        self.errors = 0
        
        results = {
            "files_changed": len(file_changes),
            "lines_added": 0,
            "lines_removed": 0,
            "issues": [],
            "score": 100,
            "summary": ""
        }
        
        for file_change in file_changes:
            if "patch" in file_change:
                patch = file_change["patch"]
                lines_added = patch.count("\n+")
                lines_removed = patch.count("\n-")
                results["lines_added"] += lines_added
                results["lines_removed"] += lines_removed
                
                if file_change["filename"].endswith(".py"):
                    file_issues = self._analyze_python_file(
                        file_change["filename"], 
                        patch
                    )
                    results["issues"].extend(file_issues)
        
        self.warnings = sum(1 for issue in results["issues"] if issue["severity"] == "warning")
        self.errors = sum(1 for issue in results["issues"] if issue["severity"] == "error")
        
        results["warnings"] = self.warnings
        results["errors"] = self.errors
        results["score"] = max(0, 100 - (self.errors * 10) - (self.warnings * 2))
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _analyze_python_file(self, filename: str, patch: str) -> List[Dict[str, Any]]:
        issues = []
        
        lines = patch.split("\n")
        added_lines = [line[1:] for line in lines if line.startswith("+") and not line.startswith("+++")]
        
        if not added_lines:
            return issues
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file.write("\n".join(added_lines))
            tmp_file_path = tmp_file.name
        
        try:
            flake8_issues = self._run_flake8(tmp_file_path, filename)
            issues.extend(flake8_issues)
            
            pylint_issues = self._run_pylint(tmp_file_path, filename)
            issues.extend(pylint_issues)
        finally:
            os.unlink(tmp_file_path)
        
        return issues
    
    def _run_flake8(self, file_path: str, original_filename: str) -> List[Dict[str, Any]]:
        issues = []
        try:
            result = subprocess.run(
                ["flake8", "--format=json", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                try:
                    flake8_output = json.loads(result.stdout)
                    for file_issues in flake8_output.values():
                        for issue in file_issues:
                            issues.append({
                                "file": original_filename,
                                "line": issue.get("line_number", 0),
                                "column": issue.get("column_number", 0),
                                "message": issue.get("text", ""),
                                "code": issue.get("code", ""),
                                "severity": "warning",
                                "tool": "flake8"
                            })
                except json.JSONDecodeError:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return issues
    
    def _run_pylint(self, file_path: str, original_filename: str) -> List[Dict[str, Any]]:
        issues = []
        try:
            result = subprocess.run(
                ["pylint", "--output-format=json", "--disable=all", 
                 "--enable=E,W", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                try:
                    pylint_output = json.loads(result.stdout)
                    for issue in pylint_output:
                        severity = "error" if issue.get("type") == "error" else "warning"
                        issues.append({
                            "file": original_filename,
                            "line": issue.get("line", 0),
                            "column": issue.get("column", 0),
                            "message": issue.get("message", ""),
                            "code": issue.get("message-id", ""),
                            "severity": severity,
                            "tool": "pylint"
                        })
                except json.JSONDecodeError:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return issues
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        summary_parts = []
        
        if results["errors"] == 0 and results["warnings"] == 0:
            summary_parts.append("✓ No issues found. Code quality looks good!")
        else:
            if results["errors"] > 0:
                summary_parts.append(f"✗ Found {results['errors']} error(s)")
            if results["warnings"] > 0:
                summary_parts.append(f"⚠ Found {results['warnings']} warning(s)")
        
        summary_parts.append(f"Score: {results['score']}/100")
        
        return " | ".join(summary_parts)
    
    def analyze_complexity(self, code: str) -> Dict[str, Any]:
        lines = code.split("\n")
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
        
        complexity = {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_lines": len([line for line in lines if line.strip().startswith("#")]),
            "blank_lines": len([line for line in lines if not line.strip()]),
        }
        
        return complexity
