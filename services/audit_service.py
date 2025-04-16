import json
from datetime import datetime
from flask import current_app
from app import db
from models import AuditLog

def log_action(action, entity_type, entity_id, description, data=None):
    """
    Log an action in the audit log
    
    Args:
        action (str): Type of action (create_booking, update_booking, etc.)
        entity_type (str): Type of entity (booking, restaurant, etc.)
        entity_id (int): ID of the entity
        description (str): Description of the action
        data (str, optional): Additional JSON data as string
        
    Returns:
        AuditLog: The created audit log entry
    """
    try:
        # Create audit log entry
        audit_log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            data=data,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        current_app.logger.info(f"Audit log created: {action} - {description}")
        return audit_log
        
    except Exception as e:
        current_app.logger.error(f"Failed to create audit log: {str(e)}")
        
        # Try to rollback the session
        try:
            db.session.rollback()
        except:
            pass
            
        return None

def get_audit_logs(entity_type=None, entity_id=None, action=None, start_date=None, end_date=None, limit=100):
    """
    Get audit logs with optional filtering
    
    Args:
        entity_type (str, optional): Filter by entity type
        entity_id (int, optional): Filter by entity ID
        action (str, optional): Filter by action type
        start_date (datetime, optional): Start date for filtering
        end_date (datetime, optional): End date for filtering
        limit (int, optional): Maximum number of logs to return
        
    Returns:
        list: List of AuditLog objects
    """
    try:
        query = AuditLog.query
        
        # Apply filters
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
            
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
            
        if action:
            query = query.filter(AuditLog.action == action)
            
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
            
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
            
        # Order by timestamp (newest first) and limit results
        query = query.order_by(AuditLog.timestamp.desc()).limit(limit)
        
        return query.all()
        
    except Exception as e:
        current_app.logger.error(f"Error getting audit logs: {str(e)}")
        return []

def export_audit_logs_to_json(logs):
    """
    Export audit logs to JSON format
    
    Args:
        logs (list): List of AuditLog objects
        
    Returns:
        str: JSON string of audit logs
    """
    try:
        log_data = []
        
        for log in logs:
            log_data.append({
                'id': log.id,
                'action': log.action,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'description': log.description,
                'data': log.data,
                'timestamp': log.timestamp.isoformat()
            })
            
        return json.dumps(log_data, indent=2)
        
    except Exception as e:
        current_app.logger.error(f"Error exporting audit logs: {str(e)}")
        return json.dumps({'error': str(e)})
