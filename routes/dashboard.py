import csv
import io
from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from sqlalchemy import func
from app import db
from models import Booking, AuditLog, Restaurant, VoiceInteraction

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Render the main dashboard with booking stats and list"""
    # Get filter parameters
    filter_status = request.args.get('status', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Build query with filters
    query = Booking.query
    
    if filter_status:
        query = query.filter(Booking.status == filter_status)
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Booking.booking_date.between(start_date, end_date))
        except ValueError:
            flash('Invalid date format', 'danger')
    
    # Get bookings sorted by date (newest first)
    bookings = query.order_by(Booking.booking_date.desc()).all()
    
    # Calculate statistics
    stats = calculate_booking_stats()
    
    return render_template(
        'dashboard.html', 
        bookings=bookings, 
        stats=stats,
        filter_status=filter_status
    )

@dashboard_bp.route('/dashboard/booking-stats', methods=['GET'])
def booking_stats():
    """API endpoint for booking statistics chart data"""
    # Get booking counts for the last 14 days
    end_date = date.today()
    start_date = end_date - timedelta(days=13)
    
    # Query booking counts by date
    bookings_by_date = db.session.query(
        Booking.booking_date,
        func.count(Booking.id).label('count')
    ).filter(
        Booking.booking_date.between(start_date, end_date)
    ).group_by(
        Booking.booking_date
    ).all()
    
    # Create a dict for easy lookup
    booking_counts = {day[0].strftime('%Y-%m-%d'): day[1] for day in bookings_by_date}
    
    # Generate labels and data for all days in range
    current_date = start_date
    labels = []
    values = []
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        labels.append(date_str)
        values.append(booking_counts.get(date_str, 0))
        current_date += timedelta(days=1)
    
    return jsonify({
        'labels': labels,
        'values': values
    })

@dashboard_bp.route('/dashboard/export-csv', methods=['GET'])
def export_csv():
    """Export bookings as CSV file"""
    # Get filter parameters (same as dashboard)
    filter_status = request.args.get('status', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Build query with filters
    query = Booking.query
    
    if filter_status:
        query = query.filter(Booking.status == filter_status)
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Booking.booking_date.between(start_date, end_date))
        except ValueError:
            flash('Invalid date format', 'danger')
    
    # Get bookings
    bookings = query.order_by(Booking.booking_date.desc()).all()
    
    # Create CSV in memory
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write header
    csv_writer.writerow([
        'ID', 'Customer Name', 'Phone', 'Email', 'Party Size', 
        'Date', 'Time', 'Status', 'Special Requests', 'Created At'
    ])
    
    # Write data rows
    for booking in bookings:
        csv_writer.writerow([
            booking.id,
            booking.customer_name,
            booking.customer_phone,
            booking.customer_email,
            booking.party_size,
            booking.booking_date.strftime('%Y-%m-%d'),
            booking.booking_time,
            booking.status,
            booking.special_requests,
            booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Prepare response
    csv_data.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        io.BytesIO(csv_data.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'restaurant_bookings_{timestamp}.csv'
    )

@dashboard_bp.route('/dashboard/audit-logs', methods=['GET'])
def audit_logs():
    """View audit logs with filtering"""
    # Get filter parameters
    filter_action = request.args.get('action', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Build query with filters
    query = AuditLog.query
    
    if filter_action:
        query = query.filter(AuditLog.action == filter_action)
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Add 1 day to end_date to include the entire end date
            end_date_inclusive = end_date + timedelta(days=1)
            query = query.filter(AuditLog.timestamp.between(
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date_inclusive, datetime.min.time())
            ))
        except ValueError:
            flash('Invalid date format', 'danger')
    
    # Get audit logs sorted by timestamp (newest first)
    audit_logs = query.order_by(AuditLog.timestamp.desc()).all()
    
    return render_template(
        'audit_logs.html', 
        audit_logs=audit_logs,
        filter_action=filter_action
    )

@dashboard_bp.route('/dashboard/export-audit-logs', methods=['GET'])
def export_audit_logs():
    """Export audit logs as CSV file"""
    # Get filter parameters (same as audit_logs)
    filter_action = request.args.get('action', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Build query with filters
    query = AuditLog.query
    
    if filter_action:
        query = query.filter(AuditLog.action == filter_action)
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Add 1 day to end_date to include the entire end date
            end_date_inclusive = end_date + timedelta(days=1)
            query = query.filter(AuditLog.timestamp.between(
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date_inclusive, datetime.min.time())
            ))
        except ValueError:
            flash('Invalid date format', 'danger')
    
    # Get audit logs
    audit_logs = query.order_by(AuditLog.timestamp.desc()).all()
    
    # Create CSV in memory
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write header
    csv_writer.writerow([
        'ID', 'Timestamp', 'Action', 'Entity Type', 'Entity ID', 
        'Description', 'Data'
    ])
    
    # Write data rows
    for log in audit_logs:
        csv_writer.writerow([
            log.id,
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.action,
            log.entity_type,
            log.entity_id,
            log.description,
            log.data
        ])
    
    # Prepare response
    csv_data.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        io.BytesIO(csv_data.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'audit_logs_{timestamp}.csv'
    )

def calculate_booking_stats():
    """Calculate booking statistics for the dashboard"""
    today = date.today()
    
    # Total bookings
    total_bookings = Booking.query.count()
    
    # Bookings by status
    confirmed = Booking.query.filter_by(status='confirmed').count()
    canceled = Booking.query.filter_by(status='canceled').count()
    completed = Booking.query.filter_by(status='completed').count()
    
    # Today's bookings
    today_bookings = Booking.query.filter_by(booking_date=today).count()
    
    return {
        'total_bookings': total_bookings,
        'confirmed': confirmed,
        'canceled': canceled,
        'completed': completed,
        'today': today_bookings
    }
