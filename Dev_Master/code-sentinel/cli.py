#!/usr/bin/env python3
"""
Code-Sentinel CLI

Command-line interface for security vulnerability scanning and fixing.

Usage:
    code-sentinel scan <path>                    # Scan for vulnerabilities
    code-sentinel scan <path> --critical-only    # Show only critical issues
    code-sentinel fix <path>                     # Auto-fix vulnerabilities
    code-sentinel fix <path> --dry-run           # Preview fixes without applying
    code-sentinel report <path>                  # Generate security report
    code-sentinel patterns                       # List all security patterns
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try importing as module, fall back to relative imports
try:
    from code_sentinel.core import CodeSentinel, SecurityScanner, SecurityFinding
    from code_sentinel.fixers.auto_fixer import AutoFixer, FixResult
    from code_sentinel.patterns.security_patterns import (
        ALL_PATTERNS,
        Severity,
        Category,
        get_patterns_by_severity,
        get_patterns_by_category
    )
except ModuleNotFoundError:
    # Use relative imports if module not installed
    sys.path.insert(0, str(Path(__file__).parent))
    from core import CodeSentinel, SecurityScanner, SecurityFinding
    from fixers.auto_fixer import AutoFixer, FixResult
    from patterns.security_patterns import (
        ALL_PATTERNS,
        Severity,
        Category,
        get_patterns_by_severity,
        get_patterns_by_category
    )


class Colors:
    """ANSI color codes for terminal output"""
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_banner():
    """Print the Code-Sentinel banner"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   {Colors.BOLD}CODE-SENTINEL{Colors.RESET}{Colors.CYAN}  🛡️                                    ║
║   Security Vulnerability Scanner & Auto-Fixer            ║
║                                                           ║
║   OWASP Top 10 | CWE Database | Auto-Fix                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def print_summary(summary: Dict[str, int]):
    """Print a summary of findings"""
    print(f"\n{Colors.BOLD}═══ SECURITY SCAN SUMMARY ══={Colors.RESET}\n")
    
    total = summary.get('total', 0)
    critical = summary.get('critical', 0)
    high = summary.get('high', 0)
    medium = summary.get('medium', 0)
    low = summary.get('low', 0)
    info = summary.get('info', 0)
    
    print(f"  Total Issues Found: {Colors.BOLD}{total}{Colors.RESET}")
    
    if critical > 0:
        print(f"  {Colors.RED}● CRITICAL: {critical}{Colors.RESET}")
    if high > 0:
        print(f"  {Colors.YELLOW}● HIGH:     {high}{Colors.RESET}")
    if medium > 0:
        print(f"  {Colors.BLUE}● MEDIUM:   {medium}{Colors.RESET}")
    if low > 0:
        print(f"  {Colors.GREEN}● LOW:      {low}{Colors.RESET}")
    if info > 0:
        print(f"  {Colors.CYAN}● INFO:     {info}{Colors.RESET}")
    
    print()
    
    if critical > 0:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  CRITICAL VULNERABILITIES DETECTED! Fix immediately.{Colors.RESET}")
    elif high > 0:
        print(f"{Colors.YELLOW}⚠️  High severity issues found. Review and fix soon.{Colors.RESET}")
    elif total > 0:
        print(f"{Colors.BLUE}ℹ️  Minor security issues detected. Consider fixing.{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✓ No security vulnerabilities detected!{Colors.RESET}")
    
    print()


def print_findings(findings: List[SecurityFinding], verbose: bool = False):
    """Print detailed findings"""
    if not findings:
        return
    
    print(f"\n{Colors.BOLD}═══ DETAILED FINDINGS ══={Colors.RESET}\n")
    
    for i, finding in enumerate(findings, 1):
        severity_color = {
            Severity.CRITICAL: Colors.RED,
            Severity.HIGH: Colors.YELLOW,
            Severity.MEDIUM: Colors.BLUE,
            Severity.LOW: Colors.GREEN,
            Severity.INFO: Colors.CYAN,
        }.get(finding.pattern.severity, Colors.RESET)
        
        print(f"{Colors.BOLD}[{i}] {severity_color}{finding.pattern.severity.value}{Colors.RESET} "
              f"{finding.pattern.name} ({finding.pattern.cwe_id})")
        print(f"    {Colors.CYAN}File:{Colors.RESET} {finding.file_path}:{finding.line_number}")
        print(f"    {Colors.CYAN}Issue:{Colors.RESET} {finding.pattern.description}")
        print(f"    {Colors.CYAN}Code:{Colors.RESET} {finding.line_content.strip()}")
        print(f"    {Colors.GREEN}Fix:{Colors.RESET} {finding.pattern.fix_strategy}")
        
        if verbose and finding.context_lines:
            print(f"    {Colors.CYAN}Context:{Colors.RESET}")
            for ctx_line in finding.context_lines:
                print(f"        {ctx_line.rstrip()}")
        
        print()


def cmd_scan(args):
    """Execute the scan command"""
    print_banner()
    
    path = args.path
    if not os.path.exists(path):
        print(f"{Colors.RED}Error: Path '{path}' does not exist{Colors.RESET}")
        sys.exit(1)
    
    print(f"{Colors.CYAN}Scanning:{Colors.RESET} {path}")
    
    if args.critical_only:
        print(f"{Colors.YELLOW}Mode:{Colors.RESET} Critical vulnerabilities only\n")
        findings = SecurityScanner.scan_critical_only(path)
        scanner = CodeSentinel(severity_threshold=Severity.CRITICAL)
        summary = scanner.get_summary() if findings else {"total": 0}
    elif args.severity:
        severity = Severity[args.severity.upper()]
        print(f"{Colors.YELLOW}Mode:{Colors.RESET} {severity.value} and above\n")
        scanner = CodeSentinel(severity_threshold=severity)
        if os.path.isfile(path):
            findings = scanner.scan_file(path)
        else:
            findings = scanner.scan_directory(path)
        summary = scanner.get_summary()
    else:
        print(f"{Colors.YELLOW}Mode:{Colors.RESET} All vulnerabilities\n")
        findings, summary = SecurityScanner.quick_scan(path, severity_threshold=Severity.INFO)
    
    print_summary(summary)
    print_findings(findings, verbose=args.verbose)
    
    if args.json:
        output_json(findings, summary, args.json)
        print(f"{Colors.GREEN}JSON report saved to: {args.json}{Colors.RESET}")
    
    # Exit with error code if critical/high issues found
    if summary.get('critical', 0) > 0:
        sys.exit(2)
    elif summary.get('high', 0) > 0:
        sys.exit(1)


def cmd_fix(args):
    """Execute the fix command"""
    print_banner()
    
    path = args.path
    if not os.path.exists(path):
        print(f"{Colors.RED}Error: Path '{path}' does not exist{Colors.RESET}")
        sys.exit(1)
    
    dry_run = args.dry_run
    mode_str = "DRY RUN (no changes will be made)" if dry_run else "LIVE MODE (files will be modified)"
    
    print(f"{Colors.CYAN}Scanning and fixing:{Colors.RESET} {path}")
    print(f"{Colors.YELLOW}Mode:{Colors.RESET} {mode_str}\n")
    
    # Scan for vulnerabilities
    scanner = CodeSentinel()
    if os.path.isfile(path):
        findings = scanner.scan_file(path)
    else:
        findings = scanner.scan_directory(path)
    
    if not findings:
        print(f"{Colors.GREEN}✓ No vulnerabilities found. Nothing to fix!{Colors.RESET}")
        return
    
    print(f"{Colors.BOLD}Found {len(findings)} vulnerabilities{Colors.RESET}\n")
    
    # Group findings by file
    findings_by_file: Dict[str, List[SecurityFinding]] = {}
    for finding in findings:
        filepath = finding.file_path
        if filepath not in findings_by_file:
            findings_by_file[filepath] = []
        findings_by_file[filepath].append(finding)
    
    # Fix each file
    fixer = AutoFixer(dry_run=dry_run)
    all_results: List[FixResult] = []
    
    for filepath, file_findings in findings_by_file.items():
        print(f"{Colors.CYAN}Fixing:{Colors.RESET} {filepath}")
        results = fixer.fix_file(filepath, file_findings)
        all_results.extend(results)
        
        for result in results:
            if result.success:
                print(f"  {Colors.GREEN}✓{Colors.RESET} {result.message}")
            else:
                print(f"  {Colors.YELLOW}⚠{Colors.RESET} {result.message}")
        print()
    
    # Print summary
    fix_summary = fixer.get_summary()
    print(f"\n{Colors.BOLD}═══ FIX SUMMARY ══={Colors.RESET}\n")
    print(f"  Total fixes attempted: {fix_summary['total']}")
    print(f"  {Colors.GREEN}✓ Successful: {fix_summary['successful']}{Colors.RESET}")
    print(f"  {Colors.YELLOW}⚠ Failed: {fix_summary['failed']}{Colors.RESET}\n")
    
    if dry_run:
        print(f"{Colors.CYAN}This was a dry run. Re-run without --dry-run to apply fixes.{Colors.RESET}")


def cmd_report(args):
    """Generate a security report"""
    print_banner()
    
    path = args.path
    if not os.path.exists(path):
        print(f"{Colors.RED}Error: Path '{path}' does not exist{Colors.RESET}")
        sys.exit(1)
    
    print(f"{Colors.CYAN}Generating security report for:{Colors.RESET} {path}\n")
    
    # Scan by OWASP category
    by_category = SecurityScanner.scan_for_owasp_top10(path)
    
    # Get all findings
    scanner = CodeSentinel()
    if os.path.isfile(path):
        scanner.scan_file(path)
    else:
        scanner.scan_directory(path)
    
    summary = scanner.get_summary()
    
    print(f"{Colors.BOLD}═══ OWASP TOP 10 BREAKDOWN ══={Colors.RESET}\n")
    
    for category, findings in sorted(by_category.items()):
        if findings:
            severity_counts = {}
            for finding in findings:
                sev = finding.pattern.severity.value
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            print(f"{Colors.BOLD}{category}{Colors.RESET}")
            print(f"  Issues: {len(findings)}")
            for sev, count in sorted(severity_counts.items(), reverse=True):
                print(f"    - {sev}: {count}")
            print()
    
    print_summary(summary)
    
    if args.output:
        generate_html_report(scanner.findings, summary, by_category, args.output)
        print(f"{Colors.GREEN}HTML report saved to: {args.output}{Colors.RESET}")


def cmd_patterns(args):
    """List all security patterns"""
    print_banner()
    
    print(f"{Colors.BOLD}═══ AVAILABLE SECURITY PATTERNS ══={Colors.RESET}\n")
    print(f"Total patterns: {len(ALL_PATTERNS)}\n")
    
    if args.category:
        category = Category[args.category.upper().replace('-', '_')]
        patterns = get_patterns_by_category(category)
        print(f"{Colors.CYAN}Category:{Colors.RESET} {category.value}\n")
    elif args.severity:
        severity = Severity[args.severity.upper()]
        patterns = get_patterns_by_severity(severity)
        print(f"{Colors.CYAN}Severity:{Colors.RESET} {severity.value}\n")
    else:
        patterns = ALL_PATTERNS
    
    # Group by category
    by_cat = {}
    for pattern in patterns:
        cat = pattern.category.value
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(pattern)
    
    for category, cat_patterns in sorted(by_cat.items()):
        print(f"{Colors.BOLD}{category}{Colors.RESET}")
        for pattern in cat_patterns:
            severity_color = {
                Severity.CRITICAL: Colors.RED,
                Severity.HIGH: Colors.YELLOW,
                Severity.MEDIUM: Colors.BLUE,
                Severity.LOW: Colors.GREEN,
                Severity.INFO: Colors.CYAN,
            }.get(pattern.severity, Colors.RESET)
            
            print(f"  [{severity_color}{pattern.severity.value}{Colors.RESET}] "
                  f"{pattern.name} ({pattern.cwe_id})")
            if args.verbose:
                print(f"      {pattern.description}")
        print()


def output_json(findings: List[SecurityFinding], summary: Dict[str, int], output_path: str):
    """Output findings as JSON"""
    data = {
        "summary": summary,
        "findings": [
            {
                "pattern": finding.pattern.name,
                "severity": finding.pattern.severity.value,
                "cwe": finding.pattern.cwe_id,
                "category": finding.pattern.category.value,
                "file": finding.file_path,
                "line": finding.line_number,
                "description": finding.pattern.description,
                "code": finding.line_content.strip(),
                "fix": finding.pattern.fix_strategy,
            }
            for finding in findings
        ]
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def generate_html_report(findings: List[SecurityFinding], 
                        summary: Dict[str, int],
                        by_category: Dict[str, List[SecurityFinding]],
                        output_path: str):
    """Generate an HTML security report"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code-Sentinel Security Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .critical {{ color: #e74c3c; }}
        .high {{ color: #f39c12; }}
        .medium {{ color: #3498db; }}
        .low {{ color: #2ecc71; }}
        .finding {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; border-radius: 3px; }}
        .finding.critical {{ border-left-color: #e74c3c; }}
        .finding.high {{ border-left-color: #f39c12; }}
        code {{ background: #ecf0f1; padding: 2px 5px; border-radius: 3px; }}
        .category {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Code-Sentinel Security Report</h1>
        <p>Generated: {os.popen('date').read().strip()}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Issues: <strong>{summary['total']}</strong></p>
        <p class="critical">CRITICAL: {summary['critical']}</p>
        <p class="high">HIGH: {summary['high']}</p>
        <p class="medium">MEDIUM: {summary['medium']}</p>
        <p class="low">LOW: {summary['low']}</p>
    </div>
    
    <div class="findings">
        <h2>Findings by Category</h2>
"""
    
    for category, cat_findings in sorted(by_category.items()):
        html += f"""
        <div class="category">
            <h3>{category}</h3>
"""
        for finding in cat_findings:
            severity_class = finding.pattern.severity.value.lower()
            html += f"""
            <div class="finding {severity_class}">
                <h4>[{finding.pattern.severity.value}] {finding.pattern.name}</h4>
                <p><strong>CWE:</strong> {finding.pattern.cwe_id}</p>
                <p><strong>File:</strong> {finding.file_path}:{finding.line_number}</p>
                <p><strong>Issue:</strong> {finding.pattern.description}</p>
                <p><strong>Code:</strong> <code>{finding.line_content.strip()}</code></p>
                <p><strong>Fix:</strong> {finding.pattern.fix_strategy}</p>
            </div>
"""
        html += "</div>"
    
    html += """
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Code-Sentinel - Security Vulnerability Scanner & Auto-Fixer',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for security vulnerabilities')
    scan_parser.add_argument('path', help='File or directory to scan')
    scan_parser.add_argument('--critical-only', action='store_true', help='Show only critical vulnerabilities')
    scan_parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low', 'info'], help='Minimum severity level')
    scan_parser.add_argument('--json', help='Output results as JSON to file')
    scan_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output with context')
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Auto-fix security vulnerabilities')
    fix_parser.add_argument('path', help='File or directory to fix')
    fix_parser.add_argument('--dry-run', action='store_true', help='Preview fixes without applying')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate security report')
    report_parser.add_argument('path', help='File or directory to analyze')
    report_parser.add_argument('-o', '--output', help='Output HTML report to file')
    
    # Patterns command
    patterns_parser = subparsers.add_parser('patterns', help='List all security patterns')
    patterns_parser.add_argument('--category', help='Filter by category')
    patterns_parser.add_argument('--severity', help='Filter by severity')
    patterns_parser.add_argument('-v', '--verbose', action='store_true', help='Show pattern descriptions')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command
    if args.command == 'scan':
        cmd_scan(args)
    elif args.command == 'fix':
        cmd_fix(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'patterns':
        cmd_patterns(args)


if __name__ == '__main__':
    main()
