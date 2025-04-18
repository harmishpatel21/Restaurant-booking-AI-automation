import json
import os
from datetime import datetime, timedelta
from flask import Blueprint, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from app import db
from models import Restaurant, Booking, VoiceInteraction
from services.booking_service import extract_booking_info, create_booking
from services.voice_service import analyze_sentiment
from services.audit_service import log_action
from utils.calendly_helper import get_available_slots

twilio_call_bp = Blueprint('twilio_call', __name__)

# Global conversation state dictionary to track call states
# In production, this should be stored in a database or Redis
conversation_states = {}

@twilio_call_bp.route('/twilio/incoming-call', methods=['GET', 'POST'])
def incoming_call():
    """Handle incoming Twilio voice calls"""
    # Get the caller's phone number
    caller_number = request.values.get('From', '')
    call_sid = request.values.get('CallSid', '')
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Log the incoming call
    log_action(
        'incoming_call',
        'call',
        None,
        f"Incoming call from {caller_number}",
        json.dumps({'caller': caller_number, 'call_sid': call_sid})
    )
    
    # Initialize conversation state for this call
    conversation_states[call_sid] = {
        'stage': 'greeting',
        'caller_number': caller_number,
        'booking_data': {
            'customer_phone': caller_number,  # Pre-fill phone number
            'restaurant_id': 1  # Default restaurant
        }
    }
    
    # Welcome message
    response.say(
        "Welcome to our restaurant booking system. "
        "My name is Alex, and I'll help you make a reservation. "
        "What's your name?",
        voice='Polly.Matthew'
    )
    
    gather = Gather(
        input='speech',
        action='/twilio/collect-name',
        timeout=5,
        speech_timeout='auto'
    )
    
    response.append(gather)
    
    # If no input, retry
    response.redirect('/twilio/incoming-call')
    
    return Response(str(response), mimetype='text/xml')

@twilio_call_bp.route('/twilio/collect-name', methods=['GET', 'POST'])
def collect_name():
    """Collect the caller's name"""
    call_sid = request.values.get('CallSid', '')
    speech_result = request.values.get('SpeechResult', '')
    
    # Get the conversation state
    state = conversation_states.get(call_sid, {
        'stage': 'greeting',
        'booking_data': {}
    })
    
    response = VoiceResponse()
    
    # Create voice interaction record
    voice_interaction = VoiceInteraction(
        transcript=speech_result,
        response_text="Name collection"
    )
    db.session.add(voice_interaction)
    db.session.commit()
    
    # Try to extract the name from speech
    name_match = None
    if "my name is" in speech_result.lower():
        name_match = speech_result.lower().split("my name is")[1].strip()
    elif "this is" in speech_result.lower():
        name_match = speech_result.lower().split("this is")[1].strip()
    else:
        # Assume the entire speech is the name
        name_match = speech_result.strip()
    
    if name_match:
        # Store name in state
        state['booking_data']['customer_name'] = name_match
        state['stage'] = 'party_size'
        conversation_states[call_sid] = state
        
        # Respond and ask for party size
        response.say(
            f"Thanks, {name_match}. How many people will be in your party?",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-party-size',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    else:
        # If we couldn't understand, try again
        response.say(
            "I'm sorry, I didn't catch your name. Could you please tell me your name?",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-name',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    
    return Response(str(response), mimetype='text/xml')

@twilio_call_bp.route('/twilio/collect-party-size', methods=['GET', 'POST'])
def collect_party_size():
    """Collect the party size"""
    call_sid = request.values.get('CallSid', '')
    speech_result = request.values.get('SpeechResult', '')
    
    # Get the conversation state
    state = conversation_states.get(call_sid, {
        'stage': 'party_size',
        'booking_data': {}
    })
    
    response = VoiceResponse()
    
    # Create voice interaction record
    voice_interaction = VoiceInteraction(
        transcript=speech_result,
        response_text="Party size collection"
    )
    db.session.add(voice_interaction)
    db.session.commit()
    
    # Try to extract the party size from speech
    # Get words that might be numbers
    words = speech_result.lower().split()
    
    word_to_num = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }
    
    party_size = None
    for word in words:
        if word in word_to_num:
            party_size = word_to_num[word]
            break
        elif word.isdigit():
            party_size = int(word)
            break
    
    if party_size:
        # Store party size in state
        state['booking_data']['party_size'] = party_size
        state['stage'] = 'date'
        conversation_states[call_sid] = state
        
        # Respond and ask for date
        response.say(
            f"Great, a table for {party_size}. What date would you like to book? "
            "For example, you can say 'today', 'tomorrow', or a specific date.",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-date',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    else:
        # If we couldn't understand, try again
        response.say(
            "I'm sorry, I didn't catch how many people will be in your party. "
            "Could you please tell me the number of people?",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-party-size',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    
    return Response(str(response), mimetype='text/xml')

@twilio_call_bp.route('/twilio/collect-date', methods=['GET', 'POST'])
def collect_date():
    """Collect the booking date"""
    call_sid = request.values.get('CallSid', '')
    speech_result = request.values.get('SpeechResult', '')
    
    # Get the conversation state
    state = conversation_states.get(call_sid, {
        'stage': 'date',
        'booking_data': {}
    })
    
    response = VoiceResponse()
    
    # Create voice interaction record
    voice_interaction = VoiceInteraction(
        transcript=speech_result,
        response_text="Date collection"
    )
    db.session.add(voice_interaction)
    db.session.commit()
    
    # Try to extract the date from speech
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    booking_date = None
    
    speech_lower = speech_result.lower()
    
    if "today" in speech_lower:
        booking_date = today
    elif "tomorrow" in speech_lower:
        booking_date = tomorrow
    elif any(day in speech_lower for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
        # Handle days of the week
        weekday_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        for day, weekday_num in weekday_map.items():
            if day in speech_lower:
                # Find the next occurrence of this weekday
                days_ahead = weekday_num - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                booking_date = today + timedelta(days=days_ahead)
                break
    
    if booking_date:
        # Store date in state
        state['booking_data']['booking_date'] = booking_date
        state['stage'] = 'time'
        conversation_states[call_sid] = state
        
        # Format date for speech
        formatted_date = booking_date.strftime("%A, %B %d")
        
        # Respond and ask for time
        response.say(
            f"I've set your reservation date for {formatted_date}. "
            "What time would you like to book?",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-time',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    else:
        # If we couldn't understand, try again
        response.say(
            "I'm sorry, I didn't catch the date you'd like to book. "
            "Could you please tell me the date, like 'today', 'tomorrow', or a specific date?",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-date',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    
    return Response(str(response), mimetype='text/xml')

@twilio_call_bp.route('/twilio/collect-time', methods=['GET', 'POST'])
def collect_time():
    """Collect the booking time"""
    call_sid = request.values.get('CallSid', '')
    speech_result = request.values.get('SpeechResult', '')
    
    # Get the conversation state
    state = conversation_states.get(call_sid, {
        'stage': 'time',
        'booking_data': {}
    })
    
    response = VoiceResponse()
    
    # Create voice interaction record
    voice_interaction = VoiceInteraction(
        transcript=speech_result,
        response_text="Time collection"
    )
    db.session.add(voice_interaction)
    db.session.commit()
    
    # Try to extract the time from speech
    import re
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?', speech_result.lower())
    
    if time_match:
        hour = int(time_match.group(1))
        minute = time_match.group(2)
        minute = int(minute) if minute else 0
        ampm = time_match.group(3)
        
        # Handle AM/PM
        if ampm and ('p' in ampm) and hour < 12:
            hour += 12
        elif ampm and ('a' in ampm) and hour == 12:
            hour = 0
            
        # Format as HH:MM
        booking_time = f"{hour:02d}:{minute:02d}"
        
        # Check if restaurant is open at this time
        restaurant = Restaurant.query.get(state['booking_data']['restaurant_id'])
        
        # Default opening/closing if no restaurant found
        opening_time = restaurant.opening_time if restaurant else "11:00"
        closing_time = restaurant.closing_time if restaurant else "22:00"
        
        # Check if time is within business hours
        if booking_time < opening_time or booking_time > closing_time:
            response.say(
                f"I'm sorry, our restaurant is only open from {opening_time} to {closing_time}. "
                "Please choose a time within our business hours.",
                voice='Polly.Matthew'
            )
            
            gather = Gather(
                input='speech',
                action='/twilio/collect-time',
                timeout=5,
                speech_timeout='auto'
            )
            response.append(gather)
            return Response(str(response), mimetype='text/xml')
        
        # Check availability for this time slot
        booking_date = state['booking_data']['booking_date']
        party_size = state['booking_data']['party_size']
        
        # Check if slot is available (will implement actual check later)
        date_str = booking_date.strftime('%Y-%m-%d')
        available_slots = get_available_slots(date_str)
        
        # Check if our time is in available slots
        is_available = any(slot['time'] == booking_time for slot in available_slots)
        
        if is_available:
            # Store time in state
            state['booking_data']['booking_time'] = booking_time
            state['stage'] = 'confirmation'
            conversation_states[call_sid] = state
            
            # Get data for confirmation
            customer_name = state['booking_data'].get('customer_name', 'you')
            formatted_date = booking_date.strftime("%A, %B %d")
            
            # Respond and ask for confirmation
            response.say(
                f"Great, I have a table for {party_size} on {formatted_date} at {booking_time}. "
                f"Is this correct, {customer_name}? Please say yes or no.",
                voice='Polly.Matthew'
            )
            
            gather = Gather(
                input='speech',
                action='/twilio/confirm-booking',
                timeout=5,
                speech_timeout='auto'
            )
            response.append(gather)
        else:
            # Suggest alternative times
            response.say(
                "I'm sorry, that time is not available. Here are some alternative times: ",
                voice='Polly.Matthew'
            )
            
            for i, slot in enumerate(available_slots[:3]):
                response.say(f"Option {i+1}: {slot['time']}", voice='Polly.Matthew')
            
            response.say(
                "Please say the time you would prefer, or say 'none' to try another date.",
                voice='Polly.Matthew'
            )
            
            gather = Gather(
                input='speech',
                action='/twilio/collect-alternative-time',
                timeout=5,
                speech_timeout='auto'
            )
            response.append(gather)
    else:
        # If we couldn't understand, try again
        response.say(
            "I'm sorry, I didn't catch the time you'd like to book. "
            "Could you please tell me the time, like '7 PM' or '6:30'?",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-time',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    
    return Response(str(response), mimetype='text/xml')

@twilio_call_bp.route('/twilio/collect-alternative-time', methods=['GET', 'POST'])
def collect_alternative_time():
    """Handle selection of alternative time slots"""
    call_sid = request.values.get('CallSid', '')
    speech_result = request.values.get('SpeechResult', '')
    
    # Get the conversation state
    state = conversation_states.get(call_sid, {
        'stage': 'time',
        'booking_data': {}
    })
    
    response = VoiceResponse()
    speech_lower = speech_result.lower()
    
    if "none" in speech_lower or "different date" in speech_lower:
        # User wants to try a different date
        response.say(
            "Let's try a different date. What date would you like to book?",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-date',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    else:
        # Try to extract a time from the response
        import re
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?', speech_lower)
        
        if time_match:
            hour = int(time_match.group(1))
            minute = time_match.group(2)
            minute = int(minute) if minute else 0
            ampm = time_match.group(3)
            
            # Handle AM/PM
            if ampm and ('p' in ampm) and hour < 12:
                hour += 12
            elif ampm and ('a' in ampm) and hour == 12:
                hour = 0
                
            # Format as HH:MM
            booking_time = f"{hour:02d}:{minute:02d}"
            
            # Store time in state
            state['booking_data']['booking_time'] = booking_time
            state['stage'] = 'confirmation'
            conversation_states[call_sid] = state
            
            # Get data for confirmation
            customer_name = state['booking_data'].get('customer_name', 'you')
            booking_date = state['booking_data']['booking_date']
            party_size = state['booking_data']['party_size']
            formatted_date = booking_date.strftime("%A, %B %d")
            
            # Respond and ask for confirmation
            response.say(
                f"Great, I have a table for {party_size} on {formatted_date} at {booking_time}. "
                f"Is this correct, {customer_name}? Please say yes or no.",
                voice='Polly.Matthew'
            )
            
            gather = Gather(
                input='speech',
                action='/twilio/confirm-booking',
                timeout=5,
                speech_timeout='auto'
            )
            response.append(gather)
        else:
            # If we couldn't understand, try again with the original time options
            booking_date = state['booking_data']['booking_date']
            date_str = booking_date.strftime('%Y-%m-%d')
            available_slots = get_available_slots(date_str)
            
            response.say(
                "I'm sorry, I didn't understand your choice. Here are the available times again: ",
                voice='Polly.Matthew'
            )
            
            for i, slot in enumerate(available_slots[:3]):
                response.say(f"Option {i+1}: {slot['time']}", voice='Polly.Matthew')
            
            response.say(
                "Please say the time you would prefer, or say 'none' to try another date.",
                voice='Polly.Matthew'
            )
            
            gather = Gather(
                input='speech',
                action='/twilio/collect-alternative-time',
                timeout=5,
                speech_timeout='auto'
            )
            response.append(gather)
    
    return Response(str(response), mimetype='text/xml')

@twilio_call_bp.route('/twilio/confirm-booking', methods=['GET', 'POST'])
def confirm_booking():
    """Handle booking confirmation"""
    call_sid = request.values.get('CallSid', '')
    speech_result = request.values.get('SpeechResult', '')
    
    # Get the conversation state
    state = conversation_states.get(call_sid, {
        'stage': 'confirmation',
        'booking_data': {}
    })
    
    response = VoiceResponse()
    
    # Create voice interaction record
    voice_interaction = VoiceInteraction(
        transcript=speech_result,
        response_text="Booking confirmation"
    )
    db.session.add(voice_interaction)
    db.session.commit()
    
    # Analyze speech for confirmation
    speech_lower = speech_result.lower()
    
    if any(word in speech_lower for word in ['yes', 'correct', 'right', 'sure', 'confirm']):
        # User confirmed the booking
        
        # Convert date to string format for create_booking
        booking_date = state['booking_data']['booking_date']
        state['booking_data']['booking_date'] = booking_date.strftime('%Y-%m-%d')
        
        # Create the booking
        booking, success, message = create_booking(state['booking_data'])
        
        if success:
            # Booking created successfully
            response.say(
                f"Excellent! Your reservation has been confirmed. "
                f"You'll receive a confirmation SMS with your booking details. "
                f"Thank you for choosing our restaurant. Goodbye!",
                voice='Polly.Matthew'
            )
            
            # Cleanup state
            if call_sid in conversation_states:
                del conversation_states[call_sid]
                
        else:
            # Failed to create booking
            response.say(
                f"I'm sorry, there was an issue creating your booking: {message} "
                f"Please try again later or call our restaurant directly. Thank you and goodbye!",
                voice='Polly.Matthew'
            )
            
            # Cleanup state
            if call_sid in conversation_states:
                del conversation_states[call_sid]
    else:
        # User did not confirm, go back to date selection
        state['stage'] = 'date'
        conversation_states[call_sid] = state
        
        response.say(
            "Let's try again. What date would you like to book?",
            voice='Polly.Matthew'
        )
        
        gather = Gather(
            input='speech',
            action='/twilio/collect-date',
            timeout=5,
            speech_timeout='auto'
        )
        response.append(gather)
    
    return Response(str(response), mimetype='text/xml')

@twilio_call_bp.route('/twilio/fallback', methods=['GET', 'POST'])
def fallback():
    """Handle fallback for when things go wrong"""
    response = VoiceResponse()
    
    response.say(
        "I'm sorry, there seems to be an issue with our booking system. "
        "Please try again later or call our restaurant directly during business hours. "
        "Thank you for your patience.",
        voice='Polly.Matthew'
    )
    
    return Response(str(response), mimetype='text/xml')