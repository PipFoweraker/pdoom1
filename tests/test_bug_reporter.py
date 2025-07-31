"""
Tests for the bug reporting system.

This module tests the functionality of the BugReporter class to ensure
privacy-focused bug reporting works correctly.
"""

import unittest
import os
import json
import tempfile
import shutil
from bug_reporter import BugReporter


class TestBugReporter(unittest.TestCase):
    """Test the BugReporter class functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        self.reporter = BugReporter()
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_bug_reporter_initialization(self):
        """Test that BugReporter initializes correctly."""
        self.assertIsInstance(self.reporter, BugReporter)
        self.assertEqual(self.reporter.reports_dir, "bug_reports")
        self.assertTrue(os.path.exists("bug_reports"))
    
    def test_system_info_collection(self):
        """Test that system information is collected correctly."""
        system_info = self.reporter.collect_system_info()
        
        # Check required fields
        self.assertIn("os_type", system_info)
        self.assertIn("python_version", system_info)
        self.assertIn("timestamp", system_info)
        
        # Check that only safe OS info is collected
        self.assertIn(system_info["os_type"], ["Linux", "Windows", "Darwin"])
        
        # Check Python version format
        self.assertRegex(system_info["python_version"], r"^\d+\.\d+$")
    
    def test_create_bug_report_minimal(self):
        """Test creating a bug report with minimal information."""
        report = self.reporter.create_bug_report(
            report_type="bug",
            title="Test bug",
            description="This is a test bug report"
        )
        
        # Check required fields
        self.assertEqual(report["report_type"], "bug")
        self.assertEqual(report["title"], "Test bug")
        self.assertEqual(report["description"], "This is a test bug report")
        self.assertIn("system_info", report)
        self.assertIn("created_at", report)
        self.assertIsNone(report["attribution"])
    
    def test_create_bug_report_with_attribution(self):
        """Test creating a bug report with attribution."""
        report = self.reporter.create_bug_report(
            report_type="feature_request",
            title="Add new feature",
            description="This would be a cool feature",
            include_attribution=True,
            attribution_name="Test User",
            contact_info="test@example.com"
        )
        
        self.assertEqual(report["report_type"], "feature_request")
        self.assertIsNotNone(report["attribution"])
        self.assertEqual(report["attribution"]["name"], "Test User")
        self.assertEqual(report["attribution"]["contact"], "test@example.com")
    
    def test_create_bug_report_without_attribution(self):
        """Test creating anonymous bug report."""
        report = self.reporter.create_bug_report(
            report_type="feedback",
            title="General feedback",
            description="Some feedback",
            include_attribution=False,
            attribution_name="Should be ignored"
        )
        
        self.assertIsNone(report["attribution"])
    
    def test_save_report_locally(self):
        """Test saving bug report to local file system."""
        report = self.reporter.create_bug_report(
            report_type="bug",
            title="Test save",
            description="Testing local save functionality"
        )
        
        filepath = self.reporter.save_report_locally(report)
        
        # Check file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.startswith("bug_reports/bug_report_"))
        self.assertTrue(filepath.endswith(".json"))
        
        # Check file content
        with open(filepath, 'r') as f:
            saved_report = json.load(f)
        
        self.assertEqual(saved_report["title"], "Test save")
        self.assertEqual(saved_report["description"], "Testing local save functionality")
    
    def test_format_for_github(self):
        """Test formatting bug report for GitHub issues."""
        report = self.reporter.create_bug_report(
            report_type="bug",
            title="GitHub test",
            description="Testing GitHub formatting",
            steps_to_reproduce="1. Step one\n2. Step two",
            expected_behavior="Should work",
            actual_behavior="Doesn't work",
            include_attribution=True,
            attribution_name="GitHub User"
        )
        
        github_format = self.reporter.format_for_github(report)
        
        # Check title format
        self.assertEqual(github_format["title"], "[Bug] GitHub test")
        
        # Check body contains required sections
        body = github_format["body"]
        self.assertIn("**Type:** Bug", body)
        self.assertIn("**Description:**", body)
        self.assertIn("Testing GitHub formatting", body)
        self.assertIn("**Steps to Reproduce:**", body)
        self.assertIn("1. Step one", body)
        self.assertIn("**Expected Behavior:**", body)
        self.assertIn("Should work", body)
        self.assertIn("**Actual Behavior:**", body)
        self.assertIn("Doesn't work", body)
        self.assertIn("**System Information:**", body)
        self.assertIn("**Reported by:** GitHub User", body)
    
    def test_format_for_github_anonymous(self):
        """Test formatting anonymous bug report for GitHub."""
        report = self.reporter.create_bug_report(
            report_type="feature_request",
            title="Anonymous feature",
            description="Anonymous feature request"
        )
        
        github_format = self.reporter.format_for_github(report)
        
        self.assertEqual(github_format["title"], "[Feature Request] Anonymous feature")
        self.assertIn("**Reported by:** Anonymous", github_format["body"])
    
    def test_get_recent_reports_empty(self):
        """Test getting recent reports when none exist."""
        reports = self.reporter.get_recent_reports()
        self.assertEqual(reports, [])
    
    def test_get_recent_reports_with_files(self):
        """Test getting recent reports when files exist."""
        # Create some test reports
        report1 = self.reporter.create_bug_report("bug", "First", "First report")
        report2 = self.reporter.create_bug_report("bug", "Second", "Second report")
        
        file1 = self.reporter.save_report_locally(report1)
        
        # Small delay to ensure different timestamps
        import time
        time.sleep(0.01)
        
        file2 = self.reporter.save_report_locally(report2)
        
        recent = self.reporter.get_recent_reports()
        
        # Should have both files
        self.assertGreaterEqual(len(recent), 2)
        self.assertIn(file1, recent)
        self.assertIn(file2, recent)


class TestBugReporterPrivacy(unittest.TestCase):
    """Test privacy aspects of bug reporting."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        self.reporter = BugReporter()
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_no_personal_info_in_system_data(self):
        """Test that system info contains no personal information."""
        system_info = self.reporter.collect_system_info()
        
        # Should not contain username, hostname, or detailed system info
        for key, value in system_info.items():
            self.assertNotIn("user", str(value).lower())
            self.assertNotIn("home", str(value).lower())
            self.assertNotIn("admin", str(value).lower())
        
        # OS type should be generic
        self.assertIn(system_info["os_type"], ["Linux", "Windows", "Darwin"])
    
    def test_attribution_optional(self):
        """Test that attribution is completely optional."""
        # Without attribution
        report_anon = self.reporter.create_bug_report(
            "bug", "Anonymous", "No attribution",
            include_attribution=False
        )
        self.assertIsNone(report_anon["attribution"])
        
        # With attribution
        report_credited = self.reporter.create_bug_report(
            "bug", "Credited", "With attribution",
            include_attribution=True,
            attribution_name="Test User"
        )
        self.assertIsNotNone(report_credited["attribution"])
        self.assertEqual(report_credited["attribution"]["name"], "Test User")
    
    def test_contact_info_optional(self):
        """Test that contact information is optional even with attribution."""
        report = self.reporter.create_bug_report(
            "bug", "No contact", "Attribution without contact",
            include_attribution=True,
            attribution_name="User",
            contact_info=""
        )
        
        self.assertIsNotNone(report["attribution"])
        self.assertEqual(report["attribution"]["name"], "User")
        self.assertIsNone(report["attribution"]["contact"])


if __name__ == "__main__":
    unittest.main()