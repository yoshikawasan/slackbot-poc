import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from slackbot_poc.csv_processor import validate_csv_format, check_comma_separation, process_csv_files, format_results_for_slack


class TestCSVProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.valid_csv = b"name,age,score\nAlice,25,100\nBob,30,85"
        self.invalid_csv = b"\x00\x01\x02\x03invalid binary content"
        self.semicolon_csv = b"name;age;score\nAlice;25;100\nBob;30;85"
        self.tab_csv = b"name\tage\tscore\nAlice\t25\t100\nBob\t30\t85"
        self.mixed_types_csv = b"name,age,height,score\nAlice,25,5.6,100\nBob,30,6.0,85"
    
    def test_validate_csv_format_valid(self):
        """Test validation with valid CSV."""
        result = validate_csv_format(self.valid_csv)
        self.assertTrue(result)
    
    def test_validate_csv_format_invalid(self):
        """Test validation with invalid CSV."""
        result = validate_csv_format(self.invalid_csv)
        self.assertFalse(result)
    
    def test_check_comma_separation_valid(self):
        """Test comma separation check with valid CSV."""
        result = check_comma_separation(self.valid_csv)
        self.assertTrue(result)
    
    def test_check_comma_separation_semicolon(self):
        """Test comma separation check with semicolon separated CSV."""
        result = check_comma_separation(self.semicolon_csv)
        self.assertFalse(result)
    
    def test_check_comma_separation_tab(self):
        """Test comma separation check with tab separated CSV."""
        result = check_comma_separation(self.tab_csv)
        self.assertFalse(result)
    
    def test_process_csv_files_valid_single(self):
        """Test processing single valid CSV file."""
        result = process_csv_files([self.valid_csv])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("Alice,50,200", result[0])  # age doubled: 25 -> 50, score: 100 -> 200
        self.assertIn("Bob,60,170", result[0])    # age doubled: 30 -> 60, score: 85 -> 170
    
    def test_process_csv_files_valid_multiple(self):
        """Test processing multiple valid CSV files."""
        result = process_csv_files([self.valid_csv, self.mixed_types_csv])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
    
    def test_process_csv_files_invalid_format(self):
        """Test processing invalid CSV format."""
        result = process_csv_files([self.invalid_csv])
        self.assertEqual(result, "Please send csv file")
    
    def test_process_csv_files_wrong_separator(self):
        """Test processing CSV with wrong separator."""
        result = process_csv_files([self.semicolon_csv])
        self.assertEqual(result, "Please send csv file with comma(,).")
    
    def test_process_csv_files_mixed_types(self):
        """Test processing CSV with mixed data types."""
        result = process_csv_files([self.mixed_types_csv])
        self.assertIsInstance(result, list)
        processed_content = result[0]
        self.assertIn("Alice,50,5.6,200", processed_content)  # age: 25->50, score: 100->200
        self.assertIn("Bob,60,6.0,170", processed_content)    # age: 30->60, score: 85->170
    
    def test_format_results_for_slack_single(self):
        """Test formatting single result for Slack."""
        results = ["name,age\nAlice,50\nBob,60"]
        formatted = format_results_for_slack(results)
        self.assertIn("```", formatted)
        self.assertIn("Alice,50", formatted)
    
    def test_format_results_for_slack_multiple(self):
        """Test formatting multiple results for Slack."""
        results = ["name,age\nAlice,50", "name,score\nBob,170"]
        formatted = format_results_for_slack(results)
        self.assertIn("**File 1:**", formatted)
        self.assertIn("**File 2:**", formatted)
        self.assertIn("Alice,50", formatted)
        self.assertIn("Bob,170", formatted)


if __name__ == '__main__':
    unittest.main()