# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""Unit tests for meta_tags module (H1 duplicate detection was refactored)."""
from database import Database
from modules.meta_tags import MetaTagsModule


def _page(url, h1_list):
    h1s = ''.join(f'<h1>{h}</h1>' for h in h1_list)
    return {'url': url, 'status': 200,
            'html': f'<html><head><title>{url}</title></head><body>{h1s}</body></html>'}


def test_three_pages_same_h1_report_one_issue_each():
    db = Database(':memory:')
    try:
        scan_id = db.create_scan('http://x.test')
        pages = [_page('http://x.test/a', ['Shared']),
                 _page('http://x.test/b', ['Shared']),
                 _page('http://x.test/c', ['Shared'])]
        issues = MetaTagsModule(db).analyze(scan_id, pages)
        dupes = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        # One issue per affected page, never one per pair (the old code
        # produced 6 for this fixture and N*(N-1) in the worst case).
        assert len(dupes) == 3
        assert {i['url'] for i in dupes} == {
            'http://x.test/a', 'http://x.test/b', 'http://x.test/c'}
        assert all(i['severity'] == 'high' for i in dupes)
        assert all('Shared' in i['description'] for i in dupes)
    finally:
        db.close()


def test_many_pages_same_h1_scale_linearly():
    db = Database(':memory:')
    try:
        scan_id = db.create_scan('http://x.test')
        pages = [_page(f'http://x.test/p{i}', ['Welcome']) for i in range(10)]
        issues = MetaTagsModule(db).analyze(scan_id, pages)
        dupes = [i for i in issues if i['issue_type'] == 'duplicate_h1']
        assert len(dupes) == 10
    finally:
        db.close()


def test_same_h1_different_case_is_duplicate():
    db = Database(':memory:')
    try:
        scan_id = db.create_scan('http://x.test')
        pages = [_page('http://x.test/a', ['Welcome']),
                 _page('http://x.test/b', ['WELCOME'])]
        issues = MetaTagsModule(db).analyze(scan_id, pages)
        assert len([i for i in issues if i['issue_type'] == 'duplicate_h1']) == 2
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
