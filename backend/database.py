# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Optional

from core.issues import count_actionable_issues
from modules.seo_grade import SEOGradeCalculator


def _iso_utc(value: str) -> str:
    """Return an ISO timestamp with a zone, converting legacy naive rows.

    Older scans stored a naive ``datetime.now()`` (server local time); new
    scans store UTC with an explicit offset. Converting on read keeps the
    API contract uniform without rewriting existing databases.
    """
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return value
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()
    return parsed.astimezone(timezone.utc).isoformat()


class Database:
    """SQLite database for storing scan results."""
    
    def __init__(self, db_path: str = "scans.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        # The scan pipeline runs its CPU-bound analysis in a worker thread
        # while using the same connection. Access stays sequential (the event
        # loop awaits the worker before touching it again), so relaxing the
        # thread check is safe; each request owns its own Database instance.
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # WAL + synchronous=NORMAL: each add_issue commit stops costing a full
        # fsync (~7.7ms -> ~0.07ms measured). Under WAL, synchronous=NORMAL only
        # risks the last transactions on power loss, never on process crash.
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('PRAGMA synchronous=NORMAL')
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_pages INTEGER DEFAULT 0,
                total_issues INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                status INTEGER NOT NULL,
                html TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER NOT NULL,
                target_url TEXT NOT NULL,
                source_url TEXT NOT NULL,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                issue_type TEXT NOT NULL,
                url TEXT NOT NULL,
                source_page TEXT,
                description TEXT,
                severity TEXT DEFAULT 'medium',
                FOREIGN KEY (scan_id) REFERENCES scans (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_scan(self, url: str) -> int:
        """
        Create a new scan record.
        
        Args:
            url: Target URL being scanned
        
        Returns:
            Scan ID
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO scans (url, timestamp) VALUES (?, ?)',
            (url, datetime.now(timezone.utc).isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def add_page(self, scan_id: int, url: str, status: int, html: Optional[str] = None) -> int:
        """
        Add a page to the scan.
        
        Args:
            scan_id: Scan ID
            url: Page URL
            status: HTTP status code
            html: Page HTML content (optional)
        
        Returns:
            Page ID
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO pages (scan_id, url, status, html) VALUES (?, ?, ?, ?)',
            (scan_id, url, status, html)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def add_link(self, page_id: int, target_url: str, source_url: str):
        """
        Add a link found on a page.
        
        Args:
            page_id: Page ID
            target_url: Target URL of the link
            source_url: Source page URL
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO links (page_id, target_url, source_url) VALUES (?, ?, ?)',
            (page_id, target_url, source_url)
        )
        self.conn.commit()
    
    def store_crawled_pages(self, scan_id: int, crawled_pages: List[Dict]):
        """
        Store all crawled pages and their outgoing links in one transaction.
        
        Args:
            scan_id: Scan ID
            crawled_pages: List of page dicts with 'url', 'status', 'html' and 'links'
        """
        cursor = self.conn.cursor()
        for page in crawled_pages:
            cursor.execute(
                'INSERT INTO pages (scan_id, url, status, html) VALUES (?, ?, ?, ?)',
                (scan_id, page['url'], page['status'], page.get('html'))
            )
            page_id = cursor.lastrowid
            links = page.get('links', [])
            if links:
                cursor.executemany(
                    'INSERT INTO links (page_id, target_url, source_url) VALUES (?, ?, ?)',
                    [(page_id, link, page['url']) for link in links]
                )
        self.conn.commit()
    
    def add_issue(self, scan_id: int, issue_type: str, url: str, 
                  source_page: Optional[str] = None, description: Optional[str] = None,
                  severity: str = 'medium'):
        """
        Add an issue found during scan.
        
        Args:
            scan_id: Scan ID
            issue_type: Type of issue (e.g., 'broken_link', 'missing_title')
            url: URL where issue was found
            source_page: Source page URL (optional)
            description: Issue description (optional)
            severity: Issue severity (low/medium/high)
        """
        cursor = self.conn.cursor()
        cursor.execute(
            '''INSERT INTO issues (scan_id, issue_type, url, source_page, description, severity) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (scan_id, issue_type, url, source_page, description, severity)
        )
        self.conn.commit()
    
    def update_scan_totals(self, scan_id: int, total_pages: int, total_issues: int):
        """
        Update scan totals.
        
        Args:
            scan_id: Scan ID
            total_pages: Total pages scanned
            total_issues: Actionable issues found (info notices excluded)
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE scans SET total_pages = ?, total_issues = ? WHERE id = ?',
            (total_pages, total_issues, scan_id)
        )
        self.conn.commit()
    
    def get_scan_results(self, scan_id: int) -> Dict:
        """
        Get complete scan results.
        
        Args:
            scan_id: Scan ID
        
        Returns:
            Dictionary with scan results. 'pages' holds id/scan_id/url/status
            only; the stored HTML body is intentionally not returned.
        """
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
        scan = cursor.fetchone()
        
        if not scan:
            return {}
        
        cursor.execute('SELECT * FROM issues WHERE scan_id = ?', (scan_id,))
        issues = [dict(row) for row in cursor.fetchall()]
        
        # Get pages. The html column is deliberately NOT selected: nothing
        # consumes it (the CLI --json payload and the MCP tool drop pages on
        # purpose, the frontend never reads it), and serving it meant 4-8 MB
        # of JSON per GET /results. The column stays in the table so a scan can
        # be re-analysed; select it explicitly if the raw bodies are needed.
        cursor.execute(
            'SELECT id, scan_id, url, status FROM pages WHERE scan_id = ?',
            (scan_id,)
        )
        pages = [dict(row) for row in cursor.fetchall()]

        scan_dict = dict(scan)
        if 'timestamp' in scan_dict:
            scan_dict['timestamp'] = _iso_utc(scan_dict['timestamp'])
        # Count from the issue rows instead of trusting the stored total:
        # info-level confirmations are not issues and older scans may have
        # been persisted with them included.
        scan_dict['total_issues'] = count_actionable_issues(issues)
        scan_dict['info_notices'] = len(issues) - scan_dict['total_issues']

        return {
            'scan': scan_dict,
            'issues': issues,
            'pages': pages
        }
    
    def get_latest_scan(self) -> Optional[Dict]:
        """
        Get the most recent scan results.
        
        Returns:
            Dictionary with scan results or None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM scans ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        
        if result:
            return self.get_scan_results(result['id'])
        
        return None
    
    def list_scans(self, limit: int = 50) -> List[Dict]:
        """
        List recent scans, newest first.
        
        Args:
            limit: Maximum number of scans to return
        
        Returns:
            List of dicts with keys scan_id, url, scan_date (ISO string),
            grade_letter, grade_score and total_issues. Both the grade and
            the actionable issue count are recomputed from the stored page
            count and issue severities, so info-level notices are excluded
            even for scans persisted before this rule existed.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, url, timestamp, total_pages, total_issues '
            # id order (insertion order) rather than timestamp: rows written
            # before the UTC change hold a naive local timestamp, so string
            # comparison across the two formats is not chronological.
            'FROM scans ORDER BY id DESC LIMIT ?',
            (limit,)
        )
        rows = cursor.fetchall()
        
        calculator = SEOGradeCalculator()
        scans = []
        for row in rows:
            cursor.execute(
                'SELECT severity FROM issues WHERE scan_id = ?',
                (row['id'],)
            )
            issues = [{'severity': r['severity']} for r in cursor.fetchall()]
            grade = calculator.calculate_grade(row['total_pages'] or 0, issues)
            scans.append({
                'scan_id': row['id'],
                'url': row['url'],
                'scan_date': _iso_utc(row['timestamp']),
                'grade_letter': grade['grade'],
                'grade_score': grade['score'],
                'total_issues': count_actionable_issues(issues),
            })
        return scans
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()