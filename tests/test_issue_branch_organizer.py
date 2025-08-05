#!/usr/bin/env python3
"""
Tests for the Issue Branch Organizer tool

This ensures that the branch organization logic works correctly
and produces consistent results.
"""

import unittest
import json
import os
import sys

# Add parent directory to path to import the organizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from issue_branch_organizer import IssueBranchOrganizer, Issue, Branch

class TestIssueBranchOrganizer(unittest.TestCase):
    """Test the Issue Branch Organizer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.organizer = IssueBranchOrganizer()
        
        # Create test issues
        self.test_issues = [
            Issue(1, "UI bug fix", "Fix button click", ["bug"], "", "2025-01-01", False),
            Issue(2, "Add sound system", "Implement audio", ["enhancement"], "", "2025-01-01", False),
            Issue(3, "Action points system", "Complex game mechanic", ["enhancement"], "", "2025-01-01", False),
            Issue(4, "Release checklist", "Version 1.0 prep", ["documentation"], "", "2025-01-01", False),
            Issue(5, "Employee hiring", "Advanced staff system", ["enhancement"], "", "2025-01-01", False),
        ]
        
        self.organizer.issues_without_prs = self.test_issues
    
    def test_issue_complexity_scoring(self):
        """Test that complexity scoring works correctly"""
        simple_issue = Issue(1, "Fix bug", "Simple fix", ["bug"], "", "2025-01-01", False)
        complex_issue = Issue(2, "System overhaul", "Major architectural change with acceptance criteria and testing requirements", ["enhancement"], "", "2025-01-01", False)
        
        self.assertLessEqual(simple_issue.get_complexity_score(), complex_issue.get_complexity_score())
        self.assertGreaterEqual(complex_issue.get_complexity_score(), 2)
    
    def test_issue_categorization(self):
        """Test that issues are categorized correctly"""
        categories = self.organizer.categorize_issues()
        
        # Should have 5 categories
        self.assertEqual(len(categories), 5)
        
        # Should categorize at least some issues
        total_categorized = sum(len(issues) for issues in categories.values())
        self.assertEqual(total_categorized, len(self.test_issues))
    
    def test_branch_suggestion(self):
        """Test that branch suggestions are generated correctly"""
        branches = self.organizer.suggest_branches()
        
        # Should suggest exactly 5 branches
        self.assertEqual(len(branches), 5)
        
        # All branches should have names, descriptions, and themes
        for branch in branches:
            self.assertIsNotNone(branch.name)
            self.assertIsNotNone(branch.description)
            self.assertIsNotNone(branch.theme)
            self.assertIsInstance(branch.issues, list)
        
        # Total issues should be preserved
        total_issues = sum(len(branch.issues) for branch in branches)
        self.assertEqual(total_issues, len(self.test_issues))
    
    def test_branch_names_are_valid(self):
        """Test that generated branch names follow conventions"""
        branches = self.organizer.suggest_branches()
        
        for branch in branches:
            # Should be feature branches
            self.assertTrue(branch.name.startswith("feature/"))
            
            # Should not contain spaces or special characters
            self.assertNotIn(" ", branch.name)
            self.assertNotIn("_", branch.name)  # Use hyphens instead
    
    def test_report_generation(self):
        """Test that report generation works"""
        report = self.organizer.generate_report()
        
        # Report should be a non-empty string
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 100)
        
        # Should contain key sections
        self.assertIn("# Issue Branch Organization Analysis", report)
        self.assertIn("## Executive Summary", report)
        self.assertIn("## Recommended Branch Strategy", report)
        self.assertIn("## Implementation Strategy", report)
    
    def test_existing_pr_exclusion(self):
        """Test that issues with existing PRs are excluded"""
        self.organizer.load_issues_from_data()
        
        # Should exclude known PR issues
        issue_numbers = [issue.number for issue in self.organizer.issues_without_prs]
        
        for pr_issue in self.organizer.existing_prs:
            self.assertNotIn(pr_issue, issue_numbers)
    
    def test_json_export(self):
        """Test JSON data export functionality"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_filename = f.name
        
        try:
            self.organizer.save_json_data(temp_filename)
            
            # File should exist
            self.assertTrue(os.path.exists(temp_filename))
            
            # Should be valid JSON
            with open(temp_filename, 'r') as f:
                data = json.load(f)
            
            # Should have expected structure
            self.assertIn('analysis_date', data)
            self.assertIn('total_issues', data)
            self.assertIn('branches', data)
            self.assertEqual(len(data['branches']), 5)
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

class TestIssueComplexityLogic(unittest.TestCase):
    """Test the complexity scoring logic in detail"""
    
    def test_bug_vs_enhancement_complexity(self):
        """Test that bugs are generally scored as less complex"""
        bug_issue = Issue(1, "Fix crash", "Button doesn't work", ["bug"], "", "2025-01-01", False)
        enhancement_issue = Issue(2, "Add feature", "New complex system with acceptance criteria", ["enhancement"], "", "2025-01-01", False)
        
        # Enhancement should typically be more complex than bug fix
        self.assertLessEqual(bug_issue.get_complexity_score(), enhancement_issue.get_complexity_score() + 1)
    
    def test_keyword_complexity_scoring(self):
        """Test that complexity keywords affect scoring correctly"""
        simple_issue = Issue(1, "Fix button", "Quick fix", [], "", "2025-01-01", False)
        system_issue = Issue(2, "System overhaul", "Major changes", [], "", "2025-01-01", False)
        
        self.assertLess(simple_issue.get_complexity_score(), system_issue.get_complexity_score())
    
    def test_body_length_affects_complexity(self):
        """Test that longer issue descriptions increase complexity"""
        short_issue = Issue(1, "Fix", "Short", [], "", "2025-01-01", False)
        long_body = "Long description " * 100  # Create long body
        long_issue = Issue(2, "Fix", long_body, [], "", "2025-01-01", False)
        
        self.assertLessEqual(short_issue.get_complexity_score(), long_issue.get_complexity_score())

if __name__ == '__main__':
    unittest.main()