# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Tests for the CLI scan command (backend/cli.py).

Uses click.testing.CliRunner and monkeypatches cli.run_scan with a fake async
function returning synthetic fixtures, so no network access is performed.
"""
import json
import pytest
from click.testing import CliRunner

import cli


def make_issue(issue_type, url, source_page=None, description=None,
               severity='medium', issue_id=None):
    """Build a synthetic issue with the same shape returned by the database."""
    return {
        'id': issue_id,
        'scan_id': 1,
        'issue_type': issue_type,
        'url': url,
        'source_page': source_page,
        'description': description,
        'severity': severity,
    }


def make_results(issues):
    """Build a synthetic results dict with the same keys as run_scan output."""
    return {
        'scan': {
            'id': 1,
            'url': 'https://example.com',
            'timestamp': '2026-08-23 12:00:00',
            'total_pages': 3,
            'total_issues': len(issues),
        },
        'issues': issues,
        # Full HTML on purpose: --json output must never include `pages`.
        'pages': [
            {
                'id': 1,
                'scan_id': 1,
                'url': 'https://example.com',
                'status': 200,
                'html': '<html><body><h1>huge page html</h1></body></html>',
            },
        ],
        'seo_grade': {'grade': 'B', 'score': 85, 'issues_per_page': 1.5},
        'resource_analysis': {
            'html_pages': 3,
            'css_files': 1,
            'js_files': 2,
            'images': 4,
            'other_resources': 0,
            'total_resources': 10,
        },
    }


@pytest.fixture
def runner():
    # click >= 8.2 removed mix_stderr: stdout and stderr are always captured
    # separately, so result.stderr is directly available.
    return CliRunner()


def _patch_run_scan(monkeypatch, results):
    """Replace cli.run_scan with a fake async function returning `results`."""
    async def fake_run_scan(url, max_pages, ignore_robots):
        return results
    monkeypatch.setattr(cli, 'run_scan', fake_run_scan)


def test_display_shows_all_issues_without_truncation(runner, monkeypatch):
    """A category with 25 issues must show all 25, with no 'and N more'."""
    issues = [
        make_issue(
            'broken_link',
            f'https://example.com/broken/{i}',
            source_page='https://example.com/',
            description=f'HTTP 404 (link {i})',
        )
        for i in range(25)
    ]
    _patch_run_scan(monkeypatch, make_results(issues))

    result = runner.invoke(cli.scan, ['--url', 'https://example.com'])

    assert result.exit_code == 0
    assert '... and' not in result.output
    # Every single one of the 25 broken links is listed
    for i in range(25):
        assert f'https://example.com/broken/{i}' in result.output
    assert result.output.count('https://example.com/broken/') == 25


def test_counter_only_categories_show_full_detail(runner, monkeypatch):
    """Categories that used to print only a count now list each issue in detail."""
    issues = [
        make_issue('duplicate_title', 'https://example.com/a',
                   source_page='https://example.com/a',
                   description='Title also used on https://example.com/b'),
        make_issue('duplicate_description', 'https://example.com/a',
                   source_page='https://example.com/a',
                   description='Description also used on https://example.com/b'),
        make_issue('missing_alt_tag', 'https://example.com/img/logo.png',
                   source_page='https://example.com/a',
                   description='Image is missing the alt attribute'),
        make_issue('missing_h1', 'https://example.com/no-h1',
                   source_page='https://example.com/no-h1',
                   description='The page does not contain any H1 header'),
        make_issue('invalid_header_hierarchy', 'https://example.com/hier',
                   source_page='https://example.com/hier',
                   description='H3 follows H1 without an intermediate H2'),
        make_issue('meta_robots_noindex', 'https://example.com/noindex',
                   source_page='https://example.com/noindex',
                   description='noindex directive found'),
        make_issue('hreflang_invalid_code', 'https://example.com/hreflang',
                   source_page='https://example.com/hreflang',
                   description='Invalid hreflang code: xx'),
        make_issue('canonical_chain', 'https://example.com/chain',
                   source_page='https://example.com/chain',
                   description='Canonical chain of 3 hops'),
        make_issue('missing_canonical', 'https://example.com/nc',
                   source_page='https://example.com/nc',
                   description='Page has no canonical tag'),
        make_issue('empty_canonical', 'https://example.com/ec',
                   source_page='https://example.com/ec',
                   description='Canonical tag is empty'),
        make_issue('title_too_long', 'https://example.com/tl',
                   source_page='https://example.com/tl',
                   description='Title is 75 characters'),
        make_issue('broken_image', 'https://example.com/img/missing.png',
                   source_page='https://example.com/a',
                   description='Image returned HTTP 404'),
    ]
    _patch_run_scan(monkeypatch, make_results(issues))

    result = runner.invoke(cli.scan, ['--url', 'https://example.com'])

    assert result.exit_code == 0
    for issue in issues:
        assert issue['url'] in result.output
        assert issue['source_page'] in result.output
        assert issue['description'] in result.output
    # Count-only placeholder messages are gone
    assert 'images missing alt text' not in result.output
    assert 'pages missing H1 header' not in result.output
    assert 'canonical chain(s) detected' not in result.output


def test_json_output_valid_complete_and_without_pages(runner, monkeypatch):
    """--json prints a single valid JSON payload with every issue and no pages."""
    issues = [
        make_issue('missing_title', 'https://example.com/no-title',
                   source_page='https://example.com/no-title',
                   description='Missing <title> tag'),
        make_issue('broken_link', 'https://example.com/x',
                   source_page='https://example.com/'),
    ] + [
        make_issue('thin_content', f'https://example.com/thin/{i}',
                   source_page=f'https://example.com/thin/{i}',
                   description='Only 42 words of content')
        for i in range(12)
    ]
    results = make_results(issues)
    _patch_run_scan(monkeypatch, results)

    result = runner.invoke(cli.scan, ['--url', 'https://example.com', '--json'])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert set(payload.keys()) == {'scan', 'issues', 'seo_grade', 'resource_analysis'}
    assert 'pages' not in payload
    assert 'huge page html' not in result.stdout
    assert len(payload['issues']) == 14
    assert payload['scan']['url'] == 'https://example.com'
    assert payload['seo_grade'] == results['seo_grade']
    assert payload['resource_analysis']['html_pages'] == 3
    # Every issue made it into the JSON, untruncated
    assert {issue['url'] for issue in payload['issues']} == {
        issue['url'] for issue in issues
    }


def test_json_mode_sends_progress_to_stderr(runner, monkeypatch):
    """In --json mode progress messages go to stderr; stdout holds only JSON."""
    _patch_run_scan(
        monkeypatch,
        make_results([make_issue('orphan_page', 'https://example.com/orphan',
                                 source_page='https://example.com/orphan',
                                 description='No incoming links')]),
    )

    result = runner.invoke(cli.scan, ['--url', 'https://example.com', '--json'])

    assert result.exit_code == 0
    assert 'Starting scan of' in result.stderr
    assert 'Scanning remote URL' in result.stderr
    # stdout contains nothing but the JSON payload
    assert result.stdout.lstrip().startswith('{')
    json.loads(result.stdout)  # must not raise
    assert 'Starting scan of' not in result.stdout


def test_unknown_issue_type_falls_into_other_issues(runner, monkeypatch):
    """An issue_type with no dedicated section is listed under 'Other Issues'."""
    issues = [
        make_issue('mystery_new_check', 'https://example.com/mystery',
                   source_page='https://example.com/',
                   description='A brand new failure type'),
    ]
    _patch_run_scan(monkeypatch, make_results(issues))

    result = runner.invoke(cli.scan, ['--url', 'https://example.com'])

    assert result.exit_code == 0
    assert 'Other Issues' in result.output
    # The raw issue_type is shown so unknown types remain identifiable
    assert 'mystery_new_check' in result.output
    assert 'https://example.com/mystery' in result.output
    assert '(in https://example.com/)' in result.output
    assert 'A brand new failure type' in result.output
