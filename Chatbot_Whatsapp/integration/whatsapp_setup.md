

# WhatsApp Business API Setup Guide

This document outlines the steps required to configure WhatsApp Business API access and connect it with your chatbot backend.

## 1. Create or Access a WhatsApp Business Account

- Register a WhatsApp Business Account via [Facebook Business Manager](https://business.facebook.com/).
- Verify your business details and phone number.
- Obtain approval for your WhatsApp Business API usage.
- Alternatively, use a WhatsApp API provider (e.g., Twilio, 360dialog, Zenvia) for simplified onboarding.

## 2. Retrieve API Credentials

- After account approval, obtain your **Phone Number ID** and **Access Token (Bearer Token)**.
- Store these securely (do not hardcode in source code).
- For example, add them as environment variables:
  
  ```
  WHATSAPP_API_URL=https://graph.facebook.com/v16.0/<PHONE_NUMBER_ID>/messages
  WHATSAPP_TOKEN=EAA...XYOUR_ACCESS_TOKEN...uZB
  ```

## 3. Configure Webhook URL

- In the Facebook Developer Console or your provider dashboard:
  - Set your backend’s publicly accessible webhook URL (e.g., `https://yourdomain.com/whatsapp_webhook`).
  - Subscribe to message and status update events.
  - Verify webhook by responding to challenge requests as per documentation.

## 4. Webhook Payload Format

- Incoming messages from WhatsApp will arrive as POST requests containing JSON payloads.
- Your backend should parse the payload to extract:
  - Sender ID (phone number or user ID)
  - Message text or media
  - Message type, timestamps
- See official [WhatsApp API Webhook Docs](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/reference/) for details.

## 5. Sending Messages via API

- To send messages, make POST requests to the API URL (from step 2) with headers:
  
  ```
  Authorization: Bearer <YOUR_TOKEN>
  Content-Type: application/json
  ```

- JSON payload example for text message:
  
  ```json
  {
    "messaging_product": "whatsapp",
    "to": "<RECIPIENT_PHONE_NUMBER>",
    "type": "text",
    "text": { "body": "Hello from chatbot!" }
  }
  ```

- Refer to [WhatsApp Cloud API Message Types](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-message) for more formats.

## 6. Testing Your Integration

- Use tools like [Postman](https://www.postman.com/) or curl to test sending messages with your token.
- Run your backend and monitor webhook event reception.
- Test with a real WhatsApp account linked to your Business number.

## 7. Additional Considerations

- Respect WhatsApp messaging policies and rate limits.
- Template messages require prior approval for outbound notifications.
- Handle errors and retries gracefully in your backend.
- Keep tokens secret and rotate them as needed.

