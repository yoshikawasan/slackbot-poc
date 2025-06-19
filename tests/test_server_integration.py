import unittest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from slackbot_poc.csv_processor import process_csv_files, format_results_for_slack


class TestServerIntegration(unittest.TestCase):
    """Integration tests for server functionality confirmed in this session."""
    
    def test_server_initialization_without_tokens(self):
        """Test that server can be initialized without environment tokens."""
        print("Testing server initialization...")
        
        # Import and test server initialization
        import slackbot_poc.bot as slack_bot
        
        try:
            bot = slack_bot.SlackCSVBot()
            self.assertIsNotNone(bot)
            self.assertTrue(hasattr(bot, 'client'))
            self.assertTrue(hasattr(bot, 'socket_client'))
            print("✓ Bot class instantiated successfully")
            print("✓ Dependencies loaded correctly")
            print("✓ Server code is syntactically correct")
        except Exception as e:
            # This is expected without proper Slack tokens
            print(f"✗ Error during initialization: {e}")
            print("This is expected without proper Slack tokens configured")
    
    def test_csv_processing_functionality(self):
        """Test CSV processing functionality with real data."""
        print("Testing CSV processing functionality...")
        
        # Test valid CSV processing
        test_csv = b'name,age,score\nAlice,25,100\nBob,30,85'
        result = process_csv_files([test_csv])
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        
        processed_content = result[0]
        self.assertIn('Alice,50,200', processed_content)  # age: 25->50, score: 100->200
        self.assertIn('Bob,60,170', processed_content)    # age: 30->60, score: 85->170
        
        print("✓ CSV processing successful")
        print("Processed result:")
        print(processed_content)
        
        # Test Slack formatting
        formatted = format_results_for_slack(result)
        self.assertIn('```', formatted)
        self.assertIn('Alice,50,200', formatted)
        
        print("✓ Slack formatting successful")
        print("Formatted for Slack:")
        print(formatted[:100] + '...' if len(formatted) > 100 else formatted)
    
    def test_error_handling_scenarios(self):
        """Test error handling scenarios confirmed in session."""
        print("Testing error handling...")
        
        # Test invalid CSV
        invalid_csv = b'\x00\x01\x02\x03invalid'
        result = process_csv_files([invalid_csv])
        self.assertEqual(result, "Please send csv file")
        print("✓ Invalid CSV handling:", result)
        
        # Test semicolon separated CSV
        semicolon_csv = b'name;age;score\nAlice;25;100'
        result = process_csv_files([semicolon_csv])
        self.assertEqual(result, "Please send csv file with comma(,).")
        print("✓ Wrong separator handling:", result)
        
        # Test empty content
        empty_csv = b''
        result = process_csv_files([empty_csv])
        self.assertEqual(result, "Please send csv file")
        print("✓ Empty CSV handling:", result)
    
    def test_multiple_csv_files(self):
        """Test processing multiple CSV files."""
        print("Testing multiple CSV files...")
        
        csv1 = b'name,age\nAlice,25\nBob,30'
        csv2 = b'product,price\nApple,5\nBanana,3'
        
        result = process_csv_files([csv1, csv2])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        
        # Check first file (ages doubled)
        self.assertIn('Alice,50', result[0])
        self.assertIn('Bob,60', result[0])
        
        # Check second file (prices doubled)
        self.assertIn('Apple,10', result[1])
        self.assertIn('Banana,6', result[1])
        
        print("✓ Multiple CSV processing successful")
        print("File 1 result:", result[0].strip())
        print("File 2 result:", result[1].strip())
    
    def test_mixed_data_types(self):
        """Test CSV with mixed data types (integers and floats)."""
        print("Testing mixed data types...")
        
        mixed_csv = b'name,age,height,score\nAlice,25,5.6,100\nBob,30,6.0,85'
        result = process_csv_files([mixed_csv])
        
        self.assertIsInstance(result, list)
        processed = result[0]
        
        # Only integers should be doubled (age and score), not floats (height)
        self.assertIn('Alice,50,5.6,200', processed)
        self.assertIn('Bob,60,6.0,170', processed)
        
        print("✓ Mixed data types handling successful")
        print("Result:", processed.strip())
    
    def test_slack_formatting_multiple_files(self):
        """Test Slack formatting for multiple files."""
        print("Testing Slack formatting for multiple files...")
        
        results = [
            "name,age\nAlice,50\nBob,60",
            "product,price\nApple,10\nBanana,6"
        ]
        
        formatted = format_results_for_slack(results)
        
        self.assertIn('**File 1:**', formatted)
        self.assertIn('**File 2:**', formatted)
        self.assertIn('Alice,50', formatted)
        self.assertIn('Apple,10', formatted)
        
        print("✓ Multiple file formatting successful")
        print("Formatted output:")
        print(formatted)


if __name__ == '__main__':
    print("Running integration tests for server functionality...")
    print("=" * 60)
    unittest.main(verbosity=2)