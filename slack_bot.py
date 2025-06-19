import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from dotenv import load_dotenv
from csv_processor import process_csv_files, format_results_for_slack

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlackCSVBot:
    def __init__(self):
        self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.socket_client = SocketModeClient(
            app_token=os.environ.get("SLACK_APP_TOKEN"),
            web_client=self.client
        )
        self.socket_client.socket_mode_request_listeners.append(self.process_request)
    
    def process_request(self, client: SocketModeClient, req: SocketModeRequest):
        """Process incoming Slack events."""
        if req.type == "events_api":
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
            
            event = req.payload["event"]
            if event["type"] == "message" and "files" not in event:
                if "bot_id" not in event:
                    self.handle_message_without_files(event)
            elif event["type"] == "message" and "files" in event:
                if "bot_id" not in event:
                    self.handle_message_with_files(event)
    
    def handle_message_without_files(self, event):
        """Handle messages without file attachments."""
        try:
            self.client.chat_postMessage(
                channel=event["channel"],
                text="Please send csv file"
            )
        except SlackApiError as e:
            logger.error(f"Error sending message: {e}")
    
    def handle_message_with_files(self, event):
        """Handle messages with file attachments."""
        files = event.get("files", [])
        csv_files = []
        
        for file in files:
            if file.get("mimetype") == "text/csv" or file.get("name", "").endswith(".csv"):
                csv_files.append(file)
        
        if not csv_files:
            try:
                self.client.chat_postMessage(
                    channel=event["channel"],
                    text="Please send csv file"
                )
            except SlackApiError as e:
                logger.error(f"Error sending message: {e}")
            return
        
        self.process_csv_files(event["channel"], csv_files)
    
    def process_csv_files(self, channel, csv_files):
        """Download and process CSV files."""
        file_contents = []
        
        for file in csv_files:
            try:
                response = self.client.files_info(file=file["id"])
                file_url = response["file"]["url_private"]
                
                file_response = self.client.api_call(
                    "files.info",
                    params={"file": file["id"]},
                    headers={"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
                )
                
                import requests
                headers = {"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
                download_response = requests.get(file_url, headers=headers)
                
                if download_response.status_code == 200:
                    file_contents.append(download_response.content)
                else:
                    logger.error(f"Failed to download file: {file['name']}")
                    self.send_error_message(channel, "Failed to download CSV file")
                    return
                    
            except Exception as e:
                logger.error(f"Error downloading file {file['name']}: {e}")
                self.send_error_message(channel, "Error downloading CSV file")
                return
        
        results = process_csv_files(file_contents)
        
        if isinstance(results, str):
            try:
                self.client.chat_postMessage(
                    channel=channel,
                    text=results
                )
            except SlackApiError as e:
                logger.error(f"Error sending message: {e}")
        else:
            formatted_results = format_results_for_slack(results)
            try:
                self.client.chat_postMessage(
                    channel=channel,
                    text=formatted_results
                )
            except SlackApiError as e:
                logger.error(f"Error sending message: {e}")
    
    def send_error_message(self, channel, message):
        """Send error message to channel."""
        try:
            self.client.chat_postMessage(
                channel=channel,
                text=message
            )
        except SlackApiError as e:
            logger.error(f"Error sending error message: {e}")
    
    def start(self):
        """Start the bot."""
        logger.info("Starting Slack CSV Bot...")
        self.socket_client.connect()


if __name__ == "__main__":
    bot = SlackCSVBot()
    bot.start()