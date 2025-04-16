import os
import requests
from flask import current_app

def text_to_speech(text, voice_id="EXAVITQu4vr4xnSDxMaL"):
    """
    Convert text to speech using ElevenLabs API
    
    Args:
        text (str): Text to convert to speech
        voice_id (str, optional): ID of the voice to use
        
    Returns:
        bytes: Audio data as bytes
    """
    try:
        api_key = current_app.config.get('ELEVENLABS_API_KEY') or os.environ.get('ELEVENLABS_API_KEY')
        
        if not api_key:
            current_app.logger.error("ElevenLabs API key not found")
            return None
            
        # Limit text length for demo/free tier
        if len(text) > 2000:
            text = text[:1997] + "..."
            
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        # Request headers
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        # Request data
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        # Make request to ElevenLabs API
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            current_app.logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"Error in text_to_speech: {str(e)}")
        return None

def get_available_voices():
    """
    Get list of available voices from ElevenLabs
    
    Returns:
        list: List of voice dictionaries with id, name, etc.
    """
    try:
        api_key = current_app.config.get('ELEVENLABS_API_KEY') or os.environ.get('ELEVENLABS_API_KEY')
        
        if not api_key:
            current_app.logger.error("ElevenLabs API key not found")
            return []
            
        # ElevenLabs API endpoint
        url = "https://api.elevenlabs.io/v1/voices"
        
        # Request headers
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        # Make request to ElevenLabs API
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json().get("voices", [])
            return voices
        else:
            current_app.logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        current_app.logger.error(f"Error in get_available_voices: {str(e)}")
        return []
