"""
Unit Tests for Database Module
Tests database operations, logging, and data integrity
"""
import pytest
import sqlite3
import os
from database import (
    get_db_connection, log_action, authenticate_user, add_patient,
    get_all_patients, get_patient_by_id, update_patient, delete_patient,
    get_patient_count, get_all_logs
)
from auth import hash_password


@pytest.fixture
def test_db():
    """Create a test database"""
    # Use test database
    test_db_path = 'test_hospital.db'
    
    # Remove if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create test database
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Seed test user
    cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, ('testuser', hash_password('testpass'), 'admin'))
    
    conn.commit()
    conn.close()
    
    yield test_db_path
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


class TestDatabaseConnection:
    """Test database connection"""
    
    def test_get_db_connection_returns_connection(self):
        """Test that get_db_connection returns a connection object"""
        conn = get_db_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()


class TestAuthentication:
    """Test user authentication"""
    
    def test_authenticate_user_valid_credentials(self, test_db, monkeypatch):
        """Test authentication with valid credentials"""
        # Patch database connection to use test database
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        result = authenticate_user('testuser', hash_password('testpass'))
        
        assert result is not None
        assert result[1] == 'testuser'
        assert result[2] == 'admin'
    
    def test_authenticate_user_invalid_credentials(self, test_db, monkeypatch):
        """Test authentication with invalid credentials"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        result = authenticate_user('testuser', hash_password('wrongpass'))
        
        assert result is None
    
    def test_authenticate_user_nonexistent_user(self, test_db, monkeypatch):
        """Test authentication with nonexistent user"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        result = authenticate_user('nonexistent', hash_password('pass'))
        
        assert result is None


class TestPatientOperations:
    """Test patient CRUD operations"""
    
    def test_add_patient_success(self, test_db, monkeypatch):
        """Test adding a patient successfully"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        result = add_patient(
            'encrypted_name',
            'encrypted_contact',
            'encrypted_diagnosis',
            1,
            'admin'
        )
        
        assert result is True
    
    def test_get_all_patients(self, test_db, monkeypatch):
        """Test retrieving all patients"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        # Add a patient first
        add_patient('enc_name', 'enc_contact', 'enc_diagnosis', 1, 'admin')
        
        patients = get_all_patients()
        
        assert len(patients) > 0
        assert 'patient_id' in patients[0]
        assert 'name' in patients[0]
    
    def test_get_patient_by_id(self, test_db, monkeypatch):
        """Test retrieving patient by ID"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        # Add a patient
        add_patient('enc_name', 'enc_contact', 'enc_diagnosis', 1, 'admin')
        
        # Get the patient
        patient = get_patient_by_id(1)
        
        assert patient is not None
        assert patient['patient_id'] == 1
    
    def test_update_patient_success(self, test_db, monkeypatch):
        """Test updating patient successfully"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        # Add a patient
        add_patient('enc_name', 'enc_contact', 'enc_diagnosis', 1, 'admin')
        
        # Update the patient
        result = update_patient(1, 'new_name', 'new_contact', 'new_diagnosis', 1, 'admin')
        
        assert result is True
    
    def test_delete_patient_success(self, test_db, monkeypatch):
        """Test deleting patient successfully"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        # Add a patient
        add_patient('enc_name', 'enc_contact', 'enc_diagnosis', 1, 'admin')
        
        # Delete the patient
        result = delete_patient(1, 1, 'admin')
        
        assert result is True
    
    def test_get_patient_count(self, test_db, monkeypatch):
        """Test getting patient count"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        # Add patients
        add_patient('enc_name1', 'enc_contact1', 'enc_diagnosis1', 1, 'admin')
        add_patient('enc_name2', 'enc_contact2', 'enc_diagnosis2', 1, 'admin')
        
        count = get_patient_count()
        
        assert count == 2


class TestLogging:
    """Test logging functionality"""
    
    def test_log_action_success(self, test_db, monkeypatch):
        """Test that actions are logged successfully"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        # Log an action
        log_action(1, 'admin', 'TEST_ACTION', 'Test details')
        
        # Verify log was created
        logs = get_all_logs(10)
        
        assert len(logs) > 0
        assert logs[0]['action'] == 'TEST_ACTION'
    
    def test_get_all_logs(self, test_db, monkeypatch):
        """Test retrieving all logs"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        # Create some logs
        log_action(1, 'admin', 'ACTION1', 'Details 1')
        log_action(1, 'admin', 'ACTION2', 'Details 2')
        
        logs = get_all_logs(10)
        
        assert len(logs) >= 2


class TestSQLInjectionPrevention:
    """Test SQL injection prevention"""
    
    def test_authenticate_with_sql_injection_attempt(self, test_db, monkeypatch):
        """Test that SQL injection is prevented in authentication"""
        def mock_connection():
            conn = sqlite3.connect(test_db)
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr('database.get_db_connection', mock_connection)
        
        # Attempt SQL injection
        result = authenticate_user("admin' OR '1'='1", "password")
        
        # Should return None, not bypass authentication
        assert result is None
