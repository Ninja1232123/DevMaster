"""
Code-Sentinel Auto-Fixer

Automatically fixes detected security vulnerabilities by applying pattern-based
code transformations.
"""

import re
import os
import ast
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    from ..core import SecurityFinding
    from ..patterns.security_patterns import SecurityPattern
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core import SecurityFinding
    from patterns.security_patterns import SecurityPattern


@dataclass
class FixResult:
    """Result of applying a fix"""
    finding: SecurityFinding
    success: bool
    old_code: str
    new_code: str
    message: str


class AutoFixer:
    """Automatically fixes security vulnerabilities"""

    def __init__(self, dry_run: bool = False):
        """
        Initialize the auto-fixer

        Args:
            dry_run: If True, don't actually modify files
        """
        self.dry_run = dry_run
        self.fix_results: List[FixResult] = []

    def fix_finding(self, finding: SecurityFinding) -> FixResult:
        """
        Fix a single security finding

        Args:
            finding: The security finding to fix

        Returns:
            FixResult with details of the fix attempt
        """
        pattern_name = finding.pattern.name
        fixer_method = getattr(self, f"_fix_{pattern_name}", None)

        if fixer_method:
            return fixer_method(finding)
        else:
            return self._generic_fix(finding)

    def fix_file(self, filepath: str, findings: List[SecurityFinding]) -> List[FixResult]:
        """
        Fix all findings in a file

        Args:
            filepath: Path to the file
            findings: List of findings in this file

        Returns:
            List of fix results
        """
        results = []

        # Group findings by line number to avoid conflicts
        findings_by_line = {}
        for finding in findings:
            line = finding.line_number
            if line not in findings_by_line:
                findings_by_line[line] = []
            findings_by_line[line].append(finding)

        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Apply fixes line by line (in reverse to preserve line numbers)
        for line_num in sorted(findings_by_line.keys(), reverse=True):
            for finding in findings_by_line[line_num]:
                result = self.fix_finding(finding)
                results.append(result)

                if result.success and not self.dry_run:
                    # Update the line
                    lines[line_num - 1] = result.new_code + '\n'

        # Write back to file if not dry run
        if not self.dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)

        self.fix_results.extend(results)
        return results

    # ========================================================================
    # SQL INJECTION FIXERS
    # ========================================================================

    def _fix_sql_string_concatenation(self, finding: SecurityFinding) -> FixResult:
        """Fix SQL queries with string concatenation"""
        old_code = finding.line_content
        
        # Try to extract the query and convert to parameterized
        # Pattern: execute("... + var + ...")
        if 'execute(' in old_code:
            # Simple heuristic: replace concatenation with placeholders
            new_code = old_code
            
            # Replace f-strings with parameterized queries
            if re.search(r'f["\']', old_code):
                # Extract variables from f-string
                var_pattern = r'\{(\w+)\}'
                variables = re.findall(var_pattern, old_code)
                
                if variables:
                    # Replace f"...{var}..." with "...?..." and add variables as tuple
                    fixed = re.sub(var_pattern, '?', old_code)
                    fixed = re.sub(r'f(["\'])', r'\1', fixed)  # Remove f prefix
                    
                    # Add parameter tuple
                    if '.execute(' in fixed:
                        fixed = fixed.replace(')', f", ({', '.join(variables)},))")
                    
                    return FixResult(
                        finding=finding,
                        success=True,
                        old_code=old_code,
                        new_code=fixed,
                        message="Converted f-string SQL to parameterized query"
                    )
            
            # Replace + concatenation
            if '+' in old_code and 'execute' in old_code:
                # This is more complex, provide a comment suggestion
                fixed = f"{old_code.rstrip()}  # SECURITY: Use parameterized query instead"
                return FixResult(
                    finding=finding,
                    success=True,
                    old_code=old_code,
                    new_code=fixed,
                    message="Added security warning comment"
                )

        return FixResult(
            finding=finding,
            success=False,
            old_code=old_code,
            new_code=old_code,
            message="Unable to automatically fix SQL injection"
        )

    def _fix_orm_raw_query(self, finding: SecurityFinding) -> FixResult:
        """Fix ORM raw queries"""
        old_code = finding.line_content
        
        # Replace f-strings with %s parameters
        if 'f"' in old_code or "f'" in old_code:
            var_pattern = r'\{(\w+)\}'
            variables = re.findall(var_pattern, old_code)
            
            if variables:
                fixed = re.sub(var_pattern, '%s', old_code)
                fixed = re.sub(r'f(["\'])', r'\1', fixed)
                
                # Add parameters list
                if '.raw(' in fixed:
                    fixed = fixed.replace(')', f", [{', '.join(variables)}])")
                
                return FixResult(
                    finding=finding,
                    success=True,
                    old_code=old_code,
                    new_code=fixed,
                    message="Converted to parameterized raw query"
                )

        return FixResult(
            finding=finding,
            success=False,
            old_code=old_code,
            new_code=old_code,
            message="Unable to automatically fix ORM raw query"
        )

    # ========================================================================
    # CREDENTIAL FIXERS
    # ========================================================================

    def _fix_hardcoded_password(self, finding: SecurityFinding) -> FixResult:
        """Fix hardcoded passwords"""
        old_code = finding.line_content
        
        # Extract variable name
        match = re.search(r'(\w+)\s*=\s*["\']', old_code)
        if match:
            var_name = match.group(1)
            indent = len(old_code) - len(old_code.lstrip())
            
            # Replace with environment variable
            new_code = f"{' ' * indent}{var_name} = os.environ.get(\"{var_name.upper()}\")"
            
            # Add import if needed
            import_added = False
            if not self._has_import(finding.file_path, "import os"):
                import_added = True
            
            message = "Replaced hardcoded credential with environment variable"
            if import_added:
                message += " (add 'import os' at top of file)"
            
            return FixResult(
                finding=finding,
                success=True,
                old_code=old_code,
                new_code=new_code,
                message=message
            )

        return FixResult(
            finding=finding,
            success=False,
            old_code=old_code,
            new_code=old_code,
            message="Unable to automatically fix hardcoded credential"
        )

    def _fix_hardcoded_database_uri(self, finding: SecurityFinding) -> FixResult:
        """Fix hardcoded database URIs"""
        return self._fix_hardcoded_password(finding)  # Same logic

    # ========================================================================
    # XSS FIXERS
    # ========================================================================

    def _fix_unsafe_html_rendering(self, finding: SecurityFinding) -> FixResult:
        """Fix unsafe HTML rendering"""
        old_code = finding.line_content
        
        # Replace Markup() with escape()
        if 'Markup(' in old_code:
            new_code = old_code.replace('Markup(', 'escape(')
            return FixResult(
                finding=finding,
                success=True,
                old_code=old_code,
                new_code=new_code,
                message="Replaced Markup() with escape() (import from markupsafe)"
            )
        
        # Replace mark_safe() with escape()
        if 'mark_safe(' in old_code:
            new_code = old_code.replace('mark_safe(', 'escape(')
            return FixResult(
                finding=finding,
                success=True,
                old_code=old_code,
                new_code=new_code,
                message="Replaced mark_safe() with escape() (import from markupsafe)"
            )

        return FixResult(
            finding=finding,
            success=False,
            old_code=old_code,
            new_code=old_code,
            message="Unable to automatically fix XSS vulnerability"
        )

    def _fix_unsafe_redirect(self, finding: SecurityFinding) -> FixResult:
        """Fix unsafe redirects"""
        old_code = finding.line_content
        indent = len(old_code) - len(old_code.lstrip())
        
        # Add validation before redirect
        validation_code = f"""{' ' * indent}# SECURITY: Validate redirect URL
{' ' * indent}ALLOWED_REDIRECTS = ["/dashboard", "/home", "/profile"]
{' ' * indent}redirect_url = request.args.get("next", "/")
{' ' * indent}if redirect_url not in ALLOWED_REDIRECTS:
{' ' * indent}    redirect_url = "/"
{old_code.replace('request.args.get("next")', 'redirect_url').replace("request.args.get('next')", 'redirect_url')}"""
        
        return FixResult(
            finding=finding,
            success=True,
            old_code=old_code,
            new_code=validation_code,
            message="Added redirect URL validation"
        )

    # ========================================================================
    # COMMAND INJECTION FIXERS
    # ========================================================================

    def _fix_shell_command_concatenation(self, finding: SecurityFinding) -> FixResult:
        """Fix shell command injection"""
        old_code = finding.line_content
        indent = len(old_code) - len(old_code.lstrip())
        
        if 'os.system(' in old_code:
            # Try to convert to subprocess.run()
            # Extract the command
            match = re.search(r'os\.system\(["\']?([^"\']+)', old_code)
            if match:
                new_code = f"{' ' * indent}import subprocess\n"
                new_code += f"{' ' * indent}# SECURITY: Use subprocess with argument list instead\n"
                new_code += f"{' ' * indent}# subprocess.run([\"command\", \"arg1\", \"arg2\"], check=True)"
                
                return FixResult(
                    finding=finding,
                    success=True,
                    old_code=old_code,
                    new_code=new_code,
                    message="Added suggestion to use subprocess.run() with argument list"
                )
        
        if 'shell=True' in old_code:
            new_code = old_code.replace('shell=True', 'shell=False  # SECURITY: Changed to False')
            return FixResult(
                finding=finding,
                success=True,
                old_code=old_code,
                new_code=new_code,
                message="Changed shell=True to shell=False"
            )

        return FixResult(
            finding=finding,
            success=False,
            old_code=old_code,
            new_code=old_code,
            message="Unable to automatically fix command injection"
        )

    # ========================================================================
    # DESERIALIZATION FIXERS
    # ========================================================================

    def _fix_pickle_unsafe_load(self, finding: SecurityFinding) -> FixResult:
        """Fix unsafe pickle usage"""
        old_code = finding.line_content
        
        # Replace pickle with json
        if 'pickle.load' in old_code:
            new_code = old_code.replace('pickle.load', 'json.load')
            return FixResult(
                finding=finding,
                success=True,
                old_code=old_code,
                new_code=new_code,
                message="Replaced pickle.load with json.load (import json)"
            )

        return FixResult(
            finding=finding,
            success=False,
            old_code=old_code,
            new_code=old_code,
            message="Unable to automatically fix pickle usage"
        )

    def _fix_yaml_unsafe_load(self, finding: SecurityFinding) -> FixResult:
        """Fix unsafe YAML loading"""
        old_code = finding.line_content
        
        # Replace yaml.load with yaml.safe_load
        if 'yaml.load(' in old_code:
            new_code = old_code.replace('yaml.load(', 'yaml.safe_load(')
            return FixResult(
                finding=finding,
                success=True,
                old_code=old_code,
                new_code=new_code,
                message="Replaced yaml.load() with yaml.safe_load()"
            )

        return FixResult(
            finding=finding,
            success=False,
            old_code=old_code,
            new_code=old_code,
            message="Unable to automatically fix YAML loading"
        )

    # ========================================================================
    # CRYPTO FIXERS
    # ========================================================================

    def _fix_weak_hash_algorithm(self, finding: SecurityFinding) -> FixResult:
        """Fix weak hash algorithms"""
        old_code = finding.line_content
        
        # Replace MD5 with SHA256
        if 'md5' in old_code.lower():
            new_code = re.sub(r'md5', 'sha256', old_code, flags=re.IGNORECASE)
            return FixResult(
                finding=finding,
                success=True,
                old_code=old_code,
                new_code=new_code,
                message="Replaced MD5 with SHA256"
            )
        
        # Replace SHA1 with SHA256
        if 'sha1' in old_code.lower():
            new_code = re.sub(r'sha1', 'sha256', old_code, flags=re.IGNORECASE)
            return FixResult(
                finding=finding,
                success=True,
                old_code=old_code,
                new_code=new_code,
                message="Replaced SHA1 with SHA256"
            )

        return FixResult(
            finding=finding,
            success=False,
            old_code=old_code,
            new_code=old_code,
            message="Unable to automatically fix weak hash"
        )

    # ========================================================================
    # DEBUG MODE FIXERS
    # ========================================================================

    def _fix_debug_mode_enabled(self, finding: SecurityFinding) -> FixResult:
        """Fix hardcoded DEBUG=True"""
        old_code = finding.line_content
        indent = len(old_code) - len(old_code.lstrip())

        # Replace DEBUG = True with environment variable
        indent_str = ' ' * indent
        new_code = f'{indent_str}DEBUG = os.environ.get("DEBUG", "False") == "True"'

        return FixResult(
            finding=finding,
            success=True,
            old_code=old_code,
            new_code=new_code,
            message="Replaced hardcoded DEBUG with environment variable"
        )

    # ========================================================================
    # LOGGING FIXERS
    # ========================================================================

    def _fix_logging_sensitive_data(self, finding: SecurityFinding) -> FixResult:
        """Fix logging of sensitive data"""
        old_code = finding.line_content
        
        # Add a comment warning
        new_code = f"{old_code.rstrip()}  # SECURITY WARNING: Logging sensitive data!"
        
        # Try to redact the sensitive parts
        sensitive_keywords = ['password', 'token', 'secret', 'api_key']
        for keyword in sensitive_keywords:
            if keyword in old_code.lower():
                # Add redaction suggestion
                indent = len(old_code) - len(old_code.lstrip())
                new_code = f"{' ' * indent}# SECURITY: Redact {keyword} before logging\n{old_code}"
                break
        
        return FixResult(
            finding=finding,
            success=True,
            old_code=old_code,
            new_code=new_code,
            message="Added security warning for sensitive data logging"
        )

    # ========================================================================
    # GENERIC FIXER
    # ========================================================================

    def _generic_fix(self, finding: SecurityFinding) -> FixResult:
        """Generic fix that adds a security comment"""
        old_code = finding.line_content
        indent = len(old_code) - len(old_code.lstrip())
        
        new_code = f"{' ' * indent}# SECURITY: {finding.pattern.description}\n"
        new_code += f"{' ' * indent}# Fix: {finding.pattern.fix_strategy}\n"
        new_code += old_code
        
        return FixResult(
            finding=finding,
            success=True,
            old_code=old_code,
            new_code=new_code,
            message="Added security comment with fix suggestion"
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _has_import(self, filepath: str, import_statement: str) -> bool:
        """Check if file already has an import"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                return import_statement in content
        except:
            return False

    def get_summary(self) -> Dict[str, int]:
        """Get summary of fix results"""
        return {
            "total": len(self.fix_results),
            "successful": sum(1 for r in self.fix_results if r.success),
            "failed": sum(1 for r in self.fix_results if not r.success),
        }
