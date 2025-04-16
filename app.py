import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "restaurant-booking-secret")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///restaurant_booking.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Load API keys from environment variables
app.config["ELEVENLABS_API_KEY"] = os.environ.get("ELEVENLABS_API_KEY", "")
app.config["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
app.config["CALENDLY_API_KEY"] = os.environ.get("CALENDLY_API_KEY", "")
app.config["TWILIO_ACCOUNT_SID"] = os.environ.get("TWILIO_ACCOUNT_SID", "")
app.config["TWILIO_AUTH_TOKEN"] = os.environ.get("TWILIO_AUTH_TOKEN", "")
app.config["TWILIO_PHONE_NUMBER"] = os.environ.get("TWILIO_PHONE_NUMBER", "")

# Import routes
with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create all database tables
    db.create_all()
    
    # Register blueprints
    from routes.main import main_bp
    from routes.booking import booking_bp
    from routes.dashboard import dashboard_bp
    from routes.voice import voice_bp
    from routes.twilio_call import twilio_call_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(voice_bp)
    app.register_blueprint(twilio_call_bp)

logger.info("Application initialized successfully")
