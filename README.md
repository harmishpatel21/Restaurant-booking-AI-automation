# AI-Powered Restaurant Booking Management System

An intelligent restaurant booking management system with voice capabilities, calendar integration, and SMS notifications.

## Features

- Web-based booking interface
- Voice booking through web interface
- Phone call booking through Twilio
- SMS notifications for booking confirmations and reminders
- Restaurant management dashboard
- Comprehensive audit logging system
- Smart slot suggestion and availability management

## Prerequisites

Before you start, make sure you have the following:

### System Requirements

- Python 3.9 or higher
- PostgreSQL database
- Internet connection for external API services

### API Keys Required

The system relies on several external services. You'll need to obtain API keys for:

1. **OpenAI API Key**: For speech recognition and NLP processing
2. **ElevenLabs API Key**: For natural-sounding voice responses
3. **Twilio Account**: You'll need:
   - Twilio Account SID
   - Twilio Auth Token
   - Twilio Phone Number (purchased through Twilio)

## Installation (Local Development)

Follow these steps to set up the project on your local machine:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd restaurant-booking-system
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/restaurant_db
SESSION_SECRET=your_secret_key_here

# API Keys
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Optional Calendly Integration
CALENDLY_API_KEY=your_calendly_api_key
CALENDLY_ORGANIZATION=your_calendly_organization_id
CALENDLY_EVENT_TYPE=your_calendly_event_type_id
```

### 5. Create Database

```bash
# Using psql command line
psql -U postgres
CREATE DATABASE restaurant_db;
```

## Running the Application

### Start the Development Server

```bash
# Start the Flask development server
python main.py
```

The application will be available at http://localhost:5000

## Setting Up Twilio for Phone Call Booking

To enable phone call booking through Twilio, you need to configure your Twilio phone number to forward calls to your application:

1. Log into your [Twilio Console](https://www.twilio.com/console)
2. Navigate to "Phone Numbers" → "Manage" → "Active numbers"
3. Click on your Twilio phone number
4. Under the "Voice & Fax" section:
   - For "A call comes in", select "Webhook" 
   - Enter your webhook URL: `https://your-domain.com/twilio/incoming-call`
   - Make sure HTTP POST is selected
5. Save your changes

### For Local Development Testing with Twilio

For local development, you'll need to make your local server accessible to Twilio. 
You can use tools like [ngrok](https://ngrok.com/) to create a secure tunnel:

```bash
# Install ngrok
npm install -g ngrok

# Create a tunnel to your local server
ngrok http 5000
```

Use the ngrok-provided URL (e.g., `https://abc123.ngrok.io`) in your Twilio webhook configuration:
```
https://abc123.ngrok.io/twilio/incoming-call
```

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  Web Interface  │◄───┤  Flask Server   │◄───┤  PostgreSQL DB  │
│                 │    │                 │    │                 │
└────────┬────────┘    └────────┬────────┘    └─────────────────┘
         │                      │
         │                      │
┌────────▼────────┐    ┌────────▼────────┐
│                 │    │                 │
│  Voice Booking  │    │  Twilio Call    │
│  (Browser Mic)  │    │  Integration    │
│                 │    │                 │
└────────┬────────┘    └────────┬────────┘
         │                      │
         │                      │
┌────────▼────────┐    ┌────────▼────────┐
│                 │    │                 │
│ OpenAI Whisper  │    │  ElevenLabs     │
│ (Speech-to-Text)│    │  (Text-to-Speech)│
│                 │    │                 │
└─────────────────┘    └─────────────────┘
```

## API and Service Integrations

### OpenAI Whisper
Used for transcribing voice recordings to text for processing booking requests.

### ElevenLabs
Provides natural-sounding voice responses for the phone booking system.

### Twilio
Powers the phone call booking system and SMS notifications.

### Calendly (Optional)
Can be integrated for advanced scheduling and calendar management.

## Database Schema

The application uses the following core models:

- **Restaurant**: Store restaurant information
- **Booking**: Track customer reservations
- **AuditLog**: Record all system activities
- **VoiceInteraction**: Store voice conversation data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.