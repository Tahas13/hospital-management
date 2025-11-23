"""
Unit Tests for Authentication Module
Tests password hashing, verification, and session management
"""
import pytest
from auth import (
    hash_password, verify_password, login_user, logout_user,
    is_authenticated, get_current_user
)
import streamlit as st


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        result = hash_password("test123")
        assert isinstance(result, str)
    
    def test_hash_password_consistent(self):
        """Test that same password produces same hash"""
        password = "test123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 == hash2
    
    def test_hash_password_different_inputs(self):
        """Test that different passwords produce different hashes"""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        assert hash1 != hash2
    
    def test_hash_password_length(self):
        """Test that SHA-256 hash is 64 characters (hex)"""
        result = hash_password("test")
        assert len(result) == 64
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test123"
        hashed = hash_password(password)
        assert verify_password("wrong", hashed) is False


class TestSessionManagement:
    """Test session state management"""
    
    def test_login_user_sets_session_state(self, mocker):
        """Test that login_user sets session state correctly"""
        # Mock streamlit session_state
        mock_session = {}
        mocker.patch.object(st, 'session_state', mock_session)
        
        login_user(1, "testuser", "admin")
        
        assert st.session_state['authenticated'] is True
        assert st.session_state['user_id'] == 1
        assert st.session_state['username'] == "testuser"
        assert st.session_state['role'] == "admin"
    
    def test_logout_user_clears_session(self, mocker):
        """Test that logout_user clears session state"""
        # Mock streamlit session_state
        mock_session = {
            'authenticated': True,
            'user_id': 1,
            'username': 'test',
            'role': 'admin'
        }
        mocker.patch.object(st, 'session_state', mock_session)
        
        logout_user()
        
        assert len(st.session_state) == 0
    
    def test_is_authenticated_true(self, mocker):
        """Test is_authenticated returns True when authenticated"""
        mock_session = {'authenticated': True}
        mocker.patch.object(st, 'session_state', mock_session)
        
        assert is_authenticated() is True
    
    def test_is_authenticated_false(self, mocker):
        """Test is_authenticated returns False when not authenticated"""
        mock_session = {}
        mocker.patch.object(st, 'session_state', mock_session)
        
        assert is_authenticated() is False
    
    def test_get_current_user_authenticated(self, mocker):
        """Test get_current_user returns user info when authenticated"""
        mock_session = {
            'authenticated': True,
            'user_id': 1,
            'username': 'testuser',
            'role': 'admin'
        }
        mocker.patch.object(st, 'session_state', mock_session)
        
        user_id, username, role = get_current_user()
        
        assert user_id == 1
        assert username == 'testuser'
        assert role == 'admin'
    
    def test_get_current_user_not_authenticated(self, mocker):
        """Test get_current_user returns None values when not authenticated"""
        mock_session = {}
        mocker.patch.object(st, 'session_state', mock_session)
        
        user_id, username, role = get_current_user()
        
        assert user_id is None
        assert username is None
        assert role is None
