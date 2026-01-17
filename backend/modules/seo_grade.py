"""
SEO Grade Calculator Module

Calculates SEO grade based on error density and severity.
Uses US grading system: A (90-100%), B (80-89%), C (70-79%), D (60-69%), F (0-59%)
"""

from typing import List, Dict


class SEOGradeCalculator:
    """Calculates SEO grade based on error density."""
    
    # Severity weights for penalty calculation
    SEVERITY_WEIGHTS = {
        'high': 8,
        'medium': 3,
        'low': 1
    }
    
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
        
        # Calculate score (0-100)
        error_density = weighted_errors / total_pages
        score = max(0, min(100, 100 - (error_density * 100)))
        
        # Determine grade
        grade = self._get_grade_from_score(score)
        
        return {
            'score': int(round(score)),
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