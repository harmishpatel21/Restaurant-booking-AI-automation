import os
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app, render_template, redirect, url_for
from utils.calendly_helper import get_available_slots, create_calendly_event
from models import db, Booking, Restaurant

calendly_bp = Blueprint('calendly', __name__)

@calendly_bp.route('/api/calendly/test-connection', methods=['GET'])
def test_calendly_connection():
    """
    Test Calendly API connection and return status
    """
    try:
        api_key = current_app.config.get('CALENDLY_API_KEY') or os.environ.get('CALENDLY_API_KEY')
        
        if not api_key:
            return jsonify({
                'success': False,
                'message': 'Calendly API key not found. Please set the CALENDLY_API_KEY environment variable.'
            })
        
        # Test by getting available slots for tomorrow
        tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        slots = get_available_slots(tomorrow)
        
        if slots:
            return jsonify({
                'success': True,
                'message': 'Successfully connected to Calendly API',
                'slots_count': len(slots),
                'sample_slots': slots[:3] if len(slots) > 3 else slots
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Connected to Calendly API but no available slots were found'
            })
    
    except Exception as e:
        current_app.logger.error(f"Error testing Calendly connection: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@calendly_bp.route('/api/calendly/available-slots', methods=['GET'])
def get_available_slots_api():
    """
    Get available slots for a specific date
    """
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({
            'success': False,
            'message': 'Date parameter is required'
        }), 400
    
    try:
        # Validate date format
        datetime.strptime(date_str, '%Y-%m-%d')
        
        # Get available slots
        slots = get_available_slots(date_str)
        
        return jsonify({
            'success': True,
            'date': date_str,
            'slots': slots
        })
    
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid date format. Use YYYY-MM-DD'
        }), 400
    
    except Exception as e:
        current_app.logger.error(f"Error getting available slots: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500