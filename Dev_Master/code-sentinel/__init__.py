"""
Code-Sentinel - Security Vulnerability Scanner & Auto-Fixer

A comprehensive security scanning tool that detects and automatically fixes
vulnerabilities based on OWASP Top 10 and CWE database.
"""

__version__ = "1.0.0"
__author__ = "Claude (Anthropic)"

from .core import CodeSentinel, SecurityScanner, SecurityFinding
from .patterns.security_patterns import (
    SecurityPattern,
    Severity,
    Category,
    ALL_PATTERNS
)
from .fixers.auto_fixer import AutoFixer, FixResult

__all__ = [
    'CodeSentinel',
    'SecurityScanner',
    'SecurityFinding',
    'SecurityPattern',
    'Severity',
    'Category',
    'ALL_PATTERNS',
    'AutoFixer',
    'FixResult',
]
