#!/usr/bin/env python3
"""
Main entry point for the Slack CSV bot.
"""

from .bot import SlackCSVBot


def main():
    """Main function to start the Slack CSV bot."""
    bot = SlackCSVBot()
    bot.start()


if __name__ == "__main__":
    main()