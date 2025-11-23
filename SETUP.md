# GDPR-Compliant Hospital Management System - Setup Guide

## 🚀 Quick Start

Follow these steps to get the Hospital Management System running on your machine.

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- streamlit (web interface)
- pandas (data manipulation)
- cryptography (Fernet encryption)
- python-dotenv (environment variables)
- pytest, pytest-mock, pytest-cov (testing)

### Step 2: Generate Encryption Key

Run this Python command to generate a Fernet encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"
```

### Step 3: Create .env File

Create a file named `.env` in the project root directory:

```bash
# Windows (PowerShell)
New-Item .env

# Linux/Mac
touch .env
```

Add the encryption key to `.env`:

```
ENCRYPTION_KEY=your-generated-key-from-step-2
```

**⚠️ IMPORTANT**: Never commit the `.env` file to git! It's already in `.gitignore`.

### Step 4: Initialize Database

Run the database initialization script:

```bash
python init_db.py
```

This will:
- Create the SQLite database (`hospital.db`)
- Set up the schema (users, patients, logs tables)
- Seed initial users with default credentials

### Step 5: Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`

### Step 6: Login

Use these default credentials to log in:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | admin | admin123 |
| **Doctor** | dr_bob | doc123 |
| **Receptionist** | alice_recep | rec123 |

---

## 🧪 Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=. --cov-report=html
```

View coverage report:
- Open `htmlcov/index.html` in your browser

### Run Specific Test Files

```bash
# Test authentication
pytest tests/test_auth.py -v

# Test anonymization
pytest tests/test_anonymizer.py -v

# Test database operations
pytest tests/test_database.py -v

# Test RBAC
pytest tests/test_rbac.py -v
```

---

## 📁 Project Structure

```
hospital-management/
├── app.py                     # Main Streamlit application
├── auth.py                    # Authentication and session management
├── anonymizer.py              # Encryption and data anonymization
├── database.py                # Database operations and logging
├── init_db.py                 # Database initialization script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .env.example               # Example environment file
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
├── SETUP.md                   # This file
├── Assignment4.ipynb          # Jupyter notebook with documentation
├── .github/
│   └── copilot-instructions.md  # AI agent instructions
└── tests/                     # Unit tests
    ├── __init__.py
    ├── test_auth.py
    ├── test_anonymizer.py
    ├── test_database.py
    └── test_rbac.py
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'cryptography'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "ValueError: ENCRYPTION_KEY not found"

**Solution**: Create `.env` file with encryption key (see Step 2 & 3)

### Issue: "sqlite3.OperationalError: no such table: users"

**Solution**: Initialize the database
```bash
python init_db.py
```

### Issue: "Address already in use" when running Streamlit

**Solution**: Stop other Streamlit instances or use a different port
```bash
streamlit run app.py --server.port 8502
```

### Issue: Tests failing with database errors

**Solution**: Make sure you have initialized the main database
```bash
python init_db.py
```

---

## 🌐 Deployment to Streamlit Cloud

### Prerequisites

1. GitHub account
2. Streamlit Cloud account (free at https://share.streamlit.io/)

### Steps

1. **Push to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/hospital-management.git
git push -u origin main
```

2. **Configure Streamlit Cloud**

- Go to https://share.streamlit.io/
- Click "New app"
- Select your repository
- Set main file: `app.py`
- Click "Advanced settings" → "Secrets"
- Add your encryption key:

```toml
ENCRYPTION_KEY = "your-fernet-key-here"
```

3. **Deploy**

- Click "Deploy"
- Wait for deployment to complete
- Your app will be live at `https://your-app-name.streamlit.app`

---

## 📊 Features Overview

### Confidentiality
✅ Fernet encryption for patient data  
✅ Role-based access control (RBAC)  
✅ Data anonymization for non-admins  
✅ SHA-256 password hashing  

### Integrity
✅ Comprehensive audit logging  
✅ SQL injection prevention  
✅ Input validation  
✅ Action tracking with timestamps  

### Availability
✅ Error handling throughout  
✅ Data backup/export (CSV)  
✅ System uptime monitoring  
✅ Responsive web interface  

### GDPR Compliance
✅ Data minimization  
✅ Consent management  
✅ Right to access  
✅ Right to erasure  
✅ Data portability  

---

## 🎯 User Guide

### As Admin

1. **View All Data**: Access raw, decrypted patient information
2. **Manage Patients**: Add, edit, delete patient records
3. **View Logs**: Access complete audit trail
4. **Export Data**: Download CSV backups
5. **View Analytics**: See activity graphs and statistics

### As Doctor

1. **View Patients**: See anonymized patient data
   - Names: ANON_1021
   - Contacts: XXX-XXX-4567
   - Diagnoses: Categorized (e.g., "Respiratory Condition")
2. **Limited Navigation**: Cannot modify data or view logs

### As Receptionist

1. **Add Patients**: Enter new patient information
2. **Edit Patients**: Update basic patient details
3. **Restricted View**: Cannot view diagnoses
4. **No Logs Access**: Cannot view audit trail

---

## 📝 Development Notes

### Adding New Features

1. **New Database Table**: Update `init_db.py` and `database.py`
2. **New User Role**: Update `anonymizer.py` RBAC logic
3. **New Page**: Add to `app.py` with proper role checks

### Code Style

- Use type hints for function parameters
- Document functions with docstrings
- Follow PEP 8 style guide
- Add unit tests for new features

### Security Considerations

- Never log sensitive data in plain text
- Always use parameterized SQL queries
- Encrypt before storing in database
- Check user role before sensitive operations

---

## 📞 Support

For issues or questions:

1. Check this SETUP.md file
2. Review the README.md
3. Check the Assignment4.ipynb notebook
4. Review test files for usage examples

---

## ✅ Verification Checklist

After setup, verify these work:

- [ ] Application starts without errors
- [ ] Can login with all three roles
- [ ] Admin sees decrypted data
- [ ] Doctor sees anonymized data
- [ ] Receptionist can add patients
- [ ] Audit logs are being recorded
- [ ] Data export works
- [ ] All tests pass

---

**Version:** 1.0  
**Last Updated:** November 22, 2025  
**License:** Educational Use
