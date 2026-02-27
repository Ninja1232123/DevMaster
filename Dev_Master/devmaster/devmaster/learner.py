"""
Persistent Coding Learner - Learns your coding style and patterns.

The brain of DevMaster that observes how you code and builds a model
of your preferences, habits, strengths, and areas for improvement.

Features:
- Analyzes your code commits over time
- Learns naming conventions, patterns, preferences
- Tracks error patterns and what you struggle with
- Builds a profile of your coding style
- Stores everything persistently in SQLite
"""

import ast
import hashlib
import json
import os
import re
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class CodingPattern:
    """A detected coding pattern."""
    pattern_type: str  # 'naming', 'structure', 'style', 'error', 'preference'
    name: str
    description: str
    frequency: int
    examples: list
    first_seen: str
    last_seen: str
    confidence: float  # 0-1, how confident we are this is a real pattern


@dataclass
class CodingInsight:
    """An insight about the developer's coding style."""
    category: str  # 'strength', 'weakness', 'habit', 'preference', 'growth'
    title: str
    description: str
    evidence: list  # Examples that support this insight
    actionable: bool
    suggestion: Optional[str]
    created_at: str


@dataclass
class ProgressMetric:
    """A metric tracking coding improvement over time."""
    metric_name: str
    current_value: float
    previous_value: float
    change_percent: float
    trend: str  # 'improving', 'stable', 'declining'
    period: str  # 'week', 'month', 'quarter'


class CodingLearner:
    """
    Persistent coding learner that lives in your environment.

    Analyzes your code, learns your patterns, and helps you improve.
    """

    def __init__(self, db_path: str = "~/.devmaster/learner.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

        # Pattern detectors
        self.pattern_detectors = {
            'naming': self._analyze_naming_patterns,
            'structure': self._analyze_structure_patterns,
            'error_prone': self._analyze_error_patterns,
            'style': self._analyze_style_patterns,
            'complexity': self._analyze_complexity_patterns,
        }

    def _init_db(self):
        """Initialize the learning database."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        self.conn.executescript("""
            -- Coding sessions (each time you code)
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_path TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                files_changed INTEGER DEFAULT 0,
                lines_added INTEGER DEFAULT 0,
                lines_removed INTEGER DEFAULT 0,
                commits INTEGER DEFAULT 0
            );

            -- Detected patterns
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                frequency INTEGER DEFAULT 1,
                examples TEXT,  -- JSON array
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence REAL DEFAULT 0.5,
                UNIQUE(pattern_type, name)
            );

            -- Generated insights
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                evidence TEXT,  -- JSON array
                actionable BOOLEAN DEFAULT 0,
                suggestion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT 0
            );

            -- Error history (what errors you make)
            CREATE TABLE IF NOT EXISTS error_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                error_message TEXT,
                file_path TEXT,
                line_number INTEGER,
                code_context TEXT,
                fixed BOOLEAN DEFAULT 0,
                fix_applied TEXT,
                occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Progress metrics over time
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Code snapshots for learning
            CREATE TABLE IF NOT EXISTS code_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                language TEXT,
                metrics TEXT,  -- JSON object with code metrics
                patterns_found TEXT,  -- JSON array
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_path, content_hash)
            );

            -- Your preferences (learned over time)
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT,
                confidence REAL DEFAULT 0.5,
                evidence_count INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, preference_key)
            );

            -- Indexes
            CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
            CREATE INDEX IF NOT EXISTS idx_insights_category ON insights(category);
            CREATE INDEX IF NOT EXISTS idx_errors_type ON error_history(error_type);
            CREATE INDEX IF NOT EXISTS idx_progress_metric ON progress(metric_name);
        """)

        self.conn.commit()

    def learn_from_repo(self, repo_path: str, days: int = 30) -> dict:
        """
        Learn from a repository's code and history.

        Analyzes:
        - Current code patterns
        - Git history for evolution
        - Error patterns from debug history
        """
        repo = Path(repo_path).resolve()
        if not repo.exists():
            raise FileNotFoundError(f"Repository not found: {repo}")

        results = {
            'files_analyzed': 0,
            'patterns_found': 0,
            'insights_generated': 0,
            'preferences_learned': 0,
        }

        # Start a learning session
        session_id = self._start_session(str(repo))

        # Analyze current code
        for py_file in repo.rglob("*.py"):
            # Skip common exclusions
            if any(part in py_file.parts for part in ['venv', 'node_modules', '__pycache__', '.git']):
                continue

            try:
                self._analyze_file(py_file)
                results['files_analyzed'] += 1
            except Exception as e:
                pass  # Skip files that can't be analyzed

        # Analyze git history
        self._analyze_git_history(repo, days)

        # Generate insights from patterns
        insights = self._generate_insights()
        results['insights_generated'] = len(insights)

        # Learn preferences
        prefs = self._learn_preferences()
        results['preferences_learned'] = len(prefs)

        # Count patterns
        cursor = self.conn.execute("SELECT COUNT(*) FROM patterns")
        results['patterns_found'] = cursor.fetchone()[0]

        # End session
        self._end_session(session_id, results['files_analyzed'])

        return results

    def _start_session(self, repo_path: str) -> int:
        """Start a learning session."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (repo_path) VALUES (?)",
            (repo_path,)
        )
        self.conn.commit()
        return cursor.lastrowid

    def _end_session(self, session_id: int, files_changed: int):
        """End a learning session."""
        self.conn.execute(
            "UPDATE sessions SET ended_at = CURRENT_TIMESTAMP, files_changed = ? WHERE id = ?",
            (files_changed, session_id)
        )
        self.conn.commit()

    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file for patterns."""
        try:
            content = file_path.read_text(encoding='utf-8')
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

            # Check if already analyzed
            cursor = self.conn.execute(
                "SELECT id FROM code_snapshots WHERE file_path = ? AND content_hash = ?",
                (str(file_path), content_hash)
            )
            if cursor.fetchone():
                return  # Already analyzed this version

            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return  # Skip files with syntax errors

            # Run all pattern detectors
            all_patterns = []
            metrics = {}

            for detector_name, detector_func in self.pattern_detectors.items():
                patterns = detector_func(content, tree, str(file_path))
                all_patterns.extend(patterns)

            # Calculate metrics
            metrics = self._calculate_metrics(content, tree)

            # Store patterns
            for pattern in all_patterns:
                self._store_pattern(pattern)

            # Store snapshot
            self.conn.execute(
                """
                INSERT OR REPLACE INTO code_snapshots
                (file_path, content_hash, language, metrics, patterns_found)
                VALUES (?, ?, ?, ?, ?)
                """,
                (str(file_path), content_hash, 'python',
                 json.dumps(metrics), json.dumps([p['name'] for p in all_patterns]))
            )
            self.conn.commit()

        except Exception as e:
            pass  # Skip problematic files

    def _analyze_naming_patterns(self, content: str, tree: ast.AST, file_path: str) -> list:
        """Analyze naming conventions used."""
        patterns = []

        # Collect all names
        function_names = []
        class_names = []
        variable_names = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)
            elif isinstance(node, ast.ClassDef):
                class_names.append(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                variable_names.append(node.id)

        # Detect function naming style
        if function_names:
            snake_case = sum(1 for n in function_names if re.match(r'^[a-z_][a-z0-9_]*$', n))
            camel_case = sum(1 for n in function_names if re.match(r'^[a-z][a-zA-Z0-9]*$', n) and '_' not in n)

            if snake_case > camel_case:
                patterns.append({
                    'type': 'naming',
                    'name': 'snake_case_functions',
                    'description': 'Uses snake_case for function names (Pythonic)',
                    'examples': function_names[:5],
                    'confidence': snake_case / len(function_names) if function_names else 0
                })
            elif camel_case > snake_case:
                patterns.append({
                    'type': 'naming',
                    'name': 'camelCase_functions',
                    'description': 'Uses camelCase for function names (non-Pythonic)',
                    'examples': function_names[:5],
                    'confidence': camel_case / len(function_names) if function_names else 0
                })

        # Detect variable naming patterns
        if variable_names:
            single_letter = sum(1 for n in variable_names if len(n) == 1)
            descriptive = sum(1 for n in variable_names if len(n) > 5)

            if single_letter > len(variable_names) * 0.3:
                patterns.append({
                    'type': 'naming',
                    'name': 'single_letter_vars',
                    'description': 'Frequently uses single-letter variable names',
                    'examples': [n for n in variable_names if len(n) == 1][:10],
                    'confidence': single_letter / len(variable_names)
                })

            if descriptive > len(variable_names) * 0.5:
                patterns.append({
                    'type': 'naming',
                    'name': 'descriptive_vars',
                    'description': 'Uses descriptive variable names (good practice)',
                    'examples': [n for n in variable_names if len(n) > 5][:10],
                    'confidence': descriptive / len(variable_names)
                })

        return patterns

    def _analyze_structure_patterns(self, content: str, tree: ast.AST, file_path: str) -> list:
        """Analyze code structure patterns."""
        patterns = []

        # Count different structures
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        # Function length analysis
        long_functions = []
        for func in functions:
            func_lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 0
            if func_lines > 50:
                long_functions.append(func.name)

        if long_functions:
            patterns.append({
                'type': 'structure',
                'name': 'long_functions',
                'description': f'Has functions over 50 lines (consider refactoring)',
                'examples': long_functions[:5],
                'confidence': len(long_functions) / len(functions) if functions else 0
            })

        # Class usage
        if classes and not functions:
            patterns.append({
                'type': 'structure',
                'name': 'class_heavy',
                'description': 'Prefers class-based design',
                'examples': [c.name for c in classes[:5]],
                'confidence': 0.8
            })
        elif functions and not classes:
            patterns.append({
                'type': 'structure',
                'name': 'functional_style',
                'description': 'Prefers functional programming style',
                'examples': [f.name for f in functions[:5]],
                'confidence': 0.8
            })

        # Docstring usage
        documented = sum(1 for f in functions if ast.get_docstring(f))
        if functions:
            doc_ratio = documented / len(functions)
            if doc_ratio > 0.8:
                patterns.append({
                    'type': 'structure',
                    'name': 'well_documented',
                    'description': 'Consistently documents functions (excellent practice)',
                    'examples': [f.name for f in functions if ast.get_docstring(f)][:5],
                    'confidence': doc_ratio
                })
            elif doc_ratio < 0.2:
                patterns.append({
                    'type': 'structure',
                    'name': 'minimal_docs',
                    'description': 'Rarely documents functions (consider adding docstrings)',
                    'examples': [f.name for f in functions if not ast.get_docstring(f)][:5],
                    'confidence': 1 - doc_ratio
                })

        return patterns

    def _analyze_error_patterns(self, content: str, tree: ast.AST, file_path: str) -> list:
        """Analyze patterns that commonly lead to errors."""
        patterns = []

        # Check for bare excepts
        bare_excepts = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                bare_excepts.append(f"Line {node.lineno}")

        if bare_excepts:
            patterns.append({
                'type': 'error_prone',
                'name': 'bare_except',
                'description': 'Uses bare except clauses (catches all exceptions including KeyboardInterrupt)',
                'examples': bare_excepts[:5],
                'confidence': 0.9
            })

        # Check for mutable default arguments
        mutable_defaults = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        mutable_defaults.append(node.name)

        if mutable_defaults:
            patterns.append({
                'type': 'error_prone',
                'name': 'mutable_default_args',
                'description': 'Uses mutable default arguments (common Python gotcha)',
                'examples': mutable_defaults[:5],
                'confidence': 0.95
            })

        # Check for potential None access
        none_comparisons = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                for op in node.ops:
                    if isinstance(op, (ast.Is, ast.IsNot)):
                        none_comparisons.append(f"Line {node.lineno}")

        if none_comparisons:
            patterns.append({
                'type': 'style',
                'name': 'proper_none_check',
                'description': 'Uses "is None" instead of "== None" (correct style)',
                'examples': none_comparisons[:5],
                'confidence': 0.9
            })

        return patterns

    def _analyze_style_patterns(self, content: str, tree: ast.AST, file_path: str) -> list:
        """Analyze coding style patterns."""
        patterns = []
        lines = content.split('\n')

        # Line length
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            patterns.append({
                'type': 'style',
                'name': 'long_lines',
                'description': f'Has {len(long_lines)} lines over 100 characters',
                'examples': [f"Line {l}" for l in long_lines[:5]],
                'confidence': len(long_lines) / len(lines) if lines else 0
            })

        # F-string usage vs format
        f_strings = len(re.findall(r'f["\']', content))
        format_calls = len(re.findall(r'\.format\(', content))
        percent_format = len(re.findall(r'%\s*\(', content))

        if f_strings > format_calls + percent_format:
            patterns.append({
                'type': 'style',
                'name': 'modern_f_strings',
                'description': 'Prefers f-strings (modern Python style)',
                'examples': [],
                'confidence': 0.85
            })
        elif format_calls > f_strings:
            patterns.append({
                'type': 'style',
                'name': 'format_method',
                'description': 'Uses .format() method (consider f-strings)',
                'examples': [],
                'confidence': 0.7
            })

        # Type hints
        type_hints = len(re.findall(r'def \w+\([^)]*:\s*\w+', content))
        all_funcs = len(re.findall(r'def \w+\(', content))

        if all_funcs > 0:
            hint_ratio = type_hints / all_funcs
            if hint_ratio > 0.7:
                patterns.append({
                    'type': 'style',
                    'name': 'type_hints',
                    'description': 'Uses type hints consistently (excellent for maintainability)',
                    'examples': [],
                    'confidence': hint_ratio
                })

        return patterns

    def _analyze_complexity_patterns(self, content: str, tree: ast.AST, file_path: str) -> list:
        """Analyze code complexity patterns."""
        patterns = []

        # Nested depth analysis
        max_depth = 0

        def get_depth(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    get_depth(child, current_depth + 1)
                else:
                    get_depth(child, current_depth)

        get_depth(tree)

        if max_depth > 4:
            patterns.append({
                'type': 'complexity',
                'name': 'deep_nesting',
                'description': f'Has deep nesting (max depth: {max_depth}). Consider refactoring.',
                'examples': [],
                'confidence': 0.9
            })

        return patterns

    def _calculate_metrics(self, content: str, tree: ast.AST) -> dict:
        """Calculate code metrics for a file."""
        lines = content.split('\n')

        return {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            'classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            'imports': len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]),
        }

    def _store_pattern(self, pattern: dict):
        """Store or update a detected pattern."""
        cursor = self.conn.cursor()

        # Check if pattern exists
        cursor.execute(
            "SELECT id, frequency, examples FROM patterns WHERE pattern_type = ? AND name = ?",
            (pattern['type'], pattern['name'])
        )
        existing = cursor.fetchone()

        if existing:
            # Update frequency and examples
            old_examples = json.loads(existing['examples'] or '[]')
            new_examples = list(set(old_examples + pattern.get('examples', [])))[:20]

            cursor.execute(
                """
                UPDATE patterns
                SET frequency = frequency + 1,
                    examples = ?,
                    last_seen = CURRENT_TIMESTAMP,
                    confidence = (confidence + ?) / 2
                WHERE id = ?
                """,
                (json.dumps(new_examples), pattern.get('confidence', 0.5), existing['id'])
            )
        else:
            # Insert new pattern
            cursor.execute(
                """
                INSERT INTO patterns (pattern_type, name, description, examples, confidence)
                VALUES (?, ?, ?, ?, ?)
                """,
                (pattern['type'], pattern['name'], pattern.get('description', ''),
                 json.dumps(pattern.get('examples', [])), pattern.get('confidence', 0.5))
            )

        self.conn.commit()

    def _analyze_git_history(self, repo_path: Path, days: int):
        """Analyze git history for patterns."""
        try:
            # Get recent commits
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            result = subprocess.run(
                ['git', 'log', f'--since={since_date}', '--oneline', '--numstat'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return

            # Parse commit stats
            lines_added = 0
            lines_removed = 0
            files_changed = set()
            commits = 0

            for line in result.stdout.split('\n'):
                if re.match(r'^[a-f0-9]+\s+', line):
                    commits += 1
                elif re.match(r'^\d+\s+\d+\s+', line):
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            lines_added += int(parts[0])
                            lines_removed += int(parts[1])
                            files_changed.add(parts[2])
                        except ValueError:
                            pass

            # Record progress metrics
            self._record_metric('commits_per_period', commits)
            self._record_metric('lines_added_per_period', lines_added)
            self._record_metric('lines_removed_per_period', lines_removed)
            self._record_metric('files_touched_per_period', len(files_changed))

            # Analyze churn ratio
            if lines_added > 0:
                churn_ratio = lines_removed / lines_added
                self._record_metric('churn_ratio', churn_ratio)

        except Exception:
            pass

    def _record_metric(self, name: str, value: float):
        """Record a progress metric."""
        self.conn.execute(
            "INSERT INTO progress (metric_name, value) VALUES (?, ?)",
            (name, value)
        )
        self.conn.commit()

    def _generate_insights(self) -> list:
        """Generate insights from detected patterns."""
        insights = []

        # Get patterns with high frequency/confidence
        cursor = self.conn.execute(
            """
            SELECT * FROM patterns
            WHERE frequency > 3 AND confidence > 0.6
            ORDER BY frequency DESC
            """
        )

        for row in cursor.fetchall():
            pattern_type = row['pattern_type']
            name = row['name']

            # Generate insight based on pattern type
            insight = None

            if pattern_type == 'error_prone':
                insight = {
                    'category': 'weakness',
                    'title': f"Potential Issue: {name.replace('_', ' ').title()}",
                    'description': row['description'],
                    'evidence': json.loads(row['examples'] or '[]'),
                    'actionable': True,
                    'suggestion': self._get_suggestion(name)
                }
            elif pattern_type == 'style' and 'modern' in name or 'well' in name or 'proper' in name:
                insight = {
                    'category': 'strength',
                    'title': f"Good Practice: {name.replace('_', ' ').title()}",
                    'description': row['description'],
                    'evidence': json.loads(row['examples'] or '[]'),
                    'actionable': False,
                    'suggestion': None
                }
            elif pattern_type == 'naming':
                insight = {
                    'category': 'preference',
                    'title': f"Style Preference: {name.replace('_', ' ').title()}",
                    'description': row['description'],
                    'evidence': json.loads(row['examples'] or '[]'),
                    'actionable': False,
                    'suggestion': None
                }

            if insight:
                self._store_insight(insight)
                insights.append(insight)

        return insights

    def _get_suggestion(self, pattern_name: str) -> str:
        """Get improvement suggestion for a pattern."""
        suggestions = {
            'bare_except': "Replace bare 'except:' with specific exceptions like 'except ValueError:' or 'except Exception as e:'",
            'mutable_default_args': "Use None as default and initialize inside function: def func(items=None): items = items or []",
            'long_functions': "Consider breaking into smaller functions. Each function should do one thing well.",
            'deep_nesting': "Extract nested logic into separate functions or use early returns to reduce nesting.",
            'long_lines': "Break long lines using parentheses or backslash. Consider extracting complex expressions.",
            'minimal_docs': "Add docstrings to your functions explaining what they do, their parameters, and return values.",
            'single_letter_vars': "Use descriptive variable names that explain their purpose. 'user_count' is better than 'n'.",
        }
        return suggestions.get(pattern_name, "Review this pattern and consider improvements.")

    def _store_insight(self, insight: dict):
        """Store a generated insight."""
        self.conn.execute(
            """
            INSERT INTO insights (category, title, description, evidence, actionable, suggestion)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (insight['category'], insight['title'], insight['description'],
             json.dumps(insight['evidence']), insight['actionable'], insight.get('suggestion'))
        )
        self.conn.commit()

    def _learn_preferences(self) -> list:
        """Learn coding preferences from patterns."""
        preferences = []

        # Analyze naming preference
        cursor = self.conn.execute(
            "SELECT name, confidence FROM patterns WHERE pattern_type = 'naming' ORDER BY confidence DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            self._store_preference('naming', 'function_style', row['name'], row['confidence'])
            preferences.append(('naming', 'function_style', row['name']))

        # Analyze structure preference
        cursor = self.conn.execute(
            "SELECT name, confidence FROM patterns WHERE pattern_type = 'structure' AND name IN ('class_heavy', 'functional_style') ORDER BY confidence DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            self._store_preference('structure', 'paradigm', row['name'], row['confidence'])
            preferences.append(('structure', 'paradigm', row['name']))

        return preferences

    def _store_preference(self, category: str, key: str, value: str, confidence: float):
        """Store a learned preference."""
        self.conn.execute(
            """
            INSERT OR REPLACE INTO preferences (category, preference_key, preference_value, confidence, evidence_count)
            VALUES (?, ?, ?, ?, COALESCE(
                (SELECT evidence_count + 1 FROM preferences WHERE category = ? AND preference_key = ?), 1
            ))
            """,
            (category, key, value, confidence, category, key)
        )
        self.conn.commit()

    def get_insights(self, category: Optional[str] = None, limit: int = 10) -> list:
        """Get generated insights."""
        sql = "SELECT * FROM insights WHERE acknowledged = 0"
        params = []

        if category:
            sql += " AND category = ?"
            params.append(category)

        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(sql, params)

        return [
            CodingInsight(
                category=row['category'],
                title=row['title'],
                description=row['description'],
                evidence=json.loads(row['evidence'] or '[]'),
                actionable=bool(row['actionable']),
                suggestion=row['suggestion'],
                created_at=row['created_at']
            )
            for row in cursor.fetchall()
        ]

    def get_patterns(self, pattern_type: Optional[str] = None) -> list:
        """Get detected patterns."""
        sql = "SELECT * FROM patterns"
        params = []

        if pattern_type:
            sql += " WHERE pattern_type = ?"
            params.append(pattern_type)

        sql += " ORDER BY frequency DESC, confidence DESC"

        cursor = self.conn.execute(sql, params)

        return [
            CodingPattern(
                pattern_type=row['pattern_type'],
                name=row['name'],
                description=row['description'],
                frequency=row['frequency'],
                examples=json.loads(row['examples'] or '[]'),
                first_seen=row['first_seen'],
                last_seen=row['last_seen'],
                confidence=row['confidence']
            )
            for row in cursor.fetchall()
        ]

    def get_preferences(self) -> dict:
        """Get learned preferences."""
        cursor = self.conn.execute(
            "SELECT category, preference_key, preference_value, confidence FROM preferences ORDER BY confidence DESC"
        )

        prefs = defaultdict(dict)
        for row in cursor.fetchall():
            prefs[row['category']][row['preference_key']] = {
                'value': row['preference_value'],
                'confidence': row['confidence']
            }

        return dict(prefs)

    def get_progress(self, metric_name: str, periods: int = 10) -> list:
        """Get progress metrics over time."""
        cursor = self.conn.execute(
            """
            SELECT value, recorded_at FROM progress
            WHERE metric_name = ?
            ORDER BY recorded_at DESC
            LIMIT ?
            """,
            (metric_name, periods)
        )

        return [(row['value'], row['recorded_at']) for row in cursor.fetchall()]

    def record_error(self, error_type: str, error_message: str, file_path: str = None,
                    line_number: int = None, code_context: str = None):
        """Record an error occurrence for learning."""
        self.conn.execute(
            """
            INSERT INTO error_history (error_type, error_message, file_path, line_number, code_context)
            VALUES (?, ?, ?, ?, ?)
            """,
            (error_type, error_message, file_path, line_number, code_context)
        )
        self.conn.commit()

        # Check if this is a recurring pattern and publish to nervous system
        self._check_and_publish_error_pattern(error_type, error_message, code_context)

    def _check_and_publish_error_pattern(self, error_type: str, error_message: str, code_context: str = None):
        """Check if error is recurring and publish to nervous system."""
        # Count occurrences of this error type
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM error_history WHERE error_type = ?",
            (error_type,)
        )
        count = cursor.fetchone()['count']

        # If we've seen this error 3+ times, publish to nervous system
        if count >= 3:
            try:
                from .nervous_system import publish_error_pattern

                # Try to extract a pattern from the error
                pattern = self._extract_error_pattern(error_type, error_message, code_context)
                fix_suggestion = self._suggest_fix(error_type, pattern)

                publish_error_pattern(
                    error_type=error_type,
                    pattern=pattern or error_message[:100],
                    fix_suggestion=fix_suggestion or "Review error context",
                    frequency=count
                )
            except ImportError:
                pass  # Nervous system not available

    def _extract_error_pattern(self, error_type: str, message: str, context: str = None) -> str:
        """Try to extract a regex pattern from the error."""
        # Common patterns
        if error_type == 'KeyError':
            match = re.search(r"KeyError: ['\"](\w+)['\"]", message)
            if match:
                return rf"data\[['\"]?\w+['\"]?\]"

        if error_type == 'AttributeError':
            match = re.search(r"'(\w+)' object has no attribute '(\w+)'", message)
            if match:
                return rf"\.{match.group(2)}\b"

        if error_type == 'TypeError':
            if 'NoneType' in message:
                return r"\w+\.\w+\("

        return message[:50] if message else ""

    def _suggest_fix(self, error_type: str, pattern: str) -> str:
        """Suggest a fix based on error type."""
        suggestions = {
            'KeyError': "Use .get() with a default value",
            'AttributeError': "Add None check before accessing attribute",
            'TypeError': "Validate input types before operation",
            'IndexError': "Check list length before accessing index",
            'ZeroDivisionError': "Add zero check before division",
            'ValueError': "Validate input format before conversion",
        }
        return suggestions.get(error_type, "Review and handle this error case")

    def get_common_errors(self, limit: int = 10) -> list:
        """Get most common errors."""
        cursor = self.conn.execute(
            """
            SELECT error_type, COUNT(*) as count, MAX(occurred_at) as last_occurred
            FROM error_history
            GROUP BY error_type
            ORDER BY count DESC
            LIMIT ?
            """,
            (limit,)
        )

        return [
            {'error_type': row['error_type'], 'count': row['count'], 'last_occurred': row['last_occurred']}
            for row in cursor.fetchall()
        ]

    def get_coding_profile(self) -> dict:
        """Get a summary profile of the developer's coding style."""
        preferences = self.get_preferences()
        patterns = self.get_patterns()
        insights = self.get_insights()
        common_errors = self.get_common_errors(5)

        # Categorize patterns
        strengths = [p for p in patterns if p.pattern_type == 'style' and
                    ('modern' in p.name or 'well' in p.name or 'proper' in p.name)]
        weaknesses = [p for p in patterns if p.pattern_type == 'error_prone']

        return {
            'preferences': preferences,
            'strengths': [{'name': s.name, 'description': s.description} for s in strengths],
            'areas_to_improve': [{'name': w.name, 'description': w.description} for w in weaknesses],
            'common_errors': common_errors,
            'total_patterns': len(patterns),
            'total_insights': len(insights),
        }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
