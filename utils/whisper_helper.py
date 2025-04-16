import os
import openai
from flask import current_app

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using OpenAI's Whisper model
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    try:
        api_key = current_app.config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            current_app.logger.error("OpenAI API key not found")
            return None
            
        # Set OpenAI API key
        openai.api_key = api_key
        
        # Open the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Transcribe using Whisper API
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
            
            if response and hasattr(response, 'text'):
                return response.text
            else:
                current_app.logger.error("Failed to transcribe audio with Whisper")
                return None
                
    except Exception as e:
        current_app.logger.error(f"Error in transcribe_audio: {str(e)}")
        return None
