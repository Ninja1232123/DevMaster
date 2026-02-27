"""
Code-Sentinel Security Patterns Database

This module contains a comprehensive database of security vulnerability patterns
based on OWASP Top 10 and common security anti-patterns.

Each pattern includes:
- Pattern name and category
- Detection regex/AST patterns
- Severity level (CRITICAL, HIGH, MEDIUM, LOW)
- CWE reference
- Fix strategy
- Example vulnerable code
- Example fixed code
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable


class Severity(Enum):
    """Severity levels for security vulnerabilities"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Category(Enum):
    """OWASP Top 10 + Additional Categories"""
    INJECTION = "A03:2021 – Injection"
    BROKEN_AUTH = "A07:2021 – Identification and Authentication Failures"
    SENSITIVE_DATA = "A02:2021 – Cryptographic Failures"
    XXE = "A05:2021 – Security Misconfiguration"
    BROKEN_ACCESS = "A01:2021 – Broken Access Control"
    SECURITY_MISCONFIG = "A05:2021 – Security Misconfiguration"
    XSS = "A03:2021 – Injection (XSS)"
    INSECURE_DESER = "A08:2021 – Software and Data Integrity Failures"
    VULNERABLE_COMPONENTS = "A06:2021 – Vulnerable and Outdated Components"
    LOGGING = "A09:2021 – Security Logging and Monitoring Failures"
    SSRF = "A10:2021 – Server-Side Request Forgery"
    PATH_TRAVERSAL = "Path Traversal"
    COMMAND_INJECTION = "Command Injection"
    CODE_INJECTION = "Code Injection"


@dataclass
class SecurityPattern:
    """Represents a security vulnerability pattern"""
    name: str
    category: Category
    severity: Severity
    cwe_id: str
    description: str
    regex_patterns: List[str]
    ast_check: Optional[Callable] = None
    fix_strategy: str = ""
    example_vulnerable: str = ""
    example_fixed: str = ""
    references: List[str] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []


# ============================================================================
# SQL INJECTION PATTERNS
# ============================================================================

SQL_INJECTION_PATTERNS = [
    SecurityPattern(
        name="sql_string_concatenation",
        category=Category.INJECTION,
        severity=Severity.CRITICAL,
        cwe_id="CWE-89",
        description="SQL query built with string concatenation or f-strings",
        regex_patterns=[
            r'execute\([^)]*[+%].*\)',
            r'execute\(f["\'].*\{.*\}.*["\']',
            r'cursor\.execute\([^)]*\+',
            r'\.execute\(.*\.format\(',
            r'executemany\([^)]*[+%]',
        ],
        fix_strategy="Use parameterized queries with ? or %s placeholders",
        example_vulnerable='''
query = "SELECT * FROM users WHERE username = '" + username + "'"
cursor.execute(query)
''',
        example_fixed='''
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
''',
        references=[
            "https://owasp.org/www-community/attacks/SQL_Injection",
            "https://cwe.mitre.org/data/definitions/89.html"
        ]
    ),
    SecurityPattern(
        name="orm_raw_query",
        category=Category.INJECTION,
        severity=Severity.HIGH,
        cwe_id="CWE-89",
        description="Django/SQLAlchemy raw query with string formatting",
        regex_patterns=[
            r'\.raw\([^)]*[+%]',
            r'\.raw\(f["\']',
            r'session\.execute\([^)]*[+%]',
            r'session\.execute\(f["\']',
        ],
        fix_strategy="Use ORM query builders or parameterized raw queries",
        example_vulnerable='''
User.objects.raw(f"SELECT * FROM users WHERE id = {user_id}")
''',
        example_fixed='''
User.objects.raw("SELECT * FROM users WHERE id = %s", [user_id])
''',
    ),
]

# ============================================================================
# HARDCODED CREDENTIALS PATTERNS
# ============================================================================

CREDENTIAL_PATTERNS = [
    SecurityPattern(
        name="hardcoded_password",
        category=Category.SENSITIVE_DATA,
        severity=Severity.CRITICAL,
        cwe_id="CWE-798",
        description="Hardcoded password, API key, or secret in source code",
        regex_patterns=[
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'api_key\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
            r'secret\s*=\s*["\'][^"\']{16,}["\']',
            r'token\s*=\s*["\'][A-Za-z0-9\-_]{20,}["\']',
            r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']',
            r'private_key\s*=\s*["\'].*BEGIN.*PRIVATE.*KEY',
        ],
        fix_strategy="Load credentials from environment variables or secure vault",
        example_vulnerable='''
API_KEY = "sk_live_51HqJ8k2eZvKYlo2C9dPJ0Qx"
password = "SuperSecret123!"
''',
        example_fixed='''
import os
API_KEY = os.environ.get("API_KEY")
password = os.environ.get("DB_PASSWORD")
''',
        references=[
            "https://cwe.mitre.org/data/definitions/798.html"
        ]
    ),
    SecurityPattern(
        name="hardcoded_database_uri",
        category=Category.SENSITIVE_DATA,
        severity=Severity.HIGH,
        cwe_id="CWE-798",
        description="Database connection string with embedded credentials",
        regex_patterns=[
            r'://[^:]+:[^@]+@',  # user:pass@host pattern
            r'postgresql://.*:.*@',
            r'mysql://.*:.*@',
            r'mongodb://.*:.*@',
        ],
        fix_strategy="Use environment variables for database URIs",
        example_vulnerable='''
DATABASE_URL = "postgresql://admin:secret123@localhost/mydb"
''',
        example_fixed='''
import os
DATABASE_URL = os.environ.get("DATABASE_URL")
''',
    ),
]

# ============================================================================
# CROSS-SITE SCRIPTING (XSS) PATTERNS
# ============================================================================

XSS_PATTERNS = [
    SecurityPattern(
        name="unsafe_html_rendering",
        category=Category.XSS,
        severity=Severity.HIGH,
        cwe_id="CWE-79",
        description="Rendering user input as HTML without escaping",
        regex_patterns=[
            r'\.innerHTML\s*=',
            r'Markup\([^)]*\)',
            r'safe_join\(',
            r'mark_safe\(',
            r'\.render_template_string\([^)]*[+%]',
        ],
        fix_strategy="Use auto-escaping template engines or explicit escaping",
        example_vulnerable='''
from flask import Markup
return Markup(f"<div>{user_input}</div>")
''',
        example_fixed='''
from markupsafe import escape
return f"<div>{escape(user_input)}</div>"
''',
        references=[
            "https://owasp.org/www-community/attacks/xss/",
            "https://cwe.mitre.org/data/definitions/79.html"
        ]
    ),
    SecurityPattern(
        name="unsafe_redirect",
        category=Category.XSS,
        severity=Severity.MEDIUM,
        cwe_id="CWE-601",
        description="Unvalidated redirect using user input",
        regex_patterns=[
            r'redirect\(request\.',
            r'redirect\(.*get\(["\']',
            r'HttpResponseRedirect\(request\.',
        ],
        fix_strategy="Validate redirect URLs against whitelist",
        example_vulnerable='''
return redirect(request.args.get("next"))
''',
        example_fixed='''
ALLOWED_REDIRECTS = ["/dashboard", "/profile"]
next_url = request.args.get("next", "/")
if next_url in ALLOWED_REDIRECTS:
    return redirect(next_url)
return redirect("/")
''',
    ),
]

# ============================================================================
# COMMAND INJECTION PATTERNS
# ============================================================================

COMMAND_INJECTION_PATTERNS = [
    SecurityPattern(
        name="shell_command_concatenation",
        category=Category.COMMAND_INJECTION,
        severity=Severity.CRITICAL,
        cwe_id="CWE-78",
        description="Shell command with user input concatenation",
        regex_patterns=[
            r'os\.system\([^)]*[+%]',
            r'os\.system\(f["\']',
            r'subprocess\..*shell\s*=\s*True',
            r'os\.popen\([^)]*[+%]',
            r'commands\.getoutput\(',
        ],
        fix_strategy="Use subprocess with shell=False and argument list",
        example_vulnerable='''
os.system(f"ping {user_input}")
''',
        example_fixed='''
import subprocess
subprocess.run(["ping", "-c", "1", user_input], check=True)
''',
        references=[
            "https://cwe.mitre.org/data/definitions/78.html"
        ]
    ),
]

# ============================================================================
# PATH TRAVERSAL PATTERNS
# ============================================================================

PATH_TRAVERSAL_PATTERNS = [
    SecurityPattern(
        name="unsafe_file_path",
        category=Category.PATH_TRAVERSAL,
        severity=Severity.HIGH,
        cwe_id="CWE-22",
        description="File path built with user input without validation",
        regex_patterns=[
            r'open\([^)]*[+%].*["\']r',
            r'open\(f["\'].*\{',
            r'Path\([^)]*[+%]',
            r'os\.path\.join\(.*request\.',
        ],
        fix_strategy="Validate paths and use os.path.abspath/realpath",
        example_vulnerable='''
filename = request.args.get("file")
with open(f"/data/{filename}", "r") as f:
    content = f.read()
''',
        example_fixed='''
import os
filename = request.args.get("file")
base_dir = "/data"
filepath = os.path.realpath(os.path.join(base_dir, filename))
if not filepath.startswith(base_dir):
    raise ValueError("Invalid file path")
with open(filepath, "r") as f:
    content = f.read()
''',
    ),
]

# ============================================================================
# INSECURE DESERIALIZATION PATTERNS
# ============================================================================

DESERIALIZATION_PATTERNS = [
    SecurityPattern(
        name="pickle_unsafe_load",
        category=Category.INSECURE_DESER,
        severity=Severity.CRITICAL,
        cwe_id="CWE-502",
        description="Using pickle.load on untrusted data",
        regex_patterns=[
            r'pickle\.loads?\(',
            r'yaml\.load\([^,)]*\)',  # yaml.load without Loader
            r'marshal\.loads?\(',
        ],
        fix_strategy="Use JSON or yaml.safe_load for untrusted data",
        example_vulnerable='''
import pickle
data = pickle.loads(user_input)
''',
        example_fixed='''
import json
data = json.loads(user_input)
''',
        references=[
            "https://cwe.mitre.org/data/definitions/502.html"
        ]
    ),
    SecurityPattern(
        name="yaml_unsafe_load",
        category=Category.INSECURE_DESER,
        severity=Severity.HIGH,
        cwe_id="CWE-502",
        description="Using yaml.load instead of yaml.safe_load",
        regex_patterns=[
            r'yaml\.load\([^,)]*\)',
        ],
        fix_strategy="Use yaml.safe_load instead of yaml.load",
        example_vulnerable='''
import yaml
config = yaml.load(file)
''',
        example_fixed='''
import yaml
config = yaml.safe_load(file)
''',
    ),
]

# ============================================================================
# WEAK CRYPTOGRAPHY PATTERNS
# ============================================================================

CRYPTO_PATTERNS = [
    SecurityPattern(
        name="weak_hash_algorithm",
        category=Category.SENSITIVE_DATA,
        severity=Severity.HIGH,
        cwe_id="CWE-327",
        description="Using weak hash algorithms (MD5, SHA1)",
        regex_patterns=[
            r'hashlib\.md5\(',
            r'hashlib\.sha1\(',
            r'Crypto\.Hash\.MD5',
            r'Crypto\.Hash\.SHA1',
        ],
        fix_strategy="Use SHA-256 or bcrypt for password hashing",
        example_vulnerable='''
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
''',
        example_fixed='''
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
''',
        references=[
            "https://cwe.mitre.org/data/definitions/327.html"
        ]
    ),
    SecurityPattern(
        name="hardcoded_crypto_key",
        category=Category.SENSITIVE_DATA,
        severity=Severity.CRITICAL,
        cwe_id="CWE-321",
        description="Hardcoded encryption key or IV",
        regex_patterns=[
            r'AES\.new\([^)]*["\'][^"\']{16,}["\']',
            r'Cipher\([^)]*key\s*=\s*["\']',
        ],
        fix_strategy="Generate keys securely and store in environment",
        example_vulnerable='''
key = b"hardcoded_key123"
cipher = AES.new(key, AES.MODE_CBC)
''',
        example_fixed='''
import os
key = os.environ.get("ENCRYPTION_KEY").encode()
cipher = AES.new(key, AES.MODE_CBC)
''',
    ),
]

# ============================================================================
# LOGGING SENSITIVE DATA PATTERNS
# ============================================================================

LOGGING_PATTERNS = [
    SecurityPattern(
        name="logging_sensitive_data",
        category=Category.LOGGING,
        severity=Severity.MEDIUM,
        cwe_id="CWE-532",
        description="Logging potentially sensitive data",
        regex_patterns=[
            r'log.*password',
            r'log.*token',
            r'log.*secret',
            r'log.*api_key',
            r'print\(.*password',
        ],
        fix_strategy="Sanitize or redact sensitive data before logging",
        example_vulnerable='''
logger.info(f"User logged in with password: {password}")
''',
        example_fixed='''
logger.info("User logged in successfully")
''',
    ),
]

# ============================================================================
# SSRF PATTERNS
# ============================================================================

SSRF_PATTERNS = [
    SecurityPattern(
        name="unsafe_url_request",
        category=Category.SSRF,
        severity=Severity.HIGH,
        cwe_id="CWE-918",
        description="Making HTTP request with user-controlled URL",
        regex_patterns=[
            r'requests\.(get|post|put|delete)\([^)]*request\.',
            r'urllib\.request\.urlopen\([^)]*request\.',
            r'httpx\.(get|post)\([^)]*request\.',
        ],
        fix_strategy="Validate URLs against whitelist of allowed domains",
        example_vulnerable='''
url = request.args.get("url")
response = requests.get(url)
''',
        example_fixed='''
from urllib.parse import urlparse

ALLOWED_DOMAINS = ["api.example.com", "cdn.example.com"]
url = request.args.get("url")
parsed = urlparse(url)
if parsed.netloc not in ALLOWED_DOMAINS:
    raise ValueError("Invalid domain")
response = requests.get(url)
''',
    ),
]

# ============================================================================
# DEBUG/DEVELOPMENT MODE PATTERNS
# ============================================================================

DEBUG_PATTERNS = [
    SecurityPattern(
        name="debug_mode_enabled",
        category=Category.SECURITY_MISCONFIG,
        severity=Severity.MEDIUM,
        cwe_id="CWE-489",
        description="Debug mode enabled in production",
        regex_patterns=[
            r'DEBUG\s*=\s*True',
            r'app\.debug\s*=\s*True',
            r'app\.run\([^)]*debug\s*=\s*True',
        ],
        fix_strategy="Use environment variable for DEBUG setting",
        example_vulnerable='''
DEBUG = True
''',
        example_fixed='''
import os
DEBUG = os.environ.get("DEBUG", "False") == "True"
''',
    ),
]

# ============================================================================
# MASTER PATTERN DATABASE
# ============================================================================

SECURITY_PATTERNS: Dict[str, List[SecurityPattern]] = {
    "sql_injection": SQL_INJECTION_PATTERNS,
    "credentials": CREDENTIAL_PATTERNS,
    "xss": XSS_PATTERNS,
    "command_injection": COMMAND_INJECTION_PATTERNS,
    "path_traversal": PATH_TRAVERSAL_PATTERNS,
    "deserialization": DESERIALIZATION_PATTERNS,
    "crypto": CRYPTO_PATTERNS,
    "logging": LOGGING_PATTERNS,
    "ssrf": SSRF_PATTERNS,
    "debug": DEBUG_PATTERNS,
}

# Flatten all patterns for easy iteration
ALL_PATTERNS = []
for pattern_list in SECURITY_PATTERNS.values():
    ALL_PATTERNS.extend(pattern_list)


def get_patterns_by_severity(severity: Severity) -> List[SecurityPattern]:
    """Get all patterns matching a severity level"""
    return [p for p in ALL_PATTERNS if p.severity == severity]


def get_patterns_by_category(category: Category) -> List[SecurityPattern]:
    """Get all patterns matching a category"""
    return [p for p in ALL_PATTERNS if p.category == category]


def get_pattern_by_name(name: str) -> Optional[SecurityPattern]:
    """Get a specific pattern by name"""
    for pattern in ALL_PATTERNS:
        if pattern.name == name:
            return pattern
    return None
