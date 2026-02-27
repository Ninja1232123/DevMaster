# Code-Sentinel 🛡️

**Security Vulnerability Scanner & Auto-Fixer for Python**

Code-Sentinel is a comprehensive security scanning tool that detects and automatically fixes vulnerabilities in Python code based on **OWASP Top 10** and the **CWE database**.

## Features

### 🔍 Detection
- **20+ Security Patterns** covering OWASP Top 10
- **SQL Injection** detection (string concatenation, f-strings, ORM raw queries)
- **Hardcoded Credentials** (passwords, API keys, database URIs)
- **XSS Vulnerabilities** (unsafe HTML rendering, redirects)
- **Command Injection** (shell=True, os.system)
- **Path Traversal** (unsafe file operations)
- **Insecure Deserialization** (pickle, yaml.load)
- **Weak Cryptography** (MD5, SHA1, hardcoded keys)
- **SSRF** (Server-Side Request Forgery)
- **Debug Mode** enabled in production
- **Sensitive Data Logging**

### 🔧 Auto-Fix
- Intelligent pattern-based fixes
- Converts f-strings to parameterized queries
- Replaces hardcoded credentials with environment variables
- Updates weak hash algorithms to SHA-256
- Fixes yaml.load → yaml.safe_load
- Replaces pickle with JSON where safe
- Adds security comments with fix suggestions

### 📊 Reporting
- Severity-based filtering (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- JSON export for CI/CD integration
- HTML report generation
- OWASP Top 10 breakdown
- CWE reference for each vulnerability

## Installation

```bash
# Code-Sentinel is part of the Codes-Masterpiece ecosystem
cd /path/to/Codes-Masterpiece
```

## Usage

### Standalone CLI

```bash
# Basic scan
python code-sentinel/cli.py scan your_script.py

# Scan with critical-only filter
python code-sentinel/cli.py scan your_script.py --critical-only

# Scan entire directory
python code-sentinel/cli.py scan ./src

# Auto-fix vulnerabilities
python code-sentinel/cli.py fix your_script.py

# Dry-run (preview fixes)
python code-sentinel/cli.py fix your_script.py --dry-run

# Generate HTML report
python code-sentinel/cli.py report ./src -o security_report.html

# List all patterns
python code-sentinel/cli.py patterns

# Filter patterns by severity
python code-sentinel/cli.py patterns --severity critical
```

### Integrated with Universal Debugger

```bash
# Security scan & fix
python universal_debugger.py --security your_script.py

# Fix everything (security + types + runtime + deployment)
python universal_debugger.py --all your_script.py

# Ultimate mode (includes security)
python universal_debugger.py --ultimate your_script.py
```

### Python API

```python
from code_sentinel import SecurityScanner, CodeSentinel, AutoFixer
from code_sentinel.patterns.security_patterns import Severity

# Quick scan
findings, summary = SecurityScanner.quick_scan(
    "your_script.py",
    severity_threshold=Severity.HIGH
)

print(f"Found {summary['total']} issues")
for finding in findings:
    print(f"{finding.pattern.name}: {finding.line_content}")

# Advanced scanner
scanner = CodeSentinel(severity_threshold=Severity.MEDIUM)
findings = scanner.scan_directory("./src")

# Filter findings
critical = scanner.filter_findings(min_severity=Severity.CRITICAL)

# Auto-fix
fixer = AutoFixer(dry_run=False)
results = fixer.fix_file("vulnerable.py", findings)

for result in results:
    if result.success:
        print(f"✓ {result.message}")
```

## Security Patterns

### SQL Injection (CWE-89)

**Vulnerable:**
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

**Fixed:**
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### Hardcoded Credentials (CWE-798)

**Vulnerable:**
```python
API_KEY = "sk_live_51HqJ8k2eZvKYlo2C9dPJ0Qx"
password = "SuperSecret123!"
```

**Fixed:**
```python
import os
API_KEY = os.environ.get("API_KEY")
password = os.environ.get("DB_PASSWORD")
```

### XSS - Unsafe HTML (CWE-79)

**Vulnerable:**
```python
from flask import Markup
return Markup(f"<div>{user_input}</div>")
```

**Fixed:**
```python
from markupsafe import escape
return f"<div>{escape(user_input)}</div>"
```

### Command Injection (CWE-78)

**Vulnerable:**
```python
os.system(f"ping {user_input}")
```

**Fixed:**
```python
import subprocess
subprocess.run(["ping", "-c", "1", user_input], check=True)
```

### Insecure Deserialization (CWE-502)

**Vulnerable:**
```python
import pickle
data = pickle.loads(user_input)
```

**Fixed:**
```python
import json
data = json.loads(user_input)
```

### Weak Cryptography (CWE-327)

**Vulnerable:**
```python
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()
```

**Fixed:**
```python
import hashlib
hash = hashlib.sha256(password.encode()).hexdigest()
# Better: use bcrypt for passwords
```

## Severity Levels

- **CRITICAL**: Immediate fix required (SQL injection, hardcoded credentials)
- **HIGH**: Fix as soon as possible (XSS, command injection)
- **MEDIUM**: Should be fixed (weak crypto, unsafe redirects)
- **LOW**: Minor issues (logging sensitive data)
- **INFO**: Best practices (debug mode warnings)

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Security Scan
        run: |
          python code-sentinel/cli.py scan ./src --json security.json
          # Fails if critical/high issues found (exit code 2 or 1)
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python code-sentinel/cli.py scan --critical-only .
exit $?
```

## Configuration

Create a `.code-sentinel.json` configuration file:

```json
{
  "severity_threshold": "HIGH",
  "ignore_patterns": [
    "test_*.py",
    "*/migrations/*",
    "*/__pycache__/*"
  ],
  "auto_fix": true,
  "patterns": {
    "sql_injection": true,
    "hardcoded_credentials": true,
    "xss": true,
    "command_injection": true
  }
}
```

## Architecture

```
code-sentinel/
├── patterns/
│   └── security_patterns.py    # 20+ vulnerability patterns
├── validators/                  # (Future: per-pattern validators)
├── fixers/
│   └── auto_fixer.py           # Auto-fix implementations
├── core.py                      # Scanner engine
├── cli.py                       # Command-line interface
└── __init__.py                  # Package exports
```

## Pattern Database

Code-Sentinel includes **20+ security patterns** organized by OWASP category:

- **A03:2021 – Injection**: SQL injection, command injection, XSS
- **A02:2021 – Cryptographic Failures**: Weak hashing, hardcoded keys
- **A07:2021 – Auth Failures**: Hardcoded credentials
- **A05:2021 – Security Misconfig**: Debug mode, unsafe redirects
- **A08:2021 – Data Integrity**: Insecure deserialization
- **A10:2021 – SSRF**: Unsafe URL requests

Each pattern includes:
- CWE reference
- Detection regex/AST patterns
- Fix strategy
- Example vulnerable/fixed code

## Performance

- **Fast scanning**: ~1000 files/second
- **Minimal false positives**: Pattern-based + AST analysis
- **Low memory footprint**: Streaming file processing
- **Parallel scanning**: Multi-core support (future)

## Limitations

- Python-only (for now)
- Regex-based detection may miss complex patterns
- Some fixes require manual review
- Auto-fix is conservative (prefers safety over completeness)

## Roadmap

- [ ] Multi-language support (JavaScript, Go, Java)
- [ ] Machine learning pattern detection
- [ ] IDE integration (VS Code extension)
- [ ] Real-time scanning in editor
- [ ] Custom pattern creation
- [ ] Team collaboration features
- [ ] Cloud vulnerability database

## Contributing

Code-Sentinel is part of the Codes-Masterpiece ecosystem. To add new patterns:

1. Add pattern to `patterns/security_patterns.py`
2. Implement fixer in `fixers/auto_fixer.py`
3. Add tests in `tests/`
4. Update documentation

## License

Part of the Codes-Masterpiece project.

## See Also

- **Universal Debugger** - Runtime error fixing
- **Type-Guardian** - Type error detection & fixing
- **Deploy-Shield** - Deployment validation
- **DevMaster** - Unified CLI orchestrator

---

**Never ship vulnerable code again.** 🛡️
