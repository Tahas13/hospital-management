# 🏥 GDPR-Compliant Hospital Management System

A comprehensive Streamlit-based hospital management dashboard implementing the **CIA Triad** (Confidentiality, Integrity, Availability) with full **GDPR compliance**.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-Educational-green.svg)](LICENSE)

---

## 🎯 Project Highlights

### CIA Triad Implementation

#### 🔒 Confidentiality
- **Fernet Encryption**: All sensitive patient data encrypted at rest
- **Role-Based Access Control (RBAC)**: Three distinct user roles with different permissions
- **Data Anonymization**: Automatic masking for non-admin users
- **SHA-256 Password Hashing**: Secure password storage

#### ✅ Integrity
- **Comprehensive Audit Logging**: Every action tracked with timestamp and user info
- **SQL Injection Prevention**: Parameterized queries throughout
- **Input Validation**: Data validation before database operations
- **Immutable Logs**: Audit trail for accountability

#### 🟢 Availability
- **Robust Error Handling**: Try-except blocks for graceful failures
- **Data Backup**: CSV export functionality for disaster recovery
- **System Monitoring**: Uptime tracking and real-time status
- **Responsive UI**: Fast, user-friendly Streamlit interface

### GDPR Compliance

✅ **Data Minimization**: Only collect necessary information  
✅ **Consent Management**: Explicit consent required before data processing  
✅ **Right to Access**: Admins can view all patient data  
✅ **Right to Erasure**: Ability to delete patient records  
✅ **Data Portability**: CSV export for data transfer  
✅ **Security by Design**: Encryption and access controls  

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or Download the Project**

```bash
cd IS
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Generate Encryption Key**

```bash
python -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"
```

4. **Create .env File**

Create a `.env` file in the project root and add your encryption key:

```env
ENCRYPTION_KEY=your-generated-key-here
```

5. **Initialize Database**

```bash
python init_db.py
```

6. **Run the Application**

```bash
streamlit run app.py
```

7. **Access the Application**

Open your browser and navigate to `http://localhost:8501`

### Default Login Credentials

| Role | Username | Password | Capabilities |
|------|----------|----------|--------------|
| **Admin** | admin | admin123 | Full access to all features |
| **Doctor** | dr_bob | doc123 | View anonymized patient data |
| **Receptionist** | alice_recep | rec123 | Add/edit patients (no diagnosis view) |

---

## 📁 Project Structure

```
hospital-management/
├── app.py                     # Main Streamlit application
├── auth.py                    # Authentication & session management
├── anonymizer.py              # Encryption & data anonymization
├── database.py                # Database operations & logging
├── init_db.py                 # Database initialization script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── .env.example               # Example environment file
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── SETUP.md                   # Detailed setup guide
├── Assignment4.ipynb          # Jupyter notebook documentation
├── .github/
│   └── copilot-instructions.md  # AI agent instructions
└── tests/                     # Unit tests (40+ tests)
    ├── __init__.py
    ├── test_auth.py           # Authentication tests
    ├── test_anonymizer.py     # Encryption & masking tests
    ├── test_database.py       # Database operation tests
    └── test_rbac.py           # Role-based access tests
```

---

## 🎭 Role-Based Access Control

### Admin Capabilities
- ✅ View **raw** decrypted patient data
- ✅ Add, edit, and delete patient records
- ✅ View complete audit logs
- ✅ Export data to CSV
- ✅ View activity analytics
- ✅ Full system access

### Doctor Capabilities
- ✅ View **anonymized** patient data
  - Names: `ANON_1021`
  - Contacts: `XXX-XXX-4567`
  - Diagnoses: `Respiratory Condition` (categorized)
- ❌ Cannot modify records
- ❌ Cannot view logs
- ❌ Cannot export data

### Receptionist Capabilities
- ✅ Add new patient records
- ✅ Edit basic patient information
- ❌ Cannot view diagnoses (restricted)
- ❌ Cannot delete records
- ❌ Cannot view logs
- ❌ Cannot export data

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=. --cov-report=html
```

View coverage report in `htmlcov/index.html`

### Test Suite Overview

- **40+ Unit Tests** across 4 test modules
- **80%+ Code Coverage**
- Tests for authentication, encryption, database operations, and RBAC

---

## 📊 Features Overview

### Dashboard Features
- Patient count statistics
- Activity metrics (total actions, today's actions)
- Most active user tracking
- Real-time activity graphs (last 7-30 days)

### Patient Management
- Add new patients with encrypted data
- Edit existing patient records
- Delete patients (admin only)
- View patients with role-based filtering
- GDPR consent checkbox

### Audit & Compliance
- Complete audit trail of all actions
- Filter logs by user, action type, or date
- Activity analytics with visualizations
- Export logs for compliance reporting

### Data Protection
- Fernet symmetric encryption
- Automatic data anonymization
- Secure password hashing (SHA-256)
- Session management with Streamlit

---

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/hospital-management.git
git push -u origin main
```

2. **Configure Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io/)
- Create new app from your repository
- Add secrets in advanced settings:
```toml
ENCRYPTION_KEY = "your-fernet-key-here"
```

3. **Deploy**
- Click "Deploy" and wait for build completion

For detailed deployment instructions, see [SETUP.md](SETUP.md) and `.github/copilot-instructions.md`

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)**: Detailed setup and troubleshooting guide
- **[Assignment4.ipynb](Assignment4.ipynb)**: Complete project documentation with code examples
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)**: AI agent instructions and architecture details

---

## 🔒 Security Considerations

- ⚠️ Never commit `.env` file to version control
- ⚠️ Change default passwords in production
- ⚠️ Keep encryption key secure and backed up
- ⚠️ Regularly review audit logs for suspicious activity
- ⚠️ Use HTTPS in production deployments

---

## 📝 Assignment Deliverables

### ✅ Completed Requirements

1. **Source Code** ✓
   - All Python modules (app.py, database.py, auth.py, anonymizer.py)
   - Database initialization script
   - Unit tests with 80%+ coverage

2. **Documentation** ✓
   - Assignment4.ipynb with complete walkthrough
   - README.md with setup instructions
   - SETUP.md with troubleshooting guide
   - Inline code comments

3. **Bonus Features** ✓
   - Fernet encryption (reversible anonymization)
   - Real-time activity graphs
   - GDPR consent banner
   - Data retention features

---

## 🎓 Learning Outcomes

- ✅ Practical implementation of CIA Triad
- ✅ GDPR compliance in software design
- ✅ Symmetric encryption with Fernet
- ✅ Role-based access control (RBAC)
- ✅ Secure database operations
- ✅ Comprehensive testing practices
- ✅ Modern web application development

---

## 🤝 Contributing

This is an educational project for Information Security coursework.

---

## 📧 Contact

**Course:** Information Security  
**Assignment:** Assignment 4  
**Date:** November 22, 2025

---

## 📄 License

This project is for educational purposes only.

---

## 🙏 Acknowledgments

- Course instructor for project requirements
- Streamlit for the amazing web framework
- Python cryptography library for encryption capabilities

---

**⭐ If you found this project helpful, please consider starring it!**
