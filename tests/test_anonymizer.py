"""
Unit Tests for Anonymization Module
Tests encryption, decryption, and data masking functions
"""
import pytest
from anonymizer import (
    encrypt_data, decrypt_data, anonymize_name, anonymize_contact,
    anonymize_diagnosis, prepare_patient_data_for_role
)
import os
from cryptography.fernet import Fernet


@pytest.fixture
def setup_test_key(monkeypatch):
    """Set up test encryption key"""
    test_key = Fernet.generate_key()
    monkeypatch.setenv('ENCRYPTION_KEY', test_key.decode())
    return test_key


class TestEncryption:
    """Test encryption and decryption functions"""
    
    def test_encrypt_data_returns_string(self, setup_test_key):
        """Test that encrypt_data returns a string"""
        result = encrypt_data("test data")
        assert isinstance(result, str)
    
    def test_encrypt_data_not_empty(self, setup_test_key):
        """Test that encryption produces non-empty result"""
        result = encrypt_data("test data")
        assert len(result) > 0
    
    def test_encrypt_empty_string(self, setup_test_key):
        """Test encryption of empty string"""
        result = encrypt_data("")
        assert result == ""
    
    def test_decrypt_data_correct(self, setup_test_key):
        """Test that decryption returns original data"""
        original = "sensitive data"
        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)
        assert decrypted == original
    
    def test_decrypt_empty_string(self, setup_test_key):
        """Test decryption of empty string"""
        result = decrypt_data("")
        assert result == ""
    
    def test_encrypt_decrypt_round_trip(self, setup_test_key):
        """Test full encryption-decryption cycle"""
        test_data = [
            "John Doe",
            "123-456-7890",
            "Patient has chronic condition"
        ]
        
        for data in test_data:
            encrypted = encrypt_data(data)
            decrypted = decrypt_data(encrypted)
            assert decrypted == data
    
    def test_different_inputs_different_outputs(self, setup_test_key):
        """Test that different inputs produce different encrypted outputs"""
        encrypted1 = encrypt_data("data1")
        encrypted2 = encrypt_data("data2")
        assert encrypted1 != encrypted2


class TestAnonymization:
    """Test data anonymization functions"""
    
    def test_anonymize_name_format(self):
        """Test that anonymize_name returns correct format"""
        result = anonymize_name(1021)
        assert result == "ANON_1021"
    
    def test_anonymize_name_different_ids(self):
        """Test that different IDs produce different anonymized names"""
        result1 = anonymize_name(1)
        result2 = anonymize_name(2)
        assert result1 != result2
        assert result1 == "ANON_1"
        assert result2 == "ANON_2"
    
    def test_anonymize_contact_format(self):
        """Test that anonymize_contact masks correctly"""
        result = anonymize_contact("123-456-7890")
        assert result == "XXX-XXX-7890"
    
    def test_anonymize_contact_short_number(self):
        """Test anonymize_contact with short number"""
        result = anonymize_contact("123")
        assert result == "XXX-XXX-XXXX"
    
    def test_anonymize_contact_empty(self):
        """Test anonymize_contact with empty string"""
        result = anonymize_contact("")
        assert result == "XXX-XXX-XXXX"
    
    def test_anonymize_diagnosis_respiratory(self):
        """Test diagnosis anonymization for respiratory conditions"""
        diagnoses = ["Common cold", "Fever and flu", "Persistent cough"]
        for diagnosis in diagnoses:
            result = anonymize_diagnosis(diagnosis)
            assert result == "Respiratory Condition"
    
    def test_anonymize_diagnosis_metabolic(self):
        """Test diagnosis anonymization for metabolic conditions"""
        diagnoses = ["Type 2 diabetes", "High blood sugar", "Insulin resistance"]
        for diagnosis in diagnoses:
            result = anonymize_diagnosis(diagnosis)
            assert result == "Metabolic Condition"
    
    def test_anonymize_diagnosis_cardiovascular(self):
        """Test diagnosis anonymization for cardiovascular conditions"""
        diagnoses = ["Heart disease", "High blood pressure", "Cardiac arrest"]
        for diagnosis in diagnoses:
            result = anonymize_diagnosis(diagnosis)
            assert result == "Cardiovascular Condition"
    
    def test_anonymize_diagnosis_injury(self):
        """Test diagnosis anonymization for injuries"""
        diagnoses = ["Bone fracture", "Severe injury", "Deep wound"]
        for diagnosis in diagnoses:
            result = anonymize_diagnosis(diagnosis)
            assert result == "Injury/Trauma"
    
    def test_anonymize_diagnosis_general(self):
        """Test diagnosis anonymization for general conditions"""
        result = anonymize_diagnosis("Unknown condition")
        assert result == "General Medical Condition"
    
    def test_anonymize_diagnosis_empty(self):
        """Test diagnosis anonymization with empty string"""
        result = anonymize_diagnosis("")
        assert result == "[Restricted]"


class TestRoleBasedDataPreparation:
    """Test role-based data preparation"""
    
    def test_prepare_data_for_admin(self, setup_test_key):
        """Test that admin sees decrypted data"""
        patient_data = {
            'patient_id': 1,
            'name': encrypt_data("John Doe"),
            'contact': encrypt_data("123-456-7890"),
            'diagnosis': encrypt_data("Fever"),
            'date_added': '2025-01-01'
        }
        
        result = prepare_patient_data_for_role(patient_data, 'admin')
        
        assert result['name'] == "John Doe"
        assert result['contact'] == "123-456-7890"
        assert result['diagnosis'] == "Fever"
    
    def test_prepare_data_for_doctor(self, setup_test_key):
        """Test that doctor sees anonymized data"""
        patient_data = {
            'patient_id': 1,
            'name': encrypt_data("John Doe"),
            'contact': encrypt_data("123-456-7890"),
            'diagnosis': encrypt_data("Fever"),
            'date_added': '2025-01-01'
        }
        
        result = prepare_patient_data_for_role(patient_data, 'doctor')
        
        assert result['name'] == "ANON_1"
        assert result['contact'] == "XXX-XXX-7890"
        assert result['diagnosis'] == "Respiratory Condition"
    
    def test_prepare_data_for_receptionist(self, setup_test_key):
        """Test that receptionist sees restricted diagnosis"""
        patient_data = {
            'patient_id': 1,
            'name': encrypt_data("John Doe"),
            'contact': encrypt_data("123-456-7890"),
            'diagnosis': encrypt_data("Fever"),
            'date_added': '2025-01-01'
        }
        
        result = prepare_patient_data_for_role(patient_data, 'receptionist')
        
        assert result['name'] == "ANON_1"
        assert result['contact'] == "XXX-XXX-7890"
        assert result['diagnosis'] == "[Restricted]"
    
    def test_prepare_data_unknown_role(self, setup_test_key):
        """Test that unknown role sees fully restricted data"""
        patient_data = {
            'patient_id': 1,
            'name': encrypt_data("John Doe"),
            'contact': encrypt_data("123-456-7890"),
            'diagnosis': encrypt_data("Fever"),
            'date_added': '2025-01-01'
        }
        
        result = prepare_patient_data_for_role(patient_data, 'unknown')
        
        assert result['name'] == "[Restricted]"
        assert result['contact'] == "[Restricted]"
        assert result['diagnosis'] == "[Restricted]"
