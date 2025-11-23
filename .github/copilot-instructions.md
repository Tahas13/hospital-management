# GDPR-Compliant Hospital Management System - AI Agent Instructions

## Project Overview
A Streamlit-based hospital management dashboard implementing CIA triad (Confidentiality, Integrity, Availability) with GDPR compliance. Uses SQLite database with role-based access control, Fernet encryption, data anonymization, and comprehensive audit logging.

## Architecture & Data Flow

### Core Components
- **Authentication Layer**: Login system validating credentials against `users` table, assigning roles (admin/doctor/receptionist)
- **RBAC Engine**: Role-based permissions controlling data access and operations per user type
- **Anonymization Service**: Data masking/encryption applied to `patients` table sensitive fields
- **Audit Logger**: All operations logged to `logs` table with timestamp, user_id, role, action, details
- **Database Layer**: SQLite database (`hospital.db`) with three tables: `users`, `patients`, `logs`
- **Encryption Service**: Fernet symmetric encryption for reversible data protection using stored key

### Data Flow Pattern
1. User login → credentials verified → role assigned to session
2. Role determines UI elements and data visibility (decorator pattern for route protection)
3. Data operations trigger logging before/after execution
4. Sensitive data displayed only after anonymization filter applied based on role
5. All DB writes wrapped in try/except with rollback on failure

## Database Schema & Conventions

### Table: users
```sql
user_id (PK, INTEGER), username (UNIQUE, TEXT), password (TEXT - hashed with hashlib.sha256), role (TEXT: 'admin'|'doctor'|'receptionist')
```

### Table: patients
```sql
patient_id (PK, INTEGER), name (TEXT), contact (TEXT), diagnosis (TEXT), 
anonymized_name (TEXT), anonymized_contact (TEXT), date_added (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
```

### Table: logs
```sql
log_id (PK, INTEGER), user_id (INTEGER FK), role (TEXT), action (TEXT), 
timestamp (TIMESTAMP DEFAULT CURRENT_TIMESTAMP), details (TEXT)
```

**Convention**: Always insert into `logs` table after any CRUD operation. Use parameterized queries to prevent SQL injection.

## Security Implementation Patterns

### Confidentiality
- **Password Storage**: Use `hashlib.sha256(password.encode()).hexdigest()` - never store plaintext
- **Fernet Encryption (Primary Approach)**:
  ```python
  from cryptography.fernet import Fernet
  # Generate key once: Fernet.generate_key() → store in .env as ENCRYPTION_KEY
  # Initialize: cipher = Fernet(os.getenv('ENCRYPTION_KEY'))
  # Encrypt: cipher.encrypt(data.encode()).decode()
  # Decrypt: cipher.decrypt(encrypted_data.encode()).decode()
  ```
  - Encrypt `name`, `contact`, `diagnosis` before storing in database
  - Decrypt on retrieval based on user role permissions
  - Store encryption key in `.env` file (never commit to git)
- **Data Masking Function** (for display to non-admins):
  - Names → `ANON_{patient_id}` 
  - Contacts → `XXX-XXX-{last_4_digits}`
  - Diagnoses → Hash or generic category
- **Session Management**: Store `role` and `user_id` in `st.session_state` after login, check before rendering sensitive components

### Integrity
- **Logging Pattern**: Every function modifying data must call `log_action(user_id, role, action_type, details)` 
- **Validation**: Check `st.session_state.role` before allowing updates/deletes
- **Audit Display**: Admin-only page showing `logs` table with filters for date/user/action

### Availability
- **Error Handling**: Wrap all DB operations in try/except, display user-friendly errors via `st.error()`
- **Backup Feature**: Admin button to export `patients` and `logs` tables as CSV using `pd.DataFrame.to_csv()`
- **Connection Pooling**: Reuse DB connection via singleton pattern: `@st.cache_resource` decorator for connection function

## Role-Based Access Matrix

| Role         | View Raw Data | View Anonymized | Add/Edit Records | Delete Records | View Logs | Export Data |
|--------------|---------------|------------------|------------------|----------------|-----------|-------------|
| Admin        | ✓             | ✓                | ✓                | ✓              | ✓         | ✓           |
| Doctor       | ✗             | ✓                | ✗                | ✗              | ✗         | ✗           |
| Receptionist | ✗             | ✗                | ✓                | ✗              | ✗         | ✗           |

**Implementation**: Use `if st.session_state.role == 'admin':` to conditionally render UI sections and enable operations.

## Critical Developer Workflows

### Initial Setup
```bash
pip install streamlit pandas cryptography python-dotenv
# SQLite requires no additional installation (built into Python)
# Create .env file with ENCRYPTION_KEY=<generated_fernet_key>
```

### Encryption Key Generation
```python
# Run once to generate encryption key
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(f"Add to .env file:\nENCRYPTION_KEY={key.decode()}")
```

### Database Initialization
Create `init_db.py` to set up schema and seed admin user. Run once: `python init_db.py`

### Running the App
```bash
streamlit run app.py
# Access at http://localhost:8501
# Default admin credentials: username='admin', password='admin123' (hashed)
```

### Testing Roles
Seed users table with all three roles for testing. Use Streamlit's session_state inspector (`Ctrl+Shift+I` in dev mode).

## Streamlit-Specific Patterns

### Page Structure
- **Login Page**: Form with username/password, validate against hashed password in DB, set `st.session_state.authenticated = True` and `st.session_state.role`
- **Main Dashboard**: Check `if 'authenticated' not in st.session_state or not st.session_state.authenticated: st.warning() + st.stop()`
- **Sidebar Navigation**: Use `st.sidebar.radio()` to switch between views (Dashboard, Add Patient, Audit Logs, etc.)

### State Management
- Always check session state exists before accessing: `if 'role' in st.session_state:`
- Clear session on logout: `for key in list(st.session_state.keys()): del st.session_state[key]`

### Form Handling
Use `st.form()` context manager for inputs to batch submissions and prevent reruns on every keystroke.

## GDPR Features (Bonus)

### Data Retention
- Add `retention_days` column to patients table
- Background job (or manual admin button) to delete records older than specified days
- Log deletion actions with reason: "GDPR retention policy"

### Consent Banner
- Add `consent_given` boolean column to patients table
- Display banner on receptionist's add-patient form
- Store consent timestamp in logs

### Real-time Activity Graphs
Use `st.line_chart()` or `st.bar_chart()` with aggregated log data: `SELECT DATE(timestamp) as date, COUNT(*) as actions FROM logs GROUP BY DATE(timestamp)`

## Testing Strategy

### Unit Tests Structure
Create `tests/test_*.py` files using pytest. Install: `pip install pytest pytest-mock`

### Critical Test Cases
```python
# tests/test_auth.py - Authentication logic
- test_password_hashing(): Verify sha256 hashing consistency
- test_login_valid_credentials(): Check successful login flow
- test_login_invalid_credentials(): Verify rejection of bad passwords
- test_role_assignment(): Ensure correct role set in session

# tests/test_anonymizer.py - Data masking functions
- test_anonymize_name(): Verify ANON_{id} format
- test_anonymize_contact(): Check XXX-XXX-{last4} pattern
- test_decrypt_for_admin(): Ensure Fernet decryption works
- test_masking_for_non_admin(): Verify non-admins see masked data

# tests/test_database.py - Database operations
- test_add_patient(): Check insert with encryption
- test_log_action(): Verify logging mechanism
- test_retrieve_encrypted_data(): Confirm data retrieval and decryption
- test_sql_injection_prevention(): Validate parameterized queries

# tests/test_rbac.py - Role-based access control
- test_admin_full_access(): Verify admin can view/edit/delete
- test_doctor_read_only(): Ensure doctor cannot modify data
- test_receptionist_limited_write(): Check receptionist can add but not view sensitive data
```

### Running Tests
```bash
pytest tests/ -v --cov=. --cov-report=html
# View coverage report in htmlcov/index.html
```

### Mock Database Pattern
```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor
```

## Deployment to Streamlit Cloud

### Prerequisites
1. Push code to GitHub repository (exclude `.env` file via `.gitignore`)
2. Ensure `requirements.txt` contains: `streamlit pandas cryptography python-dotenv`
3. Create `secrets.toml` format for Streamlit secrets management

### Deployment Steps
```bash
# 1. Create .streamlit/secrets.toml locally (for testing)
mkdir .streamlit
echo 'ENCRYPTION_KEY = "your-fernet-key-here"' > .streamlit/secrets.toml

# 2. Add to .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
echo ".env" >> .gitignore
echo "hospital.db" >> .gitignore

# 3. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/hospital-management.git
git push -u origin main
```

### Streamlit Cloud Configuration
1. Go to https://share.streamlit.io/
2. Click "New app" → Select your GitHub repository
3. Set main file path: `app.py`
4. Go to "Advanced settings" → "Secrets"
5. Add secrets in TOML format:
   ```toml
   ENCRYPTION_KEY = "your-fernet-key-here"
   ```
6. Click "Deploy"

### Access Secrets in Code
```python
import streamlit as st
import os

# Works both locally (.env) and on Streamlit Cloud (secrets)
if 'ENCRYPTION_KEY' in st.secrets:
    ENCRYPTION_KEY = st.secrets['ENCRYPTION_KEY']
else:
    from dotenv import load_dotenv
    load_dotenv()
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
```

### Database Persistence on Cloud
- SQLite file will reset on redeployment
- For persistent storage, use Streamlit's `st.cache_resource` for DB connection
- Consider migrating to PostgreSQL (free tier: Supabase, ElephantSQL) for production persistence

## Common Pitfalls

1. **Password Hashing**: Don't compare plaintext passwords - hash input before comparison
2. **SQL Injection**: Always use parameterized queries: `cursor.execute("SELECT * FROM users WHERE username=?", (username,))`
3. **Session Persistence**: Streamlit reruns entire script on interaction - use session_state for persistence
4. **Anonymization Timing**: Apply masking during SELECT query result processing, not in database storage (keep raw data for admin access)
5. **Log Verbosity**: Don't log sensitive data in `details` field - log action type and anonymized identifiers only
6. **Encryption Key Management**: Never commit `.env` or `secrets.toml` to git - use `.gitignore`
7. **Database Locking**: SQLite doesn't handle concurrent writes well - use `timeout` parameter in connection: `sqlite3.connect('hospital.db', timeout=10.0)`

## Key Files Reference (To Be Created)

- `app.py` - Main Streamlit application with page routing
- `database.py` - DB connection, CRUD operations, logging functions
- `auth.py` - Login validation, password hashing, session management
- `anonymizer.py` - Data masking functions for different field types
- `init_db.py` - Schema creation and initial data seeding
- `requirements.txt` - Python dependencies
