# Twilio Voice Call Integration Guide

This guide explains how to set up and test the Twilio voice call integration for the restaurant booking system.

## Prerequisites

Before you start, you'll need:

1. A Twilio account (can be a free trial account)
2. A Twilio phone number with voice capabilities
3. Your Twilio Account SID and Auth Token
4. Your application deployed and accessible via a public URL

## Setting Up Twilio Credentials

1. Add your Twilio credentials to your environment variables:

```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number  # Include country code, e.g., +15551234567
```

## Configuring Your Twilio Phone Number

1. Log in to your [Twilio Console](https://www.twilio.com/console)
2. Navigate to "Phone Numbers" → "Manage" → "Active numbers"
3. Click on your Twilio phone number
4. Under the "Voice & Fax" section:
   - For "A call comes in", select "Webhook" 
   - Enter your webhook URL: `https://your-domain.com/twilio/incoming-call`
   - Make sure HTTP POST is selected
5. Save your changes

![Twilio Voice Configuration Example](https://i.imgur.com/xxxxxxx.png)

## Testing Your Voice Call Integration

### Option 1: Testing with a Real Phone Call

1. Ensure your application is deployed and running
2. Call your Twilio phone number from your mobile phone
3. You should hear the welcome message: "Welcome to our restaurant booking system..."
4. Follow the voice prompts to make a test booking

### Option 2: Testing with Twilio's Call Simulator

1. Navigate to "Phone Numbers" → "Manage" → "Active numbers" in your Twilio Console
2. Click on your Twilio phone number
3. Scroll down to "Call" under "Test"
4. Click "Call" to simulate an incoming call to your webhook
5. You should see the webhook request and response in real-time

## Debugging Common Issues

### 1. Call connects but no response from application

This usually means that Twilio can reach your webhook URL, but there's an error in your application.

**Solution**: Check your application logs for errors.

### 2. Error: "Failed to download TwiML"

This means Twilio couldn't reach your webhook URL.

**Solutions**:
- Ensure your application is running and accessible from the internet
- Check that your webhook URL is correct in the Twilio console
- Verify that your server accepts POST requests at the webhook endpoint

### 3. Call connects but there's no audio

This could be due to TwiML generation errors.

**Solution**: Check that your TwiML responses are valid. You can use Twilio's TwiML Bin feature to test simple TwiML responses.

### 4. The voice doesn't understand what I'm saying

Speech recognition quality depends on multiple factors.

**Solutions**:
- Speak clearly and in a quiet environment
- Check if the Gather verb in your TwiML has appropriate timeout settings
- Review the speech recognition settings in your TwiML

## Understanding the Voice Call Flow

Our voice call integration follows this conversation flow:

1. **Greeting**: The system introduces itself and asks for the caller's name
2. **Name Collection**: Collects the caller's name
3. **Party Size**: Asks and collects the party size
4. **Date Selection**: Asks for the preferred date
5. **Time Selection**: Asks for the preferred time 
6. **Alternative Suggestion**: If the requested time isn't available, suggests alternatives
7. **Confirmation**: Confirms all details before finalizing the booking

## Testing the Flow with Specific Inputs

Here are some test scenarios to try:

1. **Happy Path**: All requested times are available
   - Name: "John Smith"
   - Party Size: "4 people"
   - Date: "tomorrow"
   - Time: "7 PM"
   - Confirmation: "yes"

2. **Alternative Time Suggestion**: Requested time unavailable
   - Name: "Jane Doe"
   - Party Size: "2 people"
   - Date: "Friday"
   - Time: "12:00" (This should be unavailable as we configured it in the mock data)
   - Alternative: Select one of the suggested times
   - Confirmation: "yes"

## Advanced: Testing with ngrok for Local Development

If you want to test the voice integration without deploying your application, you can use ngrok:

1. Install ngrok:
   ```bash
   npm install -g ngrok
   ```

2. Start your Flask application locally:
   ```bash
   python main.py
   ```

3. Create a secure tunnel with ngrok:
   ```bash
   ngrok http 5000
   ```

4. Update your Twilio webhook URL with the ngrok URL:
   ```
   https://your-ngrok-subdomain.ngrok.io/twilio/incoming-call
   ```

5. Now you can test calls while running your application locally

## Advanced: Customizing the Voice

Our implementation uses Twilio's Polly.Matthew voice. You can customize this by changing the voice parameter in the TwiML responses:

```python
response.say(
    "Welcome message here",
    voice='Polly.Joanna'  # Use a different voice
)
```

Available Polly voices include:
- Polly.Matthew (male)
- Polly.Joanna (female)
- Polly.Salli (female)
- Polly.Joey (male)

## Troubleshooting the Voice Application

If you're having issues with the voice call flow, you can debug by:

1. Adding more logging in your Flask routes
2. Checking the conversation_states dictionary for the current state
3. Testing specific route endpoints directly with simulated POST requests
4. Using Twilio's API Explorer to test individual API calls

Remember to also check the audit logs in your application's database for debugging information about each call.