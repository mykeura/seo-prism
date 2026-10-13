# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Unit tests for meta_tags module (H1 duplicate detection was refactored)."""
from database import Database
from modules.meta_tags import MetaTagsModule


def _page(url, h1_list):
    h1s = ''.join(f'<h1>{h}</h1>' for h in h1_list)
    return {'url': url, 'status': 200,
            'html': f'<html><head><title>{url}</title></head><body>{h1s}</body></html>'}


def test_three_pages_same_h1_each_reports_two_duplicates():
    db = Database(':memory:')
    try:
        scan_id = db.create_scan('http://x.test')
        pages = [_page('http://x.test/a', ['Shared']),
                 _page('http://x.test/b', ['Shared']),
                 _page('http://x.test/c', ['Shared'])]
        issues = MetaTagsModule(db).analyze(scan_id, pages)
        dupes = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        # each of the 3 pages sees the other 2 -> 6 issues, no break
        assert len(dupes) == 6
    finally:
        db.close()


def test_distinct_h1s_report_no_duplicates():
    db = Database(':memory:')
    try:
        scan_id = db.create_scan('http://x.test')
        pages = [_page('http://x.test/a', ['Alpha']),
                 _page('http://x.test/b', ['Beta'])]
        issues = MetaTagsModule(db).analyze(scan_id, pages)
        assert not [i for i in issues if i['issue_type'] == 'duplicate_h1']
    finally:
        db.close()


def test_missing_h1_still_reported():
    db = Database(':memory:')
    try:
        scan_id = db.create_scan('http://x.test')
        pages = [{'url': 'http://x.test/a', 'status': 200,
                  'html': '<html><head><title>a</title></head><body><p>no h1</p></body></html>'}]
        issues = MetaTagsModule(db).analyze(scan_id, pages)
        assert any(i['issue_type'] == 'missing_h1' for i in issues)
    finally:
        db.close()
