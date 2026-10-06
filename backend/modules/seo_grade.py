# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 mykeura <mykeura@hotmail.com>

"""
SEO Grade Calculator Module

Calculates SEO grade based on error density and severity.
Uses US grading system: A (90-100%), B (80-89%), C (70-79%), D (60-69%), F (0-59%)

The penalty scale is logarithmic: the score falls in proportion to
log10(1 + density) instead of density itself. A linear scale saturates at
just 1 weighted issue per page (every realistic site collapsed to F and
tiny sites were crushed by a single trivial issue), while a log scale
keeps discriminating across the whole range and treats equal error
densities equally regardless of site size:

    density = (3*high + 1*medium + 0.5*low) / pages
    score   = 100 * (1 - log10(1 + density) / log10(1 + MAX_ERROR_DENSITY))
"""

import math
from typing import List, Dict


class SEOGradeCalculator:
    """Calculates SEO grade based on error density."""

    # Severity weights for penalty calculation
    SEVERITY_WEIGHTS = {
        'high': 3,
        'medium': 1,
        'low': 0.5
    }

    # Weighted issues per page considered pathological (score reaches 0).
    # Grade bands with this value: A up to d≈0.25, B to ≈0.6, C to ≈1.05,
    # D to ≈1.6, F beyond.
    MAX_ERROR_DENSITY = 10.0

    def __init__(self):
        """Initialize the SEO grade calculator."""
        pass

    def calculate_grade(self, total_pages: int, issues: List[Dict]) -> Dict:
        """
        Calculate SEO grade based on error density.

        Args:
            total_pages: Total number of pages analyzed
            issues: List of issue dictionaries with 'severity' field

        Returns:
            Dictionary with:
                - score: int (0-100)
                - grade: str ('A', 'B', 'C', 'D', 'F')
                - breakdown: dict with error counts by severity
        """
        if total_pages == 0:
            return {
                'score': 0,
                'grade': 'F',
                'breakdown': {
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'total': 0
                }
            }

        # Count errors by severity
        error_counts = {
            'high': 0,
            'medium': 0,
            'low': 0
        }

        for issue in issues:
            severity = issue.get('severity', 'medium').lower()
            if severity in error_counts:
                error_counts[severity] += 1

        # Calculate weighted error density
        weighted_errors = (
            error_counts['high'] * self.SEVERITY_WEIGHTS['high'] +
            error_counts['medium'] * self.SEVERITY_WEIGHTS['medium'] +
            error_counts['low'] * self.SEVERITY_WEIGHTS['low']
        )

        # Logarithmic penalty: equal densities give equal scores at any
        # site size, and the score keeps dropping smoothly past the point
        # where a linear scale would already be clamped at 0.
        error_density = weighted_errors / total_pages
        score = 100 * (
            1 - math.log10(1 + error_density)
            / math.log10(1 + self.MAX_ERROR_DENSITY)
        )
        score = max(0, min(100, score))

        # Round half-up and derive the letter from the rounded score so
        # the displayed score and the letter can never disagree.
        rounded_score = int(math.floor(score + 0.5))
        grade = self._get_grade_from_score(rounded_score)

        return {
            'score': rounded_score,
            'grade': grade,
            'breakdown': {
                'high': error_counts['high'],
                'medium': error_counts['medium'],
                'low': error_counts['low'],
                'total': len(issues)
            }
        }
    
    def _get_grade_from_score(self, score: float) -> str:
        """
        Convert score to grade letter.
        
        Args:
            score: Score value (0-100)
        
        Returns:
            Grade letter ('A', 'B', 'C', 'D', 'F')
        """
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_grade_color(self, grade: str) -> str:
        """
        Get color code for grade.
        
        Args:
            grade: Grade letter ('A', 'B', 'C', 'D', 'F')
        
        Returns:
            Color name or hex code
        """
        colors = {
            'A': 'green',
            'B': 'blue',
            'C': 'yellow',
            'D': 'orange',
            'F': 'red'
        }
        return colors.get(grade, 'gray')