"""
Anonymization Module
Handles data encryption, decryption, and masking for privacy protection
"""
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Initialize Fernet cipher
def get_cipher():
    """Get Fernet cipher instance with encryption key"""
    key = None
    
    # Try to get key from Streamlit secrets first (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and 'ENCRYPTION_KEY' in st.secrets:
            key = st.secrets['ENCRYPTION_KEY']
    except:
        pass
    
    # If not in secrets, try environment variable
    if not key:
        key = os.getenv('ENCRYPTION_KEY')
    
    if not key:
        raise ValueError("ENCRYPTION_KEY not found in environment or secrets. Please create a .env file with ENCRYPTION_KEY=your-key")
    
    # Convert string key to bytes if necessary
    if isinstance(key, str):
        key = key.encode()
    
    return Fernet(key)


def encrypt_data(data: str) -> str:
    """
    Encrypt data using Fernet symmetric encryption
    
    Args:
        data: Plain text data to encrypt
        
    Returns:
        Encrypted data as string
    """
    if not data:
        return ""
    
    cipher = get_cipher()
    encrypted = cipher.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt data using Fernet symmetric encryption
    
    Args:
        encrypted_data: Encrypted data string
        
    Returns:
        Decrypted plain text data
    """
    if not encrypted_data:
        return ""
    
    try:
        cipher = get_cipher()
        decrypted = cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        return "[Decryption Error]"


def anonymize_name(patient_id: int) -> str:
    """
    Anonymize patient name
    
    Args:
        patient_id: Patient's database ID
        
    Returns:
        Anonymized name in format ANON_{id}
    """
    return f"ANON_{patient_id}"


def anonymize_contact(contact: str) -> str:
    """
    Mask contact number showing only last 4 digits
    
    Args:
        contact: Full contact number
        
    Returns:
        Masked contact in format XXX-XXX-{last4}
    """
    if not contact or len(contact) < 4:
        return "XXX-XXX-XXXX"
    
    last_four = contact[-4:]
    return f"XXX-XXX-{last_four}"


def anonymize_diagnosis(diagnosis: str) -> str:
    """
    Anonymize diagnosis to generic category
    
    Args:
        diagnosis: Full diagnosis
        
    Returns:
        Generic diagnosis category
    """
    if not diagnosis:
        return "[Restricted]"
    
    # Simple categorization based on keywords
    diagnosis_lower = diagnosis.lower()
    
    if any(word in diagnosis_lower for word in ['fever', 'flu', 'cold', 'cough']):
        return "Respiratory Condition"
    elif any(word in diagnosis_lower for word in ['diabetes', 'sugar', 'insulin']):
        return "Metabolic Condition"
    elif any(word in diagnosis_lower for word in ['heart', 'cardiac', 'blood pressure']):
        return "Cardiovascular Condition"
    elif any(word in diagnosis_lower for word in ['fracture', 'injury', 'wound']):
        return "Injury/Trauma"
    else:
        return "General Medical Condition"


def prepare_patient_data_for_role(patient_data: dict, role: str) -> dict:
    """
    Prepare patient data based on user role
    
    Args:
        patient_data: Dictionary containing patient information
        role: User's role (admin/doctor/receptionist)
        
    Returns:
        Modified patient data dictionary based on role permissions
    """
    if role == 'admin':
        # Admin sees raw decrypted data
        return {
            'patient_id': patient_data['patient_id'],
            'name': decrypt_data(patient_data['name']),
            'contact': decrypt_data(patient_data['contact']),
            'diagnosis': decrypt_data(patient_data['diagnosis']),
            'date_added': patient_data['date_added']
        }
    elif role == 'doctor':
        # Doctor sees anonymized data
        return {
            'patient_id': patient_data['patient_id'],
            'name': anonymize_name(patient_data['patient_id']),
            'contact': anonymize_contact(decrypt_data(patient_data['contact'])),
            'diagnosis': anonymize_diagnosis(decrypt_data(patient_data['diagnosis'])),
            'date_added': patient_data['date_added']
        }
    elif role == 'receptionist':
        # Receptionist sees minimal anonymized data
        return {
            'patient_id': patient_data['patient_id'],
            'name': anonymize_name(patient_data['patient_id']),
            'contact': anonymize_contact(decrypt_data(patient_data['contact'])),
            'diagnosis': "[Restricted]",
            'date_added': patient_data['date_added']
        }
    else:
        # Unknown role - return fully restricted data
        return {
            'patient_id': patient_data['patient_id'],
            'name': "[Restricted]",
            'contact': "[Restricted]",
            'diagnosis': "[Restricted]",
            'date_added': patient_data['date_added']
        }
