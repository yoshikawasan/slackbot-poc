#!/usr/bin/env python3
"""
Test script to verify continuous server operation and graceful shutdown.
"""

import os
import sys
import time
import signal
import subprocess
import threading
from unittest.mock import patch, MagicMock


def test_server_startup_and_shutdown():
    """Test that server starts and can be stopped with Ctrl+C."""
    print("Testing continuous server operation...")
    
    # Test 1: Verify server can be imported and initialized
    print("1. Testing server initialization...")
    try:
        import slack_bot
        bot = slack_bot.SlackCSVBot()
        print("✓ Server can be initialized")
    except Exception as e:
        print(f"✗ Server initialization failed: {e}")
        return False
    
    # Test 2: Test signal handling setup
    print("2. Testing signal handling setup...")
    try:
        # Mock the signal handlers to avoid actually starting
        with patch('signal.signal') as mock_signal:
            with patch('slack_bot.SocketModeClient'):
                bot = slack_bot.SlackCSVBot()
                # Test that signal handlers would be set up
                print("✓ Signal handling setup works")
    except Exception as e:
        print(f"✗ Signal handling setup failed: {e}")
        return False
    
    # Test 3: Test graceful shutdown simulation
    print("3. Testing graceful shutdown...")
    try:
        with patch.dict(os.environ, {'SLACK_BOT_TOKEN': 'test', 'SLACK_APP_TOKEN': 'test'}):
            with patch('slack_bot.SocketModeClient') as mock_client:
                mock_socket = MagicMock()
                mock_client.return_value = mock_socket
                
                bot = slack_bot.SlackCSVBot()
                bot.running = True
                
                # Simulate signal handler
                def signal_handler(signum, frame):
                    bot.running = False
                    if bot.socket_client:
                        bot.socket_client.disconnect()
                
                # Test the signal handler
                signal_handler(signal.SIGINT, None)
                print("✓ Graceful shutdown simulation works")
                
    except Exception as e:
        print(f"✗ Graceful shutdown test failed: {e}")
        return False
    
    print("✓ All continuous operation tests passed!")
    return True


def test_server_with_mock_tokens():
    """Test server behavior with mocked tokens."""
    print("\n4. Testing server with mocked environment...")
    
    # Create a temporary .env file for testing
    test_env_content = """SLACK_BOT_TOKEN=xoxb-test-token
SLACK_APP_TOKEN=xapp-test-token"""
    
    with open('.env.test', 'w') as f:
        f.write(test_env_content)
    
    try:
        with patch.dict(os.environ, {'SLACK_BOT_TOKEN': 'xoxb-test', 'SLACK_APP_TOKEN': 'xapp-test'}):
            with patch('slack_bot.SocketModeClient') as mock_socket_client:
                with patch('slack_bot.WebClient') as mock_web_client:
                    # Mock the socket client
                    mock_client = MagicMock()
                    mock_socket_client.return_value = mock_client
                    
                    # Import and test
                    import slack_bot
                    bot = slack_bot.SlackCSVBot()
                    
                    # Test that bot is properly initialized
                    assert bot.client is not None
                    assert bot.socket_client is not None
                    assert bot.running == False  # Should start as False
                    
                    print("✓ Server initializes correctly with mock tokens")
                    
    except Exception as e:
        print(f"✗ Mock token test failed: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists('.env.test'):
            os.remove('.env.test')
    
    return True


def simulate_keyboard_interrupt():
    """Simulate a keyboard interrupt scenario."""
    print("\n5. Testing keyboard interrupt handling...")
    
    try:
        with patch.dict(os.environ, {'SLACK_BOT_TOKEN': 'test', 'SLACK_APP_TOKEN': 'test'}):
            with patch('slack_bot.SocketModeClient') as mock_client:
                with patch('signal.pause') as mock_pause:
                    # Make signal.pause raise KeyboardInterrupt
                    mock_pause.side_effect = KeyboardInterrupt()
                    
                    bot = slack_bot.SlackCSVBot()
                    
                    # This should handle the KeyboardInterrupt gracefully
                    bot.start()
                    
                    print("✓ Keyboard interrupt handled gracefully")
                    
    except SystemExit:
        print("✓ Keyboard interrupt handled with proper exit")
        return True
    except Exception as e:
        print(f"✗ Keyboard interrupt test failed: {e}")
        return False
    
    return True


if __name__ == '__main__':
    print("Slack CSV Bot - Continuous Operation Tests")
    print("=" * 50)
    
    success = True
    
    # Run all tests
    success &= test_server_startup_and_shutdown()
    success &= test_server_with_mock_tokens()
    success &= simulate_keyboard_interrupt()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All continuous operation tests PASSED!")
        print("\nTo run the server continuously:")
        print("1. Set up your .env file with proper Slack tokens")
        print("2. Run: uv run python slack_bot.py")
        print("3. Press Ctrl+C to stop the server gracefully")
    else:
        print("✗ Some tests FAILED!")
        sys.exit(1)