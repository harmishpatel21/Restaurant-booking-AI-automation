import os
import base64
import tempfile
import time
from flask import current_app
from utils.whisper_helper import transcribe_audio
from utils.elevenlabs_helper import text_to_speech

def process_audio(audio_file_path):
    """
    Process the audio file using Whisper for speech-to-text conversion
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text from the audio
    """
    try:
        current_app.logger.info(f"Processing audio file: {audio_file_path}")
        
        # Transcribe audio using Whisper
        transcript = transcribe_audio(audio_file_path)
        
        if not transcript:
            current_app.logger.error("Failed to transcribe audio file")
            return None
            
        current_app.logger.info(f"Audio transcription successful: {transcript[:100]}...")
        return transcript
        
    except Exception as e:
        current_app.logger.error(f"Error in process_audio: {str(e)}")
        return None

def generate_voice_response(text):
    """
    Generate voice response using ElevenLabs TTS
    
    Args:
        text (str): Text to convert to speech
        
    Returns:
        str: URL to the generated audio file
    """
    try:
        current_app.logger.info(f"Generating voice response for: {text[:100]}...")
        
        # Generate unique filename
        timestamp = int(time.time())
        filename = f"response_{timestamp}.mp3"
        
        # Get path to save audio
        static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        audio_folder = os.path.join(static_folder, 'audio')
        
        # Create audio directory if it doesn't exist
        os.makedirs(audio_folder, exist_ok=True)
        
        file_path = os.path.join(audio_folder, filename)
        
        # Convert text to speech using ElevenLabs
        audio_data = text_to_speech(text)
        
        if not audio_data:
            current_app.logger.error("Failed to generate voice response")
            return None
            
        # Save audio data to file
        with open(file_path, 'wb') as f:
            f.write(audio_data)
            
        # Return URL to the audio file
        return f"/static/audio/{filename}"
        
    except Exception as e:
        current_app.logger.error(f"Error in generate_voice_response: {str(e)}")
        return None

def analyze_sentiment(text):
    """
    Analyze sentiment of user's speech
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Sentiment analysis results
    """
    # This would normally use a more sophisticated sentiment analysis
    # For this demo, we'll use a simple keyword-based approach
    positive_keywords = ['yes', 'good', 'great', 'excellent', 'perfect', 'happy', 'thank']
    negative_keywords = ['no', 'not', 'bad', 'wrong', 'unhappy', 'cancel', 'problem']
    
    positive_count = sum(1 for word in positive_keywords if word in text.lower())
    negative_count = sum(1 for word in negative_keywords if word in text.lower())
    
    if positive_count > negative_count:
        sentiment = 'positive'
    elif negative_count > positive_count:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return {
        'sentiment': sentiment,
        'positive_score': positive_count,
        'negative_score': negative_count
    }
