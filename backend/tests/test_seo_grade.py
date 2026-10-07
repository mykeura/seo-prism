# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-SEO-Prism-Commercial
# SPDX-FileCopyrightText: 2026 Miguel Euraque (mykeura)

"""
Unit tests for seo_grade module.
"""
import pytest
from modules.seo_grade import SEOGradeCalculator


class TestSEOGradeCalculator:
    """Tests for SEOGradeCalculator class."""
    
    def test_calculate_grade_perfect(self):
        """Test calculating grade with no issues."""
        calculator = SEOGradeCalculator()
        result = calculator.calculate_grade(10, [])
        
        assert result['score'] == 100
        assert result['grade'] == 'A'
        assert result['breakdown']['high'] == 0
        assert result['breakdown']['medium'] == 0
        assert result['breakdown']['low'] == 0
        assert result['breakdown']['total'] == 0
    
    def test_calculate_grade_high_severity(self):
        """Test calculating grade with high severity issues."""
        calculator = SEOGradeCalculator()
        issues = [
            {'severity': 'high'},
            {'severity': 'high'}
        ]
        result = calculator.calculate_grade(10, issues)
        
        assert result['score'] < 100
        assert result['grade'] in ['A', 'B', 'C', 'D', 'F']
        assert result['breakdown']['high'] == 2
    
    def test_calculate_grade_medium_severity(self):
        """Test calculating grade with medium severity issues."""
        calculator = SEOGradeCalculator()
        issues = [
            {'severity': 'medium'},
            {'severity': 'medium'},
            {'severity': 'medium'}
        ]
        result = calculator.calculate_grade(10, issues)
        
        assert result['score'] < 100
        assert result['breakdown']['medium'] == 3
    
    def test_calculate_grade_low_severity(self):
        """Test calculating grade with low severity issues."""
        calculator = SEOGradeCalculator()
        issues = [
            {'severity': 'low'},
            {'severity': 'low'},
            {'severity': 'low'},
            {'severity': 'low'},
            {'severity': 'low'}
        ]
        result = calculator.calculate_grade(10, issues)
        
        assert result['score'] < 100
        assert result['breakdown']['low'] == 5
    
    def test_calculate_grade_mixed_severity(self):
        """Test calculating grade with mixed severity issues."""
        calculator = SEOGradeCalculator()
        issues = [
            {'severity': 'high'},
            {'severity': 'high'},
            {'severity': 'medium'},
            {'severity': 'medium'},
            {'severity': 'medium'},
            {'severity': 'low'}
        ]
        result = calculator.calculate_grade(10, issues)
        
        assert result['score'] < 100
        assert result['breakdown']['high'] == 2
        assert result['breakdown']['medium'] == 3
        assert result['breakdown']['low'] == 1
        assert result['breakdown']['total'] == 6
    
    def test_calculate_grade_zero_pages(self):
        """Test calculating grade with zero pages."""
        calculator = SEOGradeCalculator()
        result = calculator.calculate_grade(0, [])
        
        assert result['score'] == 0
        assert result['grade'] == 'F'
        assert result['breakdown']['total'] == 0
    
    def test_calculate_grade_f_grade(self):
        """Test calculating F grade (0-59%)."""
        calculator = SEOGradeCalculator()
        # Create enough high severity issues to get F grade
        issues = [{'severity': 'high'}] * 20
        result = calculator.calculate_grade(10, issues)
        
        assert result['grade'] == 'F'
    
    def test_calculate_grade_d_grade(self):
        """Test calculating D grade (60-69%)."""
        calculator = SEOGradeCalculator()
        # Create enough issues to get D grade
        issues = [{'severity': 'high'}] * 5
        result = calculator.calculate_grade(10, issues)
        
        assert result['grade'] in ['D', 'F']
    
    def test_calculate_grade_c_grade(self):
        """Test calculating C grade (70-79%)."""
        calculator = SEOGradeCalculator()
        # Create enough issues to get C grade
        issues = [{'severity': 'high'}] * 3
        result = calculator.calculate_grade(10, issues)
        
        assert result['grade'] in ['C', 'D', 'F']
    
    def test_calculate_grade_b_grade(self):
        """Test calculating B grade (80-89%)."""
        calculator = SEOGradeCalculator()
        # Create enough issues to get B grade
        issues = [{'severity': 'high'}] * 1
        result = calculator.calculate_grade(10, issues)
        
        assert result['grade'] in ['A', 'B', 'C']
    
    def test_get_grade_from_score(self):
        """Test _get_grade_from_score method."""
        calculator = SEOGradeCalculator()
        
        assert calculator._get_grade_from_score(95) == 'A'
        assert calculator._get_grade_from_score(90) == 'A'
        assert calculator._get_grade_from_score(85) == 'B'
        assert calculator._get_grade_from_score(80) == 'B'
        assert calculator._get_grade_from_score(75) == 'C'
        assert calculator._get_grade_from_score(70) == 'C'
        assert calculator._get_grade_from_score(65) == 'D'
        assert calculator._get_grade_from_score(60) == 'D'
        assert calculator._get_grade_from_score(50) == 'F'
        assert calculator._get_grade_from_score(0) == 'F'
    
    def test_get_grade_color(self):
        """Test get_grade_color method."""
        calculator = SEOGradeCalculator()
        
        assert calculator.get_grade_color('A') == 'green'
        assert calculator.get_grade_color('B') == 'blue'
        assert calculator.get_grade_color('C') == 'yellow'
        assert calculator.get_grade_color('D') == 'orange'
        assert calculator.get_grade_color('F') == 'red'
        assert calculator.get_grade_color('X') == 'gray'
    
    def test_severity_weights(self):
        """Test that severity weights are applied correctly."""
        calculator = SEOGradeCalculator()

        # 1 high (3) + 2 medium (2) + 3 low (1.5) = 6.5 weighted errors
        # For 10 pages: density 0.65 -> logarithmic penalty applies
        issues = [
            {'severity': 'high'},
            {'severity': 'medium'},
            {'severity': 'medium'},
            {'severity': 'low'},
            {'severity': 'low'},
            {'severity': 'low'}
        ]
        result = calculator.calculate_grade(10, issues)

        assert result['score'] >= 0
        assert result['score'] <= 100


def _issues(high=0, medium=0, low=0):
    return ([{'severity': 'high'}] * high +
            [{'severity': 'medium'}] * medium +
            [{'severity': 'low'}] * low)


class TestSEOGradeFairness:
    """Fairness guarantees of the grading formula.

    Regression guards for the historic bug where a tiny site with many
    issues could score better than a large site with fewer issues.
    """

    def test_small_dirty_vs_large_clean(self):
        """The owner's original complaint: 5 pages / 50 issues must lose
        against 100 pages / 20 issues."""
        calculator = SEOGradeCalculator()
        small = calculator.calculate_grade(5, _issues(17, 17, 16))
        large = calculator.calculate_grade(100, _issues(7, 7, 6))

        assert small['score'] < large['score']
        assert small['grade'] != 'A' and large['grade'] != 'F'
        assert small['grade'] == 'F'
        assert large['grade'] == 'B'

    def test_severity_mix_inversion(self):
        """Weighted density — not raw issue count — drives the score:
        12 high issues on 100 pages (density 0.36) must score lower than
        30 low issues on 50 pages (density 0.30), even though the second
        site has 2.5x more total issues. The severity weights encode this
        exchange rate: 1 high == 6 low."""
        calculator = SEOGradeCalculator()
        mild = calculator.calculate_grade(50, _issues(low=30))
        severe = calculator.calculate_grade(100, _issues(high=12))

        assert severe['score'] < mild['score']

        # Same weighted density through a different mix and size -> same score
        same_density = calculator.calculate_grade(100, _issues(low=60))
        assert same_density['score'] == mild['score']

    def test_equal_density_same_score_any_size(self):
        """Same error density must yield the exact same score whether the
        site has 10, 100 or 1000 pages."""
        calculator = SEOGradeCalculator()
        s10 = calculator.calculate_grade(10, _issues(7, 7, 6))
        s100 = calculator.calculate_grade(100, _issues(70, 70, 60))
        s1000 = calculator.calculate_grade(1000, _issues(700, 700, 600))

        assert s10['score'] == s100['score'] == s1000['score']

    def test_monotonic_by_density(self):
        """More error density must never improve the score."""
        calculator = SEOGradeCalculator()
        scenarios = [
            (10, _issues(0, 1, 0)),    # d = 0.1
            (10, _issues(0, 3, 0)),    # d = 0.3
            (10, _issues(0, 5, 0)),    # d = 0.5
            (10, _issues(0, 10, 0)),   # d = 1.0
            (10, _issues(0, 30, 0)),   # d = 3.0
            (10, _issues(0, 100, 0)),  # d = 10.0
        ]
        scores = [calculator.calculate_grade(p, i)['score'] for p, i in scenarios]
        assert scores == sorted(scores, reverse=True)
        assert scores[0] > scores[-1]

    def test_monotonic_by_severity(self):
        """At equal counts, high severity must hurt more than medium than low."""
        calculator = SEOGradeCalculator()
        low = calculator.calculate_grade(10, _issues(low=5))['score']
        medium = calculator.calculate_grade(10, _issues(medium=5))['score']
        high = calculator.calculate_grade(10, _issues(high=5))['score']

        assert high < medium < low

    def test_single_trivial_issue_does_not_fail_tiny_site(self):
        """1 low issue on a 1-page article must not be an F."""
        calculator = SEOGradeCalculator()
        result = calculator.calculate_grade(1, _issues(low=1))

        assert result['grade'] in ['A', 'B', 'C']
        assert result['score'] >= 80

    def test_saturation_still_discriminates(self):
        """Beyond the old linear cliff, more issues must still lower the
        score (15 vs 50 issues on 5 pages used to both be 0/F)."""
        calculator = SEOGradeCalculator()
        few = calculator.calculate_grade(5, _issues(5, 5, 5))['score']
        many = calculator.calculate_grade(5, _issues(17, 17, 16))['score']

        assert few > many >= 0

    def test_score_and_letter_always_agree(self):
        """The letter must match the displayed (rounded) score."""
        calculator = SEOGradeCalculator()
        for pages, issues in [(100, _issues(7, 7, 6)), (10, _issues(0, 1, 0)),
                              (1, _issues(low=1)), (200, _issues(high=7)),
                              (3, _issues(1, 1, 1))]:
            result = calculator.calculate_grade(pages, issues)
            assert result['grade'] == calculator._get_grade_from_score(result['score'])

    def test_zero_pages_with_issues_is_safe(self):
        calculator = SEOGradeCalculator()
        result = calculator.calculate_grade(0, _issues(high=3))

        assert result['score'] == 0
        assert result['grade'] == 'F'

    def test_unknown_severity_counts_but_does_not_weigh(self):
        """'info' issues appear in breakdown.total yet do not lower the score."""
        calculator = SEOGradeCalculator()
        result = calculator.calculate_grade(10, [{'severity': 'info'}] * 5)

        assert result['score'] == 100
        assert result['grade'] == 'A'
        assert result['breakdown']['total'] == 5

    def test_reference_values_of_the_scale(self):
        """Documents the log scale so accidental re-linearization is caught."""
        calculator = SEOGradeCalculator()

        # d = 0.5 (5 medium on 10 pages)
        assert calculator.calculate_grade(10, _issues(medium=5))['score'] == 83
        # d = 1.0 (10 medium on 10 pages)
        assert calculator.calculate_grade(10, _issues(medium=10))['score'] == 71
        # d >= MAX_ERROR_DENSITY (100 medium on 10 pages)
        assert calculator.calculate_grade(10, _issues(medium=100))['score'] == 0
        assert calculator.calculate_grade(10, _issues(medium=100))['grade'] == 'F'