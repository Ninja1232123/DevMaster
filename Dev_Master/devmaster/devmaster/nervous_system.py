"""
The Nervous System - Unified event bus connecting all tools.

This is the backbone that makes the ecosystem alive. Tools publish events,
other tools subscribe and react. One brain, not nine.

Event Types:
- hotspot_detected: CodeArchaeology found a frequently-changing file
- error_pattern_learned: DevMaster learner detected a recurring error
- deployment_failed: Deploy-Shield caught a pre-deploy issue
- code_indexed: CodeSeek finished indexing
- knowledge_added: DevKnowledge stored new documentation
- fix_applied: Universal Debugger fixed an error
"""

import json
import sqlite3
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Any
from enum import Enum


class EventType(Enum):
    """All event types in the ecosystem."""
    # CodeArchaeology events
    HOTSPOT_DETECTED = "hotspot_detected"
    CODE_EVOLUTION = "code_evolution"
    CHURN_SPIKE = "churn_spike"

    # DevMaster Learner events
    ERROR_PATTERN_LEARNED = "error_pattern_learned"
    CODING_STYLE_UPDATED = "coding_style_updated"
    NEW_INSIGHT = "new_insight"

    # Deploy-Shield events
    DEPLOYMENT_FAILED = "deployment_failed"
    ENV_MISCONFIGURED = "env_misconfigured"
    CONNECTION_FAILED = "connection_failed"

    # CodeSeek events
    CODE_INDEXED = "code_indexed"
    SIMILAR_CODE_FOUND = "similar_code_found"

    # DevKnowledge events
    KNOWLEDGE_ADDED = "knowledge_added"
    LINK_DISCOVERED = "link_discovered"

    # Universal Debugger events
    FIX_APPLIED = "fix_applied"
    NEW_PATTERN_NEEDED = "new_pattern_needed"
    ERROR_PREDICTED = "error_predicted"

    # Type-Guardian events
    TYPE_ERROR_FIXED = "type_error_fixed"
    HINTS_ADDED = "hints_added"

    # AI Debug Companion events
    SUGGESTION_MADE = "suggestion_made"
    FIX_ACCEPTED = "fix_accepted"


@dataclass
class Event:
    """An event in the nervous system."""
    event_type: str
    source_tool: str
    payload: dict
    timestamp: str = None
    event_id: int = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Subscription:
    """A subscription to events."""
    event_type: str
    callback: Callable[[Event], None]
    subscriber_id: str


class NervousSystem:
    """
    The central event bus connecting all tools in the ecosystem.

    Usage:
        ns = NervousSystem()

        # Subscribe to events
        ns.subscribe('hotspot_detected', my_callback, 'debugger')

        # Publish events
        ns.publish(Event(
            event_type='hotspot_detected',
            source_tool='codearchaeology',
            payload={'file': 'src/main.py', 'churn_rate': 15}
        ))
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = None):
        """Singleton pattern - one nervous system for the whole ecosystem."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None):
        if self._initialized:
            return

        self.db_path = Path(db_path or "~/.devmaster/nervous_system.db").expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.subscriptions: dict[str, list[Subscription]] = {}
        self.conn: Optional[sqlite3.Connection] = None

        self._init_db()
        self._initialized = True

    def _init_db(self):
        """Initialize the event store database."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                source_tool TEXT NOT NULL,
                payload TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                processed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
            CREATE INDEX IF NOT EXISTS idx_events_source ON events(source_tool);
            CREATE INDEX IF NOT EXISTS idx_events_processed ON events(processed);

            CREATE TABLE IF NOT EXISTS integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_event TEXT NOT NULL,
                target_tool TEXT NOT NULL,
                action TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                last_triggered TEXT,
                trigger_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                subscriber_id TEXT,
                status TEXT,
                error_message TEXT,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

        # Register default integrations
        self._register_default_integrations()

    def _register_default_integrations(self):
        """Register the default cross-tool integrations."""
        default_integrations = [
            # CodeArchaeology → Universal Debugger
            ('hotspot_detected', 'universal_debugger', 'add_to_watchlist'),
            ('churn_spike', 'universal_debugger', 'increase_scrutiny'),

            # DevMaster Learner → Universal Debugger
            ('error_pattern_learned', 'universal_debugger', 'generate_pattern'),

            # Deploy-Shield → AI Debug Companion
            ('deployment_failed', 'ai_debug_companion', 'analyze_failure'),
            ('connection_failed', 'ai_debug_companion', 'suggest_fix'),

            # CodeSeek → DevKnowledge
            ('code_indexed', 'devknowledge', 'link_documentation'),
            ('similar_code_found', 'devknowledge', 'create_reference'),

            # Universal Debugger → DevMaster Learner
            ('fix_applied', 'devmaster_learner', 'record_fix'),
            ('new_pattern_needed', 'devmaster_learner', 'analyze_error'),

            # Type-Guardian → Universal Debugger
            ('type_error_fixed', 'universal_debugger', 'add_type_pattern'),
        ]

        cursor = self.conn.cursor()
        for source_event, target_tool, action in default_integrations:
            cursor.execute("""
                INSERT OR IGNORE INTO integrations (source_event, target_tool, action)
                SELECT ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM integrations
                    WHERE source_event = ? AND target_tool = ? AND action = ?
                )
            """, (source_event, target_tool, action, source_event, target_tool, action))
        self.conn.commit()

    def subscribe(self, event_type: str, callback: Callable[[Event], None], subscriber_id: str):
        """Subscribe to an event type."""
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []

        self.subscriptions[event_type].append(Subscription(
            event_type=event_type,
            callback=callback,
            subscriber_id=subscriber_id
        ))

    def unsubscribe(self, event_type: str, subscriber_id: str):
        """Unsubscribe from an event type."""
        if event_type in self.subscriptions:
            self.subscriptions[event_type] = [
                s for s in self.subscriptions[event_type]
                if s.subscriber_id != subscriber_id
            ]

    def publish(self, event: Event) -> int:
        """Publish an event to all subscribers."""
        # Store event
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO events (event_type, source_tool, payload, timestamp)
            VALUES (?, ?, ?, ?)
        """, (event.event_type, event.source_tool, json.dumps(event.payload), event.timestamp))
        self.conn.commit()
        event_id = cursor.lastrowid
        event.event_id = event_id

        # Notify subscribers
        subscribers = self.subscriptions.get(event.event_type, [])
        for sub in subscribers:
            try:
                sub.callback(event)
                self._log_event_processing(event_id, sub.subscriber_id, 'success')
            except Exception as e:
                self._log_event_processing(event_id, sub.subscriber_id, 'error', str(e))

        # Trigger integrations
        self._trigger_integrations(event)

        return event_id

    def _trigger_integrations(self, event: Event):
        """Trigger registered integrations for an event."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM integrations
            WHERE source_event = ? AND enabled = 1
        """, (event.event_type,))

        for row in cursor.fetchall():
            # Update trigger stats
            self.conn.execute("""
                UPDATE integrations
                SET last_triggered = ?, trigger_count = trigger_count + 1
                WHERE id = ?
            """, (datetime.now().isoformat(), row['id']))

        self.conn.commit()

    def _log_event_processing(self, event_id: int, subscriber_id: str, status: str, error: str = None):
        """Log event processing result."""
        self.conn.execute("""
            INSERT INTO event_log (event_id, subscriber_id, status, error_message)
            VALUES (?, ?, ?, ?)
        """, (event_id, subscriber_id, status, error))
        self.conn.commit()

    def get_recent_events(self, event_type: str = None, limit: int = 50) -> list[Event]:
        """Get recent events, optionally filtered by type."""
        if event_type:
            cursor = self.conn.execute("""
                SELECT * FROM events WHERE event_type = ?
                ORDER BY id DESC LIMIT ?
            """, (event_type, limit))
        else:
            cursor = self.conn.execute("""
                SELECT * FROM events ORDER BY id DESC LIMIT ?
            """, (limit,))

        return [
            Event(
                event_id=row['id'],
                event_type=row['event_type'],
                source_tool=row['source_tool'],
                payload=json.loads(row['payload']),
                timestamp=row['timestamp']
            )
            for row in cursor.fetchall()
        ]

    def get_integration_stats(self) -> list[dict]:
        """Get statistics on integrations."""
        cursor = self.conn.execute("""
            SELECT source_event, target_tool, action, enabled,
                   last_triggered, trigger_count
            FROM integrations
            ORDER BY trigger_count DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    def get_event_flow(self, hours: int = 24) -> dict:
        """Get event flow statistics for visualization."""
        cursor = self.conn.execute("""
            SELECT source_tool, event_type, COUNT(*) as count
            FROM events
            WHERE timestamp > datetime('now', ?)
            GROUP BY source_tool, event_type
            ORDER BY count DESC
        """, (f'-{hours} hours',))

        flow = {}
        for row in cursor.fetchall():
            source = row['source_tool']
            if source not in flow:
                flow[source] = {}
            flow[source][row['event_type']] = row['count']

        return flow

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================================
# Integration Handlers - The actual wiring between tools
# ============================================================================

class IntegrationHandlers:
    """
    Handlers that implement the actual integrations between tools.
    These are the synapses of the nervous system.
    """

    def __init__(self, nervous_system: NervousSystem):
        self.ns = nervous_system
        self._register_handlers()

    def _register_handlers(self):
        """Register all integration handlers."""
        # CodeArchaeology → Universal Debugger
        self.ns.subscribe('hotspot_detected', self.hotspot_to_watchlist, 'debugger_integration')

        # DevMaster Learner → Universal Debugger
        self.ns.subscribe('error_pattern_learned', self.error_to_pattern, 'debugger_integration')

        # Universal Debugger → DevMaster Learner
        self.ns.subscribe('fix_applied', self.fix_to_learner, 'learner_integration')

        # CodeSeek → DevKnowledge
        self.ns.subscribe('code_indexed', self.index_to_knowledge, 'knowledge_integration')

    def hotspot_to_watchlist(self, event: Event):
        """When CodeArchaeology finds a hotspot, add it to debugger's watchlist."""
        file_path = event.payload.get('file_path')
        churn_rate = event.payload.get('churn_rate', 0)

        if file_path and churn_rate > 5:
            # Store as a high-priority watch target
            watchlist_path = Path("~/.devmaster/watchlist.json").expanduser()
            watchlist_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                watchlist = json.loads(watchlist_path.read_text()) if watchlist_path.exists() else []
            except:
                watchlist = []

            # Add or update entry
            existing = next((w for w in watchlist if w['file'] == file_path), None)
            if existing:
                existing['churn_rate'] = churn_rate
                existing['updated'] = datetime.now().isoformat()
            else:
                watchlist.append({
                    'file': file_path,
                    'churn_rate': churn_rate,
                    'added': datetime.now().isoformat(),
                    'source': 'codearchaeology'
                })

            watchlist_path.write_text(json.dumps(watchlist, indent=2))

    def error_to_pattern(self, event: Event):
        """When learner detects recurring error, suggest pattern for debugger."""
        error_type = event.payload.get('error_type')
        pattern = event.payload.get('pattern')
        fix_suggestion = event.payload.get('fix_suggestion')
        frequency = event.payload.get('frequency', 0)

        if error_type and pattern and frequency >= 3:
            # Store as suggested pattern
            suggestions_path = Path("~/.devmaster/pattern_suggestions.json").expanduser()
            suggestions_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                suggestions = json.loads(suggestions_path.read_text()) if suggestions_path.exists() else []
            except:
                suggestions = []

            suggestions.append({
                'error_type': error_type,
                'pattern': pattern,
                'fix_suggestion': fix_suggestion,
                'frequency': frequency,
                'suggested_at': datetime.now().isoformat(),
                'status': 'pending'
            })

            suggestions_path.write_text(json.dumps(suggestions, indent=2))

    def fix_to_learner(self, event: Event):
        """When debugger fixes an error, record it for learning."""
        error_type = event.payload.get('error_type')
        file_path = event.payload.get('file_path')
        fix_applied = event.payload.get('fix_applied')

        if error_type and fix_applied:
            # Store fix for learner analysis
            fixes_path = Path("~/.devmaster/fix_history.json").expanduser()
            fixes_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                fixes = json.loads(fixes_path.read_text()) if fixes_path.exists() else []
            except:
                fixes = []

            fixes.append({
                'error_type': error_type,
                'file_path': file_path,
                'fix_applied': fix_applied,
                'fixed_at': datetime.now().isoformat()
            })

            # Keep last 1000 fixes
            fixes = fixes[-1000:]
            fixes_path.write_text(json.dumps(fixes, indent=2))

    def index_to_knowledge(self, event: Event):
        """When CodeSeek indexes code, notify DevKnowledge for linking."""
        files_indexed = event.payload.get('files_indexed', 0)
        symbols_found = event.payload.get('symbols_found', 0)
        repo_path = event.payload.get('repo_path')

        if files_indexed > 0:
            # Store indexing event for DevKnowledge
            index_log_path = Path("~/.devmaster/index_events.json").expanduser()
            index_log_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                log = json.loads(index_log_path.read_text()) if index_log_path.exists() else []
            except:
                log = []

            log.append({
                'repo_path': repo_path,
                'files_indexed': files_indexed,
                'symbols_found': symbols_found,
                'indexed_at': datetime.now().isoformat()
            })

            # Keep last 100 events
            log = log[-100:]
            index_log_path.write_text(json.dumps(log, indent=2))


# ============================================================================
# Convenience functions for publishing events from any tool
# ============================================================================

def publish_hotspot(file_path: str, churn_rate: int, change_count: int):
    """Publish a hotspot detection event from CodeArchaeology."""
    ns = NervousSystem()
    ns.publish(Event(
        event_type='hotspot_detected',
        source_tool='codearchaeology',
        payload={
            'file_path': file_path,
            'churn_rate': churn_rate,
            'change_count': change_count
        }
    ))


def publish_error_pattern(error_type: str, pattern: str, fix_suggestion: str, frequency: int):
    """Publish an error pattern event from DevMaster Learner."""
    ns = NervousSystem()
    ns.publish(Event(
        event_type='error_pattern_learned',
        source_tool='devmaster_learner',
        payload={
            'error_type': error_type,
            'pattern': pattern,
            'fix_suggestion': fix_suggestion,
            'frequency': frequency
        }
    ))


def publish_fix_applied(error_type: str, file_path: str, line_number: int, fix_applied: str):
    """Publish a fix applied event from Universal Debugger."""
    ns = NervousSystem()
    ns.publish(Event(
        event_type='fix_applied',
        source_tool='universal_debugger',
        payload={
            'error_type': error_type,
            'file_path': file_path,
            'line_number': line_number,
            'fix_applied': fix_applied
        }
    ))


def publish_code_indexed(repo_path: str, files_indexed: int, symbols_found: int):
    """Publish a code indexed event from CodeSeek."""
    ns = NervousSystem()
    ns.publish(Event(
        event_type='code_indexed',
        source_tool='codeseek',
        payload={
            'repo_path': repo_path,
            'files_indexed': files_indexed,
            'symbols_found': symbols_found
        }
    ))


def publish_deployment_failed(reason: str, config_file: str, details: dict):
    """Publish a deployment failure event from Deploy-Shield."""
    ns = NervousSystem()
    ns.publish(Event(
        event_type='deployment_failed',
        source_tool='deploy_shield',
        payload={
            'reason': reason,
            'config_file': config_file,
            'details': details
        }
    ))


def get_nervous_system() -> NervousSystem:
    """Get the singleton nervous system instance."""
    return NervousSystem()


def initialize_integrations():
    """Initialize all integration handlers."""
    ns = NervousSystem()
    handlers = IntegrationHandlers(ns)
    return handlers
