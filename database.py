"""
Database Module
Handles all database operations, logging, and data persistence
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import streamlit as st


def get_db_connection():
    """
    Get SQLite database connection with proper configuration
    
    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect('hospital.db', timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


@st.cache_resource
def get_cached_connection():
    """
    Get cached database connection for better performance
    Used with Streamlit's caching mechanism
    """
    return get_db_connection()


# ==================== LOGGING FUNCTIONS ====================

def log_action(user_id: int, role: str, action: str, details: str = ""):
    """
    Log user action to audit trail
    
    Args:
        user_id: User's database ID
        role: User's role
        action: Action type (login, view, add, update, delete, export, etc.)
        details: Additional details about the action (no sensitive data)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO logs (user_id, role, action, details)
            VALUES (?, ?, ?, ?)
        """, (user_id, role, action, details))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging action: {e}")


# ==================== USER FUNCTIONS ====================

def authenticate_user(username: str, password_hash: str) -> Optional[Tuple[int, str, str]]:
    """
    Authenticate user with username and hashed password
    
    Args:
        username: Username
        password_hash: SHA-256 hashed password
        
    Returns:
        Tuple of (user_id, username, role) if successful, None otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, role
            FROM users
            WHERE username = ? AND password = ?
        """, (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return (result['user_id'], result['username'], result['role'])
        return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None


def get_all_users() -> List[Dict]:
    """
    Get all users (admin only)
    
    Returns:
        List of user dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, username, role FROM users ORDER BY user_id")
        users = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


# ==================== PATIENT FUNCTIONS ====================

def add_patient(name_encrypted: str, contact_encrypted: str, diagnosis_encrypted: str, 
                user_id: int, role: str) -> bool:
    """
    Add new patient record with encrypted data
    
    Args:
        name_encrypted: Encrypted patient name
        contact_encrypted: Encrypted contact number
        diagnosis_encrypted: Encrypted diagnosis
        user_id: ID of user adding the record
        role: Role of user adding the record
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO patients (name, contact, diagnosis)
            VALUES (?, ?, ?)
        """, (name_encrypted, contact_encrypted, diagnosis_encrypted))
        
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log the action
        log_action(user_id, role, "ADD_PATIENT", f"Added patient ID: {patient_id}")
        
        return True
    except Exception as e:
        print(f"Error adding patient: {e}")
        return False


def get_all_patients() -> List[Dict]:
    """
    Get all patient records (encrypted)
    
    Returns:
        List of patient dictionaries with encrypted data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT patient_id, name, contact, diagnosis, date_added
            FROM patients
            ORDER BY patient_id DESC
        """)
        
        patients = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return patients
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return []


def get_patient_by_id(patient_id: int) -> Optional[Dict]:
    """
    Get patient record by ID
    
    Args:
        patient_id: Patient's database ID
        
    Returns:
        Patient dictionary or None if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT patient_id, name, contact, diagnosis, date_added
            FROM patients
            WHERE patient_id = ?
        """, (patient_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    except Exception as e:
        print(f"Error fetching patient: {e}")
        return None


def update_patient(patient_id: int, name_encrypted: str, contact_encrypted: str, 
                   diagnosis_encrypted: str, user_id: int, role: str) -> bool:
    """
    Update patient record
    
    Args:
        patient_id: Patient's database ID
        name_encrypted: Encrypted patient name
        contact_encrypted: Encrypted contact number
        diagnosis_encrypted: Encrypted diagnosis
        user_id: ID of user updating the record
        role: Role of user updating the record
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE patients
            SET name = ?, contact = ?, diagnosis = ?
            WHERE patient_id = ?
        """, (name_encrypted, contact_encrypted, diagnosis_encrypted, patient_id))
        
        conn.commit()
        conn.close()
        
        # Log the action
        log_action(user_id, role, "UPDATE_PATIENT", f"Updated patient ID: {patient_id}")
        
        return True
    except Exception as e:
        print(f"Error updating patient: {e}")
        return False


def delete_patient(patient_id: int, user_id: int, role: str) -> bool:
    """
    Delete patient record (admin only)
    
    Args:
        patient_id: Patient's database ID
        user_id: ID of user deleting the record
        role: Role of user deleting the record
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
        
        conn.commit()
        conn.close()
        
        # Log the action
        log_action(user_id, role, "DELETE_PATIENT", f"Deleted patient ID: {patient_id}")
        
        return True
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return False


def get_patient_count() -> int:
    """Get total number of patients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM patients")
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0
    except Exception as e:
        print(f"Error counting patients: {e}")
        return 0


# ==================== LOG FUNCTIONS ====================

def get_all_logs(limit: int = 100) -> List[Dict]:
    """
    Get audit logs (admin only)
    
    Args:
        limit: Maximum number of logs to retrieve
        
    Returns:
        List of log dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.log_id, l.user_id, u.username, l.role, l.action, l.timestamp, l.details
            FROM logs l
            LEFT JOIN users u ON l.user_id = u.user_id
            ORDER BY l.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []


def get_logs_by_user(user_id: int, limit: int = 50) -> List[Dict]:
    """
    Get logs for specific user
    
    Args:
        user_id: User's database ID
        limit: Maximum number of logs to retrieve
        
    Returns:
        List of log dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT log_id, user_id, role, action, timestamp, details
            FROM logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    except Exception as e:
        print(f"Error fetching user logs: {e}")
        return []


def get_logs_by_action(action: str, limit: int = 50) -> List[Dict]:
    """
    Get logs by action type
    
    Args:
        action: Action type to filter by
        limit: Maximum number of logs to retrieve
        
    Returns:
        List of log dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.log_id, l.user_id, u.username, l.role, l.action, l.timestamp, l.details
            FROM logs l
            LEFT JOIN users u ON l.user_id = u.user_id
            WHERE l.action = ?
            ORDER BY l.timestamp DESC
            LIMIT ?
        """, (action, limit))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    except Exception as e:
        print(f"Error fetching logs by action: {e}")
        return []


def get_activity_stats() -> Dict:
    """
    Get activity statistics for dashboard
    
    Returns:
        Dictionary with activity statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total logs
        cursor.execute("SELECT COUNT(*) as count FROM logs")
        total_logs = cursor.fetchone()['count']
        
        # Logs today
        cursor.execute("""
            SELECT COUNT(*) as count FROM logs
            WHERE DATE(timestamp) = DATE('now')
        """)
        logs_today = cursor.fetchone()['count']
        
        # Most active user
        cursor.execute("""
            SELECT u.username, COUNT(*) as count
            FROM logs l
            JOIN users u ON l.user_id = u.user_id
            GROUP BY l.user_id
            ORDER BY count DESC
            LIMIT 1
        """)
        most_active = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_logs': total_logs,
            'logs_today': logs_today,
            'most_active_user': most_active['username'] if most_active else 'N/A',
            'most_active_count': most_active['count'] if most_active else 0
        }
    except Exception as e:
        print(f"Error fetching activity stats: {e}")
        return {
            'total_logs': 0,
            'logs_today': 0,
            'most_active_user': 'N/A',
            'most_active_count': 0
        }


def get_daily_activity(days: int = 7) -> List[Dict]:
    """
    Get daily activity for the last N days
    
    Args:
        days: Number of days to retrieve
        
    Returns:
        List of dictionaries with date and count
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM logs
            WHERE DATE(timestamp) >= DATE('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (days,))
        
        activity = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return activity
    except Exception as e:
        print(f"Error fetching daily activity: {e}")
        return []
