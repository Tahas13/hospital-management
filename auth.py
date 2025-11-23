"""
Authentication Module
Handles user authentication, password hashing, and session management
"""
import hashlib
import streamlit as st


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as hexadecimal string
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hashed version
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hashed password
        
    Returns:
        True if passwords match, False otherwise
    """
    return hash_password(plain_password) == hashed_password


def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None


def login_user(user_id: int, username: str, role: str):
    """
    Set session state for logged in user
    
    Args:
        user_id: User's database ID
        username: User's username
        role: User's role (admin/doctor/receptionist)
    """
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.username = username
    st.session_state.role = role


def logout_user():
    """Clear all session state on logout"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)


def get_current_user():
    """
    Get current user information
    
    Returns:
        Tuple of (user_id, username, role) or (None, None, None) if not authenticated
    """
    if is_authenticated():
        return (
            st.session_state.user_id,
            st.session_state.username,
            st.session_state.role
        )
    return None, None, None


def require_role(allowed_roles: list):
    """
    Decorator to restrict access to specific roles
    
    Args:
        allowed_roles: List of roles allowed to access the function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_authenticated():
                st.warning("⚠️ Please log in to access this feature")
                st.stop()
            if st.session_state.role not in allowed_roles:
                st.error("🚫 You don't have permission to access this feature")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator
