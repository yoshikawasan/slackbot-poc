#!/usr/bin/env python3
"""
Test file upload functionality for the Slack CSV bot.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import slackbot_poc.bot as slack_bot
from slackbot_poc.csv_processor import process_csv_files


class TestFileUpload(unittest.TestCase):
    """Test file upload functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_csv_content = [b'name,age,score\nAlice,25,100\nBob,30,85']
        self.expected_result = ['name,age,score\nAlice,50,200\nBob,60,170\n']
        
        self.mock_file = {
            'id': 'F123456',
            'name': 'test_data.csv',
            'mimetype': 'text/csv'
        }
    
    def test_upload_single_file(self):
        """Test uploading a single processed CSV file."""
        print("Testing single file upload...")
        
        with patch.dict('os.environ', {'SLACK_BOT_TOKEN': 'test', 'SLACK_APP_TOKEN': 'test'}):
            with patch('slackbot_poc.bot.WebClient'):
                with patch('slackbot_poc.bot.SocketModeClient'):
                    bot = slack_bot.SlackCSVBot()
                    bot.client.files_upload_v2 = MagicMock()
                    
                    results = self.expected_result
                    original_files = [self.mock_file]
                    channel = 'C123456'
                    
                    bot.upload_processed_files(channel, results, original_files)
                    
                    bot.client.files_upload_v2.assert_called_once_with(
                        channel=channel,
                        content=results[0],
                        filename='processed_test_data.csv',
                        title='Processed test_data.csv',
                        initial_comment='CSV file processed - integer columns have been doubled! 📊'
                    )
        
        print("✓ Single file upload test passed")
    
    def test_upload_multiple_files(self):
        """Test uploading multiple processed CSV files."""
        print("Testing multiple file upload...")
        
        with patch.dict('os.environ', {'SLACK_BOT_TOKEN': 'test', 'SLACK_APP_TOKEN': 'test'}):
            with patch('slackbot_poc.bot.WebClient'):
                with patch('slackbot_poc.bot.SocketModeClient'):
                    bot = slack_bot.SlackCSVBot()
                    bot.client.files_upload_v2 = MagicMock()
                    bot.client.chat_postMessage = MagicMock()
                    
                    results = [
                        'name,age\nAlice,50\nBob,60\n',
                        'product,price\nApple,10\nBanana,6\n'
                    ]
                    original_files = [
                        {'id': 'F123', 'name': 'people.csv', 'mimetype': 'text/csv'},
                        {'id': 'F456', 'name': 'products.csv', 'mimetype': 'text/csv'}
                    ]
                    channel = 'C123456'
                    
                    bot.upload_processed_files(channel, results, original_files)
                    
                    expected_calls = [
                        call(
                            channel=channel,
                            content=results[0],
                            filename='processed_people.csv',
                            title='Processed people.csv',
                            initial_comment='Processed file 1/2: people.csv'
                        ),
                        call(
                            channel=channel,
                            content=results[1],
                            filename='processed_products.csv',
                            title='Processed products.csv',
                            initial_comment=None
                        )
                    ]
                    
                    bot.client.files_upload_v2.assert_has_calls(expected_calls)
                    bot.client.chat_postMessage.assert_called_once_with(
                        channel=channel,
                        text='✅ Successfully processed 2 CSV files! Integer columns have been doubled.'
                    )
        
        print("✓ Multiple file upload test passed")
    
    def test_upload_error_handling(self):
        """Test error handling during file upload."""
        print("Testing upload error handling...")
        
        from slack_sdk.errors import SlackApiError
        
        with patch.dict('os.environ', {'SLACK_BOT_TOKEN': 'test', 'SLACK_APP_TOKEN': 'test'}):
            with patch('slackbot_poc.bot.WebClient'):
                with patch('slackbot_poc.bot.SocketModeClient'):
                    bot = slack_bot.SlackCSVBot()
                    bot.client.files_upload_v2 = MagicMock()
                    bot.client.files_upload_v2.side_effect = SlackApiError("Upload failed", response={'error': 'upload_failed'})
                    bot.send_error_message = MagicMock()
                    
                    results = self.expected_result
                    original_files = [self.mock_file]
                    channel = 'C123456'
                    
                    bot.upload_processed_files(channel, results, original_files)
                    
                    bot.send_error_message.assert_called_once_with(
                        channel, 
                        "Error uploading processed CSV files"
                    )
        
        print("✓ Upload error handling test passed")
    
    def test_csv_processing_integration(self):
        """Test integration between CSV processing and file upload."""
        print("Testing CSV processing integration...")
        
        test_csv = b'name,age,score\nAlice,25,100\nBob,30,85'
        results = process_csv_files([test_csv])
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        
        content = results[0]
        self.assertIn('Alice,50,200', content)
        self.assertIn('Bob,60,170', content)
        
        lines = content.strip().split('\n')
        self.assertEqual(lines[0], 'name,age,score')
        self.assertEqual(len(lines), 3)
        
        print("✓ CSV processing integration test passed")


def run_file_upload_tests():
    """Run all file upload tests."""
    print("Slack CSV Bot - File Upload Tests")
    print("=" * 50)
    
    test_instance = TestFileUpload()
    test_instance.setUp()
    
    try:
        test_instance.test_upload_single_file()
        test_instance.test_upload_multiple_files()
        test_instance.test_upload_error_handling()
        test_instance.test_csv_processing_integration()
        
        print("\n" + "=" * 50)
        print("✅ All file upload tests PASSED!")
        print("\nNew functionality:")
        print("- Bot now uploads processed CSV files instead of text")
        print("- Files are named 'processed_[original_name].csv'")
        print("- Single files get a processing message")
        print("- Multiple files get individual uploads + summary")
        print("- Error handling for upload failures")
        
        return True
        
    except Exception as e:
        print(f"\n❌ File upload tests FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_file_upload_tests()
    if not success:
        exit(1)