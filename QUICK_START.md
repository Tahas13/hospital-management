# Quick Reference Guide

## 🚀 Getting Started (5 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate encryption key and save output
python -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"

# 3. Create .env file with the key
echo "ENCRYPTION_KEY=your-key-here" > .env

# 4. Initialize database
python init_db.py

# 5. Run application
streamlit run app.py
```

---

## 🔐 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `dr_bob` | `doc123` |
| Receptionist | `alice_recep` | `rec123` |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit interface |
| `database.py` | All database operations |
| `auth.py` | Authentication & sessions |
| `anonymizer.py` | Encryption & masking |
| `init_db.py` | Database setup script |

---

## 🎭 Role Permissions

### Admin (Full Access)
✅ View raw data  
✅ Add/Edit/Delete patients  
✅ View audit logs  
✅ Export data  
✅ View analytics  

### Doctor (Read-Only Anonymized)
✅ View anonymized patients  
❌ Modify records  
❌ View logs  
❌ Export data  

### Receptionist (Limited Write)
✅ Add patients  
✅ Edit basic info  
❌ View diagnoses  
❌ Delete patients  
❌ View logs  

---

## 🧪 Testing Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
pytest tests/test_anonymizer.py -v
pytest tests/test_database.py -v
pytest tests/test_rbac.py -v
```

---

## 🔍 Key Features

### Confidentiality
- Fernet encryption for all patient data
- SHA-256 password hashing
- Role-based access control
- Automatic data anonymization

### Integrity
- Every action logged with timestamp
- SQL injection prevention (parameterized queries)
- Input validation
- Immutable audit trail

### Availability
- Comprehensive error handling
- CSV export for backup
- System uptime monitoring
- Responsive web interface

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "ENCRYPTION_KEY not found"
Create `.env` file with encryption key

### "No such table: users"
```bash
python init_db.py
```

### Port already in use
```bash
streamlit run app.py --server.port 8502
```

---

## 📊 Database Schema

### users
- user_id (PK)
- username (UNIQUE)
- password (SHA-256 hashed)
- role (admin/doctor/receptionist)

### patients
- patient_id (PK)
- name (Fernet encrypted)
- contact (Fernet encrypted)
- diagnosis (Fernet encrypted)
- date_added (timestamp)

### logs
- log_id (PK)
- user_id (FK)
- role
- action
- timestamp
- details

---

## 🔒 Security Best Practices

⚠️ Never commit `.env` file  
⚠️ Change default passwords in production  
⚠️ Keep encryption key backed up securely  
⚠️ Review audit logs regularly  
⚠️ Use HTTPS in production  

---

## 📈 Activity Metrics

The dashboard shows:
- Total patient count
- Total actions logged
- Actions today
- Most active user
- Daily activity graph (7-30 days)

---

## 💾 Data Export

Admin can export:
- Patient records (with decrypted data)
- Audit logs
- Both as CSV files with timestamps

---

## 🎯 Common Tasks

### Add New Patient
1. Login as receptionist or admin
2. Navigate to "Add Patient"
3. Fill form + check consent
4. Submit

### View Anonymized Data
1. Login as doctor
2. Navigate to "View Patients"
3. See ANON_XXX format

### View Audit Logs
1. Login as admin
2. Navigate to "Audit Logs"
3. Filter by action/user

### Export Data
1. Login as admin
2. Navigate to "Data Export"
3. Click download buttons

---

## 🔑 Encryption Examples

### Encrypt
```python
from anonymizer import encrypt_data
encrypted = encrypt_data("John Doe")
# Returns: Fernet encrypted string
```

### Decrypt
```python
from anonymizer import decrypt_data
decrypted = decrypt_data(encrypted)
# Returns: "John Doe"
```

### Anonymize
```python
from anonymizer import anonymize_name, anonymize_contact
name = anonymize_name(1021)  # Returns: "ANON_1021"
contact = anonymize_contact("555-123-4567")  # Returns: "XXX-XXX-4567"
```

---

## 📝 Logging Example

```python
from database import log_action
log_action(user_id=1, role='admin', action='VIEW_PATIENTS', details='Viewed 10 records')
```

---

## 🌐 Deployment

### Streamlit Cloud
1. Push to GitHub
2. Go to share.streamlit.io
3. Create new app
4. Add secrets (ENCRYPTION_KEY)
5. Deploy

---

## 📞 Support Files

- **Detailed Setup**: See `SETUP.md`
- **Full Documentation**: See `Assignment4.ipynb`
- **Architecture**: See `.github/copilot-instructions.md`
- **Checklist**: See `CHECKLIST.md`

---

## ✅ Quick Verification

After setup, test:
- [ ] Application starts
- [ ] Can login with all roles
- [ ] Admin sees decrypted data
- [ ] Doctor sees anonymized data
- [ ] Can add patient
- [ ] Audit logs populate
- [ ] Tests pass

---

**Version**: 1.0  
**Quick Start Time**: ~5 minutes  
**Full Setup Time**: ~10 minutes
