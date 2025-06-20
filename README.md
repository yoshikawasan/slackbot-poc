# Slack CSV Processing Bot

A Python-based Slack bot that processes CSV files by doubling integer values in columns.

## Features

- Processes CSV files uploaded to Slack channels
- Doubles all integer values in CSV columns
- Supports multiple CSV files in a single message
- Validates CSV format and comma separation
- Returns appropriate error messages for invalid inputs

## Requirements

- Python 3.12+
- uv (Python package manager)
- Slack workspace with bot permissions

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Create Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app "From scratch"
3. Add the following OAuth scopes in "OAuth & Permissions":
   - `chat:write` - Send messages
   - `files:read` - Read file contents
   - `files:write` - Upload processed files
   - `app_mentions:read` - Read mentions
   - `channels:history` - Read channel messages
   - `groups:history` - Read private channel messages
   - `im:history` - Read direct messages
   - `mpim:history` - Read group messages

### 2. Event Subscriptions Setup

Verify that the following settings are correctly configured in your Slack App settings:

- **Event Subscriptions** is enabled
- **Subscribe to bot events** includes `message.channels` or `message.groups`
- **OAuth & Permissions** has appropriate scopes configured (e.g., `chat:write`, `files:read`, etc.)

### 3. Enable Socket Mode

1. Go to "Socket Mode" in your app settings
2. Enable Socket Mode
3. Generate an App-Level Token with `connections:write` scope
4. Copy the App Token (starts with `xapp-`)

### 4. Install App to Workspace

1. Go to "Install App" and install to your workspace
2. Copy the Bot User OAuth Token (starts with `xoxb-`)

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your tokens:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
```

## Usage

### Start the Bot

```bash
uv run python main.py
# or using the installed script:
uv run slackbot-poc
```

You should see:
```
INFO:__main__:Starting Slack CSV Bot...
```

### Using the Bot

1. **Send CSV file**: Upload a CSV file to any channel where the bot is invited
   - The bot will process the file and double all integer columns
   - Returns the processed CSV as a downloadable file attachment

2. **Send message without CSV**: Send any text message
   - Bot responds: "Please send csv file"

3. **Send non-comma separated CSV**: Upload CSV with semicolon or tab separation
   - Bot responds: "Please send csv file with comma(,)."

### Example

**Input CSV:**
```csv
name,age,score
Alice,25,100
Bob,30,85
```

**Bot Output:**
- Uploads a file named `processed_data.csv` with content:
```csv
name,age,score
Alice,50,200
Bob,60,170
```
- Shows message: "CSV file processed - integer columns have been doubled! 📊"

## Development

### Run Tests

```bash
# Run all tests
cd tests && uv run python run_all_tests.py

# Run specific test suites
cd tests && uv run python test_csv_processor.py
cd tests && uv run python test_server_integration.py
cd tests && uv run python test_file_upload.py
```

### Project Structure

```
slackbot-poc/






```

## Error Handling

The bot handles various error cases:

- **Invalid file format**: "Please send csv file"
- **Wrong separator**: "Please send csv file with comma(,)."
- **No file attached**: "Please send csv file"
- **Download errors**: "Failed to download CSV file"
- **Processing errors**: "Error processing file X: [error details]"

## Troubleshooting

1. **Bot not responding**: Check if the bot is invited to the channel
2. **Permission errors**: Verify OAuth scopes are correctly set
3. **Token errors**: Ensure tokens are valid and properly configured
4. **File processing errors**: Check if the CSV file uses comma separation

## License

MIT License