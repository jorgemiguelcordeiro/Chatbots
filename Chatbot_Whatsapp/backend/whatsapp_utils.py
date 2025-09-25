#whatsapp_utils.py
import requests
import os
import logging

logger = logging.getLogger("whatsapp_utils")

# Your WhatsApp API credentials and endpoint (update accordingly)
#Both are read from environment variables (.env file, GitHub Secrets, etc.), not hardcoded → safer.
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")  # e.g. "https://graph.facebook.com/v16.0/<phone-number-id>/messages"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")      # Your WhatsApp Business API bearer token

def send_whatsapp_message(recipient_id: str, message_text: str) -> bool:
    """
    Send a text message via WhatsApp Business API.

    Args:
        recipient_id (str): The WhatsApp user ID (phone number or ID from webhook).
        message_text (str): The text message to send from the chatbot to the whatsapp.

    Returns:
        bool: True on success, False on failure.
    """
    if not WHATSAPP_API_URL or not WHATSAPP_TOKEN:  #credentials check
        logger.error("WhatsApp API URL or Token not set in environment.")
        return False

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}", #Standard OAuth 2.0 style auth.
        "Content-Type": "application/json"
    }
    # this is what the Whatsapp api expects
    payload = {
        "messaging_product": "whatsapp", #tells meta it is for whatsapp
        "to": recipient_id, #user's phone number
        "type": "text", #we are sending plain text
        "text": {
            "body": message_text # the actual reply
        }
    }

    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload) #it sends the message. 
        response.raise_for_status() #throws an error
        logger.info(f"Sent WhatsApp message to {recipient_id}") #if it is sucessful , sent a message to {recipient_id}
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to {recipient_id}: {e}") #if it fails to send a message 
        return False

