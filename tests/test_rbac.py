"""
Integration Tests for Role-Based Access Control (RBAC)
Tests that roles have appropriate permissions
"""
import pytest
from cryptography.fernet import Fernet
from anonymizer import prepare_patient_data_for_role, encrypt_data


@pytest.fixture
def setup_test_key(monkeypatch):
    """Set up test encryption key"""
    test_key = Fernet.generate_key()
    monkeypatch.setenv('ENCRYPTION_KEY', test_key.decode())
    return test_key


@pytest.fixture
def sample_patient_data(setup_test_key):
    """Create sample patient data"""
    return {
        'patient_id': 1,
        'name': encrypt_data("John Doe"),
        'contact': encrypt_data("123-456-7890"),
        'diagnosis': encrypt_data("Fever and flu"),
        'date_added': '2025-01-01 10:00:00'
    }


class TestAdminAccess:
    """Test admin role permissions"""
    
    def test_admin_sees_raw_data(self, sample_patient_data):
        """Verify admin can view decrypted raw data"""
        result = prepare_patient_data_for_role(sample_patient_data, 'admin')
        
        assert result['name'] == "John Doe"
        assert result['contact'] == "123-456-7890"
        assert result['diagnosis'] == "Fever and flu"
    
    def test_admin_full_access_to_all_fields(self, sample_patient_data):
        """Verify admin has access to all patient fields"""
        result = prepare_patient_data_for_role(sample_patient_data, 'admin')
        
        assert 'patient_id' in result
        assert 'name' in result
        assert 'contact' in result
        assert 'diagnosis' in result
        assert 'date_added' in result


class TestDoctorAccess:
    """Test doctor role permissions"""
    
    def test_doctor_sees_anonymized_data(self, sample_patient_data):
        """Verify doctor sees anonymized patient data"""
        result = prepare_patient_data_for_role(sample_patient_data, 'doctor')
        
        # Name should be anonymized
        assert result['name'] == "ANON_1"
        # Contact should be masked
        assert result['contact'] == "XXX-XXX-7890"
        # Diagnosis should be categorized
        assert result['diagnosis'] == "Respiratory Condition"
    
    def test_doctor_cannot_see_raw_personal_info(self, sample_patient_data):
        """Verify doctor cannot see raw personal information"""
        result = prepare_patient_data_for_role(sample_patient_data, 'doctor')
        
        assert result['name'] != "John Doe"
        assert "John" not in result['name']
    
    def test_doctor_sees_categorized_diagnosis(self, sample_patient_data):
        """Verify doctor sees categorized diagnosis not raw details"""
        result = prepare_patient_data_for_role(sample_patient_data, 'doctor')
        
        # Should see category, not specific diagnosis
        assert result['diagnosis'] != "Fever and flu"
        assert "Respiratory" in result['diagnosis'] or "Condition" in result['diagnosis']


class TestReceptionistAccess:
    """Test receptionist role permissions"""
    
    def test_receptionist_cannot_view_diagnosis(self, sample_patient_data):
        """Verify receptionist cannot view diagnosis"""
        result = prepare_patient_data_for_role(sample_patient_data, 'receptionist')
        
        assert result['diagnosis'] == "[Restricted]"
    
    def test_receptionist_sees_masked_data(self, sample_patient_data):
        """Verify receptionist sees masked patient data"""
        result = prepare_patient_data_for_role(sample_patient_data, 'receptionist')
        
        assert result['name'] == "ANON_1"
        assert result['contact'] == "XXX-XXX-7890"
    
    def test_receptionist_limited_access(self, sample_patient_data):
        """Verify receptionist has most limited access"""
        result = prepare_patient_data_for_role(sample_patient_data, 'receptionist')
        
        # Should not see any sensitive information
        assert "John Doe" not in str(result.values())
        assert "Fever" not in str(result.values())


class TestRoleComparison:
    """Test comparison between different roles"""
    
    def test_admin_sees_more_than_doctor(self, sample_patient_data):
        """Verify admin has more access than doctor"""
        admin_data = prepare_patient_data_for_role(sample_patient_data, 'admin')
        doctor_data = prepare_patient_data_for_role(sample_patient_data, 'doctor')
        
        # Admin sees real name, doctor doesn't
        assert admin_data['name'] != doctor_data['name']
        assert admin_data['name'] == "John Doe"
        assert doctor_data['name'] == "ANON_1"
    
    def test_doctor_sees_more_than_receptionist(self, sample_patient_data):
        """Verify doctor has more access than receptionist"""
        doctor_data = prepare_patient_data_for_role(sample_patient_data, 'doctor')
        receptionist_data = prepare_patient_data_for_role(sample_patient_data, 'receptionist')
        
        # Doctor sees categorized diagnosis, receptionist sees nothing
        assert doctor_data['diagnosis'] != "[Restricted]"
        assert receptionist_data['diagnosis'] == "[Restricted]"
    
    def test_access_hierarchy(self, sample_patient_data):
        """Verify access hierarchy: Admin > Doctor > Receptionist"""
        admin_data = prepare_patient_data_for_role(sample_patient_data, 'admin')
        doctor_data = prepare_patient_data_for_role(sample_patient_data, 'doctor')
        receptionist_data = prepare_patient_data_for_role(sample_patient_data, 'receptionist')
        
        # Calculate "information visibility" score
        def visibility_score(data):
            score = 0
            if "John Doe" in str(data.values()):
                score += 3
            if "ANON" not in data['name']:
                score += 2
            if data['diagnosis'] not in ["[Restricted]", "General Medical Condition"]:
                score += 1
            return score
        
        admin_score = visibility_score(admin_data)
        doctor_score = visibility_score(doctor_data)
        receptionist_score = visibility_score(receptionist_data)
        
        assert admin_score > doctor_score > receptionist_score


class TestUnauthorizedAccess:
    """Test handling of unauthorized roles"""
    
    def test_unknown_role_restricted(self, sample_patient_data):
        """Verify unknown role gets fully restricted access"""
        result = prepare_patient_data_for_role(sample_patient_data, 'hacker')
        
        assert result['name'] == "[Restricted]"
        assert result['contact'] == "[Restricted]"
        assert result['diagnosis'] == "[Restricted]"
    
    def test_empty_role_restricted(self, sample_patient_data):
        """Verify empty role gets restricted access"""
        result = prepare_patient_data_for_role(sample_patient_data, '')
        
        assert result['name'] == "[Restricted]"
        assert result['contact'] == "[Restricted]"
        assert result['diagnosis'] == "[Restricted]"
