import os
import json
import tempfile
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from models import VoiceInteraction
from services.voice_service import process_audio, generate_voice_response
from services.booking_service import extract_booking_info
from services.audit_service import log_action

voice_bp = Blueprint('voice', __name__)

@voice_bp.route('/voice/process', methods=['POST'])
def process_voice():
    """Process audio recording and extract booking information"""
    try:
        # Check if audio file is present in request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Save the audio file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, secure_filename(audio_file.filename))
        audio_file.save(temp_file_path)
        
        # Process the audio file to get the transcript
        transcript = process_audio(temp_file_path)
        
        if not transcript:
            return jsonify({'error': 'Failed to transcribe audio'}), 400
        
        # Extract booking information from transcript
        booking_data, response_text = extract_booking_info(transcript)
        
        # Generate voice response
        audio_response_url = generate_voice_response(response_text)
        
        # Create voice interaction record
        voice_interaction = VoiceInteraction(
            transcript=transcript,
            response_text=response_text
        )
        db.session.add(voice_interaction)
        db.session.commit()
        
        # Log the voice interaction in audit logs
        log_action(
            'voice_interaction',
            'voice_interaction',
            voice_interaction.id,
            'Voice interaction processed',
            json.dumps({
                'transcript': transcript,
                'response': response_text
            })
        )
        
        # Clean up temporary file
        os.remove(temp_file_path)
        os.rmdir(temp_dir)
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'response': response_text,
            'booking_data': booking_data,
            'audio_response_url': audio_response_url,
            'interaction_id': voice_interaction.id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing voice: {str(e)}")
        
        # Log the error
        log_action(
            'voice_error',
            'voice_interaction',
            None,
            f"Error processing voice: {str(e)}",
            None
        )
        
        return jsonify({'error': str(e)}), 500
