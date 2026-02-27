"""
Code-Sentinel Core Scanner Engine

This module contains the main scanning logic that detects security vulnerabilities
in Python code using pattern matching and AST analysis.
"""

import ast
import re
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

try:
    from .patterns.security_patterns import (
        SecurityPattern,
        ALL_PATTERNS,
        Severity,
        get_patterns_by_severity,
        get_patterns_by_category
    )
except ImportError:
    from patterns.security_patterns import (
        SecurityPattern,
        ALL_PATTERNS,
        Severity,
        get_patterns_by_severity,
        get_patterns_by_category
    )


@dataclass
class SecurityFinding:
    """Represents a detected security vulnerability"""
    pattern: SecurityPattern
    file_path: str
    line_number: int
    line_content: str
    column: Optional[int] = None
    context_lines: List[str] = field(default_factory=list)
    confidence: float = 1.0

    def __str__(self):
        severity_colors = {
            Severity.CRITICAL: "\033[91m",  # Red
            Severity.HIGH: "\033[93m",      # Yellow
            Severity.MEDIUM: "\033[94m",    # Blue
            Severity.LOW: "\033[92m",       # Green
            Severity.INFO: "\033[96m",      # Cyan
        }
        reset = "\033[0m"
        color = severity_colors.get(self.pattern.severity, "")

        return (
            f"{color}[{self.pattern.severity.value}]{reset} "
            f"{self.pattern.name} ({self.pattern.cwe_id})\n"
            f"  File: {self.file_path}:{self.line_number}\n"
            f"  Issue: {self.pattern.description}\n"
            f"  Code: {self.line_content.strip()}\n"
            f"  Fix: {self.pattern.fix_strategy}"
        )


class CodeSentinel:
    """Main security scanner class"""

    def __init__(self,
                 patterns: List[SecurityPattern] = None,
                 severity_threshold: Severity = Severity.INFO,
                 ignore_patterns: List[str] = None):
        """
        Initialize the scanner

        Args:
            patterns: List of patterns to check (default: all patterns)
            severity_threshold: Minimum severity to report
            ignore_patterns: File patterns to ignore (e.g., ['test_*.py', '*/migrations/*'])
        """
        self.patterns = patterns or ALL_PATTERNS
        self.severity_threshold = severity_threshold
        self.ignore_patterns = ignore_patterns or []
        self.findings: List[SecurityFinding] = []

    def should_ignore_file(self, filepath: str) -> bool:
        """Check if file should be ignored based on ignore patterns"""
        for pattern in self.ignore_patterns:
            if re.search(pattern, filepath):
                return True
        return False

    def scan_file(self, filepath: str) -> List[SecurityFinding]:
        """
        Scan a single Python file for security vulnerabilities

        Args:
            filepath: Path to the Python file

        Returns:
            List of security findings
        """
        if self.should_ignore_file(filepath):
            return []

        findings = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Regex-based scanning
            findings.extend(self._scan_with_regex(filepath, lines))

            # AST-based scanning
            findings.extend(self._scan_with_ast(filepath, content))

        except Exception as e:
            print(f"Error scanning {filepath}: {e}")

        return findings

    def _scan_with_regex(self, filepath: str, lines: List[str]) -> List[SecurityFinding]:
        """Scan file using regex patterns"""
        findings = []

        for line_num, line in enumerate(lines, start=1):
            for pattern in self.patterns:
                # Check severity threshold
                if self._severity_level(pattern.severity) < self._severity_level(self.severity_threshold):
                    continue

                for regex in pattern.regex_patterns:
                    try:
                        if re.search(regex, line, re.IGNORECASE):
                            # Get context lines (2 before, 2 after)
                            context = self._get_context_lines(lines, line_num, context_size=2)

                            finding = SecurityFinding(
                                pattern=pattern,
                                file_path=filepath,
                                line_number=line_num,
                                line_content=line,
                                context_lines=context
                            )
                            findings.append(finding)
                            break  # Don't report same pattern multiple times per line
                    except re.error:
                        continue

        return findings

    def _scan_with_ast(self, filepath: str, content: str) -> List[SecurityFinding]:
        """Scan file using AST analysis"""
        findings = []

        try:
            tree = ast.parse(content)

            # Walk through AST nodes
            for node in ast.walk(tree):
                for pattern in self.patterns:
                    if pattern.ast_check and callable(pattern.ast_check):
                        if pattern.ast_check(node):
                            line_num = getattr(node, 'lineno', 0)
                            col = getattr(node, 'col_offset', 0)

                            # Get the actual line content
                            lines = content.split('\n')
                            line_content = lines[line_num - 1] if line_num > 0 else ""

                            finding = SecurityFinding(
                                pattern=pattern,
                                file_path=filepath,
                                line_number=line_num,
                                line_content=line_content,
                                column=col,
                                context_lines=self._get_context_lines(lines, line_num)
                            )
                            findings.append(finding)

        except SyntaxError:
            # Can't parse file, skip AST scanning
            pass

        return findings

    def _get_context_lines(self, lines: List[str], line_num: int, context_size: int = 2) -> List[str]:
        """Get surrounding lines for context"""
        start = max(0, line_num - context_size - 1)
        end = min(len(lines), line_num + context_size)
        return lines[start:end]

    def _severity_level(self, severity: Severity) -> int:
        """Convert severity to numeric level for comparison"""
        levels = {
            Severity.CRITICAL: 4,
            Severity.HIGH: 3,
            Severity.MEDIUM: 2,
            Severity.LOW: 1,
            Severity.INFO: 0,
        }
        return levels.get(severity, 0)

    def scan_directory(self, directory: str, recursive: bool = True) -> List[SecurityFinding]:
        """
        Scan a directory for security vulnerabilities

        Args:
            directory: Path to directory
            recursive: Whether to scan subdirectories

        Returns:
            List of all findings
        """
        findings = []

        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]

                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        findings.extend(self.scan_file(filepath))
        else:
            for file in os.listdir(directory):
                if file.endswith('.py'):
                    filepath = os.path.join(directory, file)
                    if os.path.isfile(filepath):
                        findings.extend(self.scan_file(filepath))

        self.findings = findings
        return findings

    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics of findings"""
        summary = {
            "total": len(self.findings),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for finding in self.findings:
            severity = finding.pattern.severity.value.lower()
            if severity in summary:
                summary[severity] += 1

        return summary

    def get_findings_by_severity(self, severity: Severity) -> List[SecurityFinding]:
        """Get all findings of a specific severity"""
        return [f for f in self.findings if f.pattern.severity == severity]

    def get_findings_by_file(self, filepath: str) -> List[SecurityFinding]:
        """Get all findings for a specific file"""
        return [f for f in self.findings if f.file_path == filepath]

    def filter_findings(self,
                       min_severity: Optional[Severity] = None,
                       max_severity: Optional[Severity] = None,
                       pattern_names: Optional[List[str]] = None,
                       file_pattern: Optional[str] = None) -> List[SecurityFinding]:
        """
        Filter findings based on criteria

        Args:
            min_severity: Minimum severity level
            max_severity: Maximum severity level
            pattern_names: List of pattern names to include
            file_pattern: Regex pattern for file paths

        Returns:
            Filtered list of findings
        """
        filtered = self.findings

        if min_severity:
            min_level = self._severity_level(min_severity)
            filtered = [f for f in filtered if self._severity_level(f.pattern.severity) >= min_level]

        if max_severity:
            max_level = self._severity_level(max_severity)
            filtered = [f for f in filtered if self._severity_level(f.pattern.severity) <= max_level]

        if pattern_names:
            filtered = [f for f in filtered if f.pattern.name in pattern_names]

        if file_pattern:
            filtered = [f for f in filtered if re.search(file_pattern, f.file_path)]

        return filtered


class SecurityScanner:
    """High-level scanner interface with convenience methods"""

    @staticmethod
    def quick_scan(path: str,
                   severity_threshold: Severity = Severity.HIGH) -> Tuple[List[SecurityFinding], Dict[str, int]]:
        """
        Quick scan with sensible defaults

        Args:
            path: File or directory to scan
            severity_threshold: Minimum severity to report (default: HIGH)

        Returns:
            Tuple of (findings, summary)
        """
        scanner = CodeSentinel(severity_threshold=severity_threshold)

        if os.path.isfile(path):
            findings = scanner.scan_file(path)
        else:
            findings = scanner.scan_directory(path)

        return findings, scanner.get_summary()

    @staticmethod
    def scan_for_owasp_top10(path: str) -> Dict[str, List[SecurityFinding]]:
        """
        Scan specifically for OWASP Top 10 vulnerabilities

        Args:
            path: File or directory to scan

        Returns:
            Dictionary mapping category names to findings
        """
        scanner = CodeSentinel()

        if os.path.isfile(path):
            scanner.scan_file(path)
        else:
            scanner.scan_directory(path)

        # Group by category
        by_category = {}
        for finding in scanner.findings:
            category = finding.pattern.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(finding)

        return by_category

    @staticmethod
    def scan_critical_only(path: str) -> List[SecurityFinding]:
        """Scan for critical vulnerabilities only"""
        scanner = CodeSentinel(severity_threshold=Severity.CRITICAL)

        if os.path.isfile(path):
            return scanner.scan_file(path)
        else:
            return scanner.scan_directory(path)
