"""
Database Initialization Script
Creates the database schema and seeds initial data
"""
import sqlite3
from auth import hash_password


def init_database():
    """Initialize database with schema and seed data"""
    
    print("🔧 Initializing hospital database...")
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # Create users table
    print("📋 Creating users table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'receptionist'))
        )
    """)
    
    # Create patients table
    print("📋 Creating patients table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create logs table
    print("📋 Creating logs table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Check if users already exist
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        print("👥 Seeding initial users...")
        
        # Seed users with hashed passwords
        users = [
            ('admin', hash_password('admin123'), 'admin'),
            ('dr_bob', hash_password('doc123'), 'doctor'),
            ('alice_recep', hash_password('rec123'), 'receptionist')
        ]
        
        cursor.executemany("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, users)
        
        print("✅ Created 3 users:")
        print("   - admin (password: admin123) - Role: admin")
        print("   - dr_bob (password: doc123) - Role: doctor")
        print("   - alice_recep (password: rec123) - Role: receptionist")
    else:
        print(f"ℹ️  Users table already contains {user_count} users")
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("✅ Database initialization complete!")
    print("📁 Database file: hospital.db")
    print("\n🚀 You can now run: streamlit run app.py")


if __name__ == "__main__":
    init_database()
