"""
GDPR-Compliant Hospital Management System
Main Streamlit Application

Implements CIA Triad:
- Confidentiality: Fernet encryption, role-based access control
- Integrity: Comprehensive audit logging, validation
- Availability: Error handling, data backup, system monitoring
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
import sqlite3

# Auto-initialize database if it doesn't exist
def ensure_database_initialized():
    """Ensure database is initialized with schema and default users"""
    if not os.path.exists('hospital.db'):
        from init_db import init_database
        init_database()

# Initialize database before importing modules
ensure_database_initialized()

# Import custom modules
from auth import (
    initialize_session_state, is_authenticated, get_current_user,
    hash_password, login_user, logout_user
)
from database import (
    authenticate_user, add_patient, get_all_patients, get_patient_by_id,
    update_patient, delete_patient, get_patient_count, log_action,
    get_all_logs, get_logs_by_action, get_activity_stats, get_daily_activity
)
from anonymizer import (
    encrypt_data, decrypt_data, prepare_patient_data_for_role
)

# Page configuration
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()

# Store app start time for uptime calculation
if 'app_start_time' not in st.session_state:
    st.session_state.app_start_time = time.time()


# ==================== UTILITY FUNCTIONS ====================

def show_login_page():
    """Display login page"""
    st.title("🏥 Hospital Management System")
    st.subheader("🔐 Secure Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        with st.form("login_form"):
            st.write("### Please enter your credentials")
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    # Hash password and authenticate
                    password_hash = hash_password(password)
                    user_data = authenticate_user(username, password_hash)
                    
                    if user_data:
                        user_id, username, role = user_data
                        login_user(user_id, username, role)
                        log_action(user_id, role, "LOGIN", f"User {username} logged in")
                        st.success(f"✅ Welcome, {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
        
        st.markdown("---")
        st.info("""
        **Demo Credentials:**
        - Admin: `admin` / `admin123`
        - Doctor: `dr_bob` / `doc123`
        - Receptionist: `alice_recep` / `rec123`
        """)


def show_dashboard():
    """Display main dashboard based on user role"""
    user_id, username, role = get_current_user()
    
    # Header
    st.title("🏥 Hospital Management Dashboard")
    st.markdown(f"**User:** {username} | **Role:** {role.upper()}")
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    
    # Role-based menu options
    menu_options = []
    
    if role == 'admin':
        menu_options = [
            "📊 Dashboard",
            "👥 View Patients",
            "➕ Add Patient",
            "✏️ Edit Patient",
            "🗑️ Delete Patient",
            "📜 Audit Logs",
            "📈 Activity Analytics",
            "💾 Data Export"
        ]
    elif role == 'doctor':
        menu_options = [
            "📊 Dashboard",
            "👥 View Patients (Anonymized)"
        ]
    elif role == 'receptionist':
        menu_options = [
            "📊 Dashboard",
            "➕ Add Patient",
            "✏️ Edit Patient"
        ]
    
    choice = st.sidebar.radio("Select Option", menu_options)
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        log_action(user_id, role, "LOGOUT", f"User {username} logged out")
        logout_user()
        st.rerun()
    
    # Display selected page
    if choice == "📊 Dashboard":
        show_dashboard_home(role)
    elif choice == "👥 View Patients" or choice == "👥 View Patients (Anonymized)":
        show_patients_page(role)
    elif choice == "➕ Add Patient":
        show_add_patient_page(user_id, role)
    elif choice == "✏️ Edit Patient":
        show_edit_patient_page(user_id, role)
    elif choice == "🗑️ Delete Patient":
        show_delete_patient_page(user_id, role)
    elif choice == "📜 Audit Logs":
        show_audit_logs_page(role)
    elif choice == "📈 Activity Analytics":
        show_analytics_page(role)
    elif choice == "💾 Data Export":
        show_export_page(user_id, role)
    
    # Footer with system info
    show_footer()


def show_dashboard_home(role: str):
    """Display dashboard home with statistics"""
    st.header("📊 Dashboard Overview")
    
    # Get statistics
    patient_count = get_patient_count()
    activity_stats = get_activity_stats()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Patients", patient_count)
    
    with col2:
        st.metric("📝 Total Actions", activity_stats['total_logs'])
    
    with col3:
        st.metric("📅 Actions Today", activity_stats['logs_today'])
    
    with col4:
        st.metric("🏆 Most Active User", activity_stats['most_active_user'])
    
    st.markdown("---")
    
    # Role-specific information
    if role == 'admin':
        st.info("🔑 **Admin Access**: You have full access to all features including raw data, audit logs, and system management.")
    elif role == 'doctor':
        st.info("👨‍⚕️ **Doctor Access**: You can view anonymized patient data to protect privacy.")
    elif role == 'receptionist':
        st.info("📝 **Receptionist Access**: You can add and edit patient records but cannot view sensitive medical information.")
    
    # Recent activity
    if role == 'admin':
        st.subheader("📊 Recent Activity (Last 7 Days)")
        daily_activity = get_daily_activity(7)
        
        if daily_activity:
            df = pd.DataFrame(daily_activity)
            st.line_chart(df.set_index('date')['count'])
        else:
            st.info("No activity data available yet")


def show_patients_page(role: str):
    """Display patients list with role-based data masking"""
    st.header("👥 Patient Records")
    
    user_id, username, _ = get_current_user()
    
    # Admin toggle for anonymization
    view_anonymized = False
    if role == 'admin':
        col1, col2 = st.columns([3, 1])
        with col2:
            view_anonymized = st.toggle("🔒 View Anonymized", value=False, help="Toggle to view data as other roles see it")
        
        if view_anonymized:
            st.info("🔍 **Anonymized View Mode**: You are viewing data as doctors/receptionists would see it.")
    
    # Get all patients (encrypted data)
    patients = get_all_patients()
    
    if not patients:
        st.info("No patient records found")
        return
    
    # Prepare data based on role (or force anonymized for admin if toggled)
    display_data = []
    for patient in patients:
        if role == 'admin' and view_anonymized:
            # Show admin what doctors see (anonymized)
            processed_patient = prepare_patient_data_for_role(patient, 'doctor')
        else:
            # Normal role-based view
            processed_patient = prepare_patient_data_for_role(patient, role)
        display_data.append(processed_patient)
    
    # Display as dataframe
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Log the view action
    view_mode = "anonymized" if (role == 'admin' and view_anonymized) else role
    log_action(user_id, role, "VIEW_PATIENTS", f"Viewed {len(patients)} patient records ({view_mode} mode)")
    
    # Show data protection notice
    if role == 'admin' and not view_anonymized:
        st.success("✅ **Admin View**: You are viewing decrypted raw patient data.")
    elif role == 'doctor' or (role == 'admin' and view_anonymized):
        st.warning("🔒 **Privacy Notice**: Patient data is anonymized to protect privacy. Only authorized administrators can view full details.")
    elif role == 'receptionist':
        st.warning("🔒 **Privacy Notice**: Medical diagnoses are restricted. You can only view basic patient information.")


def show_add_patient_page(user_id: int, role: str):
    """Display form to add new patient"""
    st.header("➕ Add New Patient")
    
    # GDPR Consent Banner
    st.info("📋 **GDPR Compliance**: By submitting this form, you confirm that the patient has consented to their data being processed and stored securely.")
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Patient Name *", placeholder="John Doe")
            contact = st.text_input("Contact Number *", placeholder="123-456-7890")
        
        with col2:
            diagnosis = st.text_area("Diagnosis *", placeholder="Enter medical diagnosis")
            consent = st.checkbox("Patient has provided consent for data processing (GDPR)", value=False)
        
        submitted = st.form_submit_button("➕ Add Patient", use_container_width=True)
        
        if submitted:
            # Validation
            if not all([name, contact, diagnosis]):
                st.error("❌ Please fill in all required fields")
            elif not consent:
                st.error("❌ Patient consent is required for GDPR compliance")
            else:
                try:
                    # Encrypt sensitive data
                    name_encrypted = encrypt_data(name)
                    contact_encrypted = encrypt_data(contact)
                    diagnosis_encrypted = encrypt_data(diagnosis)
                    
                    # Add to database
                    success = add_patient(
                        name_encrypted, 
                        contact_encrypted, 
                        diagnosis_encrypted,
                        user_id, 
                        role
                    )
                    
                    if success:
                        st.success("✅ Patient added successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to add patient. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


def show_edit_patient_page(user_id: int, role: str):
    """Display form to edit existing patient"""
    st.header("✏️ Edit Patient Record")
    
    # Get all patients
    patients = get_all_patients()
    
    if not patients:
        st.info("No patient records found")
        return
    
    # Select patient to edit
    patient_options = {f"ID {p['patient_id']} - Added {p['date_added']}": p['patient_id'] for p in patients}
    selected = st.selectbox("Select Patient to Edit", list(patient_options.keys()))
    
    if selected:
        patient_id = patient_options[selected]
        patient = get_patient_by_id(patient_id)
        
        if patient:
            st.markdown("---")
            
            # Decrypt current data (admin sees all, receptionist sees masked)
            if role == 'admin':
                current_name = decrypt_data(patient['name'])
                current_contact = decrypt_data(patient['contact'])
                current_diagnosis = decrypt_data(patient['diagnosis'])
            else:
                # Receptionist sees masked data but can enter new values
                processed = prepare_patient_data_for_role(patient, role)
                current_name = ""  # Empty so they can enter new data
                current_contact = ""  # Empty so they can enter new data
                current_diagnosis = "[Restricted - Cannot view or edit diagnosis]"
                
                # Show current masked values for reference
                st.info(f"📋 **Current Record:** Patient: {processed['name']} | Contact: {processed['contact']}")
            
            with st.form("edit_patient_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if role == 'admin':
                        name = st.text_input("Patient Name *", value=current_name)
                        contact = st.text_input("Contact Number *", value=current_contact)
                    else:
                        name = st.text_input("Patient Name * (Enter new name)", value=current_name, 
                                            placeholder="Enter updated patient name")
                        contact = st.text_input("Contact Number * (Enter new contact)", value=current_contact,
                                               placeholder="Enter updated contact number")
                
                with col2:
                    if role == 'admin':
                        diagnosis = st.text_area("Diagnosis *", value=current_diagnosis)
                    else:
                        st.text_area("Diagnosis", value=current_diagnosis, disabled=True)
                        diagnosis = decrypt_data(patient['diagnosis'])  # Keep original
                
                submitted = st.form_submit_button("💾 Update Patient", use_container_width=True)
                
                if submitted:
                    if not all([name, contact, diagnosis]):
                        st.error("❌ Please fill in all required fields")
                    else:
                        try:
                            # Encrypt data
                            name_encrypted = encrypt_data(name)
                            contact_encrypted = encrypt_data(contact)
                            diagnosis_encrypted = encrypt_data(diagnosis)
                            
                            # Update database
                            success = update_patient(
                                patient_id,
                                name_encrypted,
                                contact_encrypted,
                                diagnosis_encrypted,
                                user_id,
                                role
                            )
                            
                            if success:
                                st.success("✅ Patient updated successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Failed to update patient")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")


def show_delete_patient_page(user_id: int, role: str):
    """Display interface to delete patient (admin only)"""
    st.header("🗑️ Delete Patient Record")
    st.warning("⚠️ **Warning**: This action cannot be undone. Patient data will be permanently deleted.")
    
    # Get all patients
    patients = get_all_patients()
    
    if not patients:
        st.info("No patient records found")
        return
    
    # Prepare display data
    display_data = []
    for patient in patients:
        processed = prepare_patient_data_for_role(patient, role)
        display_data.append(processed)
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Select patient to delete
    patient_ids = [p['patient_id'] for p in patients]
    selected_id = st.selectbox("Select Patient ID to Delete", patient_ids)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🗑️ Delete Patient", type="primary", use_container_width=True):
            success = delete_patient(selected_id, user_id, role)
            if success:
                st.success("✅ Patient deleted successfully")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to delete patient")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.info("Deletion cancelled")


def show_audit_logs_page(role: str):
    """Display audit logs (admin only)"""
    st.header("📜 Integrity Audit Logs")
    
    user_id, username, _ = get_current_user()
    
    # Filter options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        log_limit = st.slider("Number of logs to display", 10, 500, 100)
    
    with col2:
        action_filter = st.selectbox("Filter by Action", 
                                     ["All", "LOGIN", "LOGOUT", "ADD_PATIENT", "UPDATE_PATIENT", 
                                      "DELETE_PATIENT", "VIEW_PATIENTS", "EXPORT_DATA"])
    
    # Get logs
    if action_filter == "All":
        logs = get_all_logs(log_limit)
    else:
        logs = get_logs_by_action(action_filter, log_limit)
    
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Log this view
        log_action(user_id, role, "VIEW_LOGS", f"Viewed {len(logs)} audit logs")
    else:
        st.info("No logs found")


def show_analytics_page(role: str):
    """Display activity analytics (admin only)"""
    st.header("📈 Activity Analytics")
    
    # Get statistics
    stats = get_activity_stats()
    daily_activity = get_daily_activity(30)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Actions", stats['total_logs'])
    
    with col2:
        st.metric("Actions Today", stats['logs_today'])
    
    with col3:
        st.metric("Most Active User", stats['most_active_user'])
    
    st.markdown("---")
    
    # Activity chart
    if daily_activity:
        st.subheader("📊 Daily Activity (Last 30 Days)")
        df = pd.DataFrame(daily_activity)
        st.line_chart(df.set_index('date')['count'])
        
        st.subheader("📊 Activity Distribution")
        st.bar_chart(df.set_index('date')['count'])
    else:
        st.info("No activity data available")


def show_export_page(user_id: int, role: str):
    """Display data export options (admin only)"""
    st.header("💾 Data Export & Backup")
    
    st.info("📦 Export patient records and audit logs for backup or compliance purposes.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Export Patient Data")
        
        # Get patients
        patients = get_all_patients()
        
        if patients:
            display_data = []
            for patient in patients:
                processed = prepare_patient_data_for_role(patient, role)
                # Format date_added to be more readable in CSV
                if 'date_added' in processed and processed['date_added']:
                    try:
                        # Parse and reformat date for better CSV display
                        processed['date_added'] = pd.to_datetime(processed['date_added']).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass  # Keep original if parsing fails
                display_data.append(processed)
            
            df_patients = pd.DataFrame(display_data)
            
            # Convert to CSV
            csv_patients = df_patients.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Patients CSV",
                data=csv_patients,
                file_name=f"patients_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.success(f"✅ {len(patients)} patient records ready for export")
        else:
            st.info("No patient records to export")
    
    with col2:
        st.subheader("📜 Export Audit Logs")
        
        # Get logs
        logs = get_all_logs(1000)
        
        if logs:
            df_logs = pd.DataFrame(logs)
            
            # Format timestamp column for better CSV display
            if 'timestamp' in df_logs.columns:
                df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert to CSV
            csv_logs = df_logs.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Logs CSV",
                data=csv_logs,
                file_name=f"audit_logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.success(f"✅ {len(logs)} log entries ready for export")
            
            # Log the export action
            log_action(user_id, role, "EXPORT_DATA", "Exported audit logs")
        else:
            st.info("No logs to export")


def show_footer():
    """Display footer with system information"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        uptime_seconds = int(time.time() - st.session_state.app_start_time)
        uptime_minutes = uptime_seconds // 60
        st.caption(f"⏱️ System Uptime: {uptime_minutes} minutes")
    
    with col2:
        st.caption(f"🕐 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col3:
        st.caption("🔒 GDPR Compliant | CIA Triad Implemented")


# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    try:
        if not is_authenticated():
            show_login_page()
        else:
            show_dashboard()
    
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        st.error("Please try refreshing the page or contact support.")


if __name__ == "__main__":
    main()
