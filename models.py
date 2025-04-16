from datetime import datetime
from app import db

class Restaurant(db.Model):
    """Restaurant model for managing restaurant information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    opening_time = db.Column(db.String(10), nullable=False)
    closing_time = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='restaurant', lazy=True)
    
    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Booking(db.Model):
    """Booking model for restaurant reservations"""
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100), nullable=True)
    party_size = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.String(10), nullable=False)
    special_requests = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='confirmed', nullable=False)  # confirmed, canceled, completed
    calendly_event_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Booking {self.id} - {self.customer_name}>"

class AuditLog(db.Model):
    """Audit log for tracking all system activities"""
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)  # create_booking, cancel_booking, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # booking, restaurant, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=True)  # JSON data as string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog {self.id} - {self.action}>"

class VoiceInteraction(db.Model):
    """Model for storing voice interaction data"""
    id = db.Column(db.Integer, primary_key=True)
    audio_file_path = db.Column(db.String(200), nullable=True)
    transcript = db.Column(db.Text, nullable=True)
    response_text = db.Column(db.Text, nullable=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with booking
    booking = db.relationship('Booking', backref='voice_interactions', lazy=True)
    
    def __repr__(self):
        return f"<VoiceInteraction {self.id}>"
