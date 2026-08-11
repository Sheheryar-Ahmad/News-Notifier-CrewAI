import os
import requests
from crewai.tools import tool

@tool("Send to Slack")
def send_to_slack(summary_text: str) -> str:
    """
    Sends a text summary to a Slack channel using an Incoming Webhook.
    Input should be the finalized text summary you want to post.
    """
    # Grab the URL we saved in the .env file
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        return "Error: SLACK_WEBHOOK_URL is not found in the environment variables."
        
    # Package the text exactly how Slack expects it
    payload = {"text": summary_text}
    
    try:
        # Send the POST request
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status() # This checks if the request was successful
        
        return f"Success! Message posted to Slack."
        
    except requests.exceptions.RequestException as e:
        # If something goes wrong (like no internet), this catches the error
        return f"Failed to send message to Slack. Error: {e}"