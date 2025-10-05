#!/usr/bin/env python3
"""
GovAI Database Initialization Script
Creates SQLite database and loads data from CSV files
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

def init_database():
    """Initialize SQLite database with government data"""
    print("🗄️ Initializing GovAI Database...")
    
    # Database path
    db_path = "data/govai.db"
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnic TEXT UNIQUE,
            name TEXT,
            language TEXT DEFAULT 'english',
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create bills table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT,
            cnic TEXT,
            amount REAL,
            date TEXT,
            consumption REAL,
            bill_type TEXT DEFAULT 'electricity',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cnic) REFERENCES users (cnic)
        )
        """)
        
        # Create contracts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_number TEXT UNIQUE,
            description TEXT,
            amount REAL,
            supplier TEXT,
            country TEXT,
            date_signed TEXT,
            risk_score REAL DEFAULT 0.0,
            risk_level TEXT DEFAULT 'LOW',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create chat_logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message TEXT,
            response TEXT,
            language TEXT,
            intent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        print("✅ Database tables created successfully")
        
        # Load users data
        try:
            users_df = pd.read_csv("data/users.csv")
            print(f"📊 Loading {len(users_df)} users...")
            
            # Sample CNIC generation for users without CNIC
            for idx, row in users_df.iterrows():
                cnic = f"42101-{str(idx+1000000)[:7]}-{(idx % 10)+1}"
                name = row.get('name', f'User_{idx+1}')
                language = 'urdu' if idx % 2 == 0 else 'english'
                
                cursor.execute("""
                INSERT OR IGNORE INTO users (cnic, name, language)
                VALUES (?, ?, ?)
                """, (cnic, name, language))
            
            print("✅ Users data loaded")
        except FileNotFoundError:
            print("⚠️ users.csv not found, creating sample data...")
            # Create sample users
            sample_users = [
                ("42101-1234567-1", "احمد علی", "urdu"),
                ("42101-2345678-2", "فاطمہ خان", "urdu"),
                ("42101-3456789-3", "John Smith", "english"),
                ("42101-4567890-4", "Maria Garcia", "english"),
                ("42101-5678901-5", "محمد حسن", "urdu")
            ]
            
            cursor.executemany("""
            INSERT OR IGNORE INTO users (cnic, name, language)
            VALUES (?, ?, ?)
            """, sample_users)
            
            print("✅ Sample users created")
        
        # Load household power consumption data as bills
        try:
            power_df = pd.read_csv("data/Household_power_consumption.csv")
            print(f"📊 Loading {len(power_df)} power consumption records...")
            
            # Sample bill data from power consumption
            for idx in range(min(1000, len(power_df))):
                row = power_df.iloc[idx]
                
                # Generate account and associate with random user
                account = f"PWR-{str(idx+100000)[:6]}"
                cnic = f"42101-{str((idx % 5)+1234567)}-{(idx % 9)+1}"
                
                # Calculate amount based on consumption
                consumption = float(row.get('Global_active_power', 0) or 0)
                amount = consumption * 15.5  # Sample rate per kWh
                
                cursor.execute("""
                INSERT OR IGNORE INTO bills (account, cnic, amount, consumption, bill_type)
                VALUES (?, ?, ?, ?, ?)
                """, (account, cnic, round(amount, 2), round(consumption, 3), "electricity"))
            
            print("✅ Bills data loaded")
        except FileNotFoundError:
            print("⚠️ Household_power_consumption.csv not found, creating sample bills...")
            # Create sample bills
            sample_bills = [
                ("PWR-100001", "42101-1234567-1", 2500.50, 125.2, "electricity"),
                ("GAS-100002", "42101-2345678-2", 1800.75, 89.3, "gas"),
                ("WTR-100003", "42101-3456789-3", 950.25, 45.1, "water"),
                ("PWR-100004", "42101-4567890-4", 3200.80, 160.4, "electricity"),
                ("GAS-100005", "42101-5678901-5", 2100.60, 105.8, "gas")
            ]
            
            cursor.executemany("""
            INSERT OR IGNORE INTO bills (account, cnic, amount, consumption, bill_type)
            VALUES (?, ?, ?, ?, ?)
            """, sample_bills)
            
            print("✅ Sample bills created")
        
        # Load contract data
        try:
            contracts_df = pd.read_csv("data/Major_Contract_Awards.csv")
            print(f"📊 Loading {len(contracts_df)} contracts...")
            
            # Load first 1000 contracts for performance
            for idx in range(min(1000, len(contracts_df))):
                row = contracts_df.iloc[idx]
                
                contract_number = row.get('WB Contract Number', f'CONTRACT-{idx+1}')
                description = str(row.get('Contract Description', 'Government Contract'))[:500]
                
                # Clean amount field - remove currency symbols and commas
                amount_str = str(row.get('Total Contract Amount (USD)', '0'))
                amount_str = amount_str.replace('$', '').replace(',', '').strip()
                try:
                    amount = float(amount_str) if amount_str and amount_str != 'nan' else 0.0
                except:
                    amount = 0.0
                
                supplier = str(row.get('Supplier', 'Unknown Supplier'))[:200]
                country = str(row.get('Supplier Country', 'Unknown'))[:100]
                date_signed = str(row.get('Contract Signing Date', '2023-01-01'))[:10]
                
                # Simple risk calculation
                risk_score = min(1.0, amount / 10000000)  # Higher amounts = higher risk
                if risk_score > 0.8:
                    risk_level = 'CRITICAL'
                elif risk_score > 0.6:
                    risk_level = 'HIGH'
                elif risk_score > 0.3:
                    risk_level = 'MEDIUM'
                else:
                    risk_level = 'LOW'
                
                cursor.execute("""
                INSERT OR IGNORE INTO contracts 
                (contract_number, description, amount, supplier, country, date_signed, risk_score, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (contract_number, description, amount, supplier, country, date_signed, risk_score, risk_level))
            
            print("✅ Contracts data loaded")
        except FileNotFoundError:
            print("⚠️ Major_Contract_Awards.csv not found, creating sample contracts...")
            # Create sample contracts
            sample_contracts = [
                ("CONTRACT-001", "Road Construction Project", 5000000.00, "ABC Construction", "Pakistan", "2023-01-15", 0.5, "MEDIUM"),
                ("CONTRACT-002", "IT Infrastructure Upgrade", 2500000.00, "Tech Solutions Inc", "USA", "2023-02-20", 0.25, "LOW"),
                ("CONTRACT-003", "Hospital Equipment Purchase", 8000000.00, "MedEquip Ltd", "Germany", "2023-03-10", 0.8, "HIGH"),
                ("CONTRACT-004", "Water Treatment Plant", 12000000.00, "AquaTech Systems", "Netherlands", "2023-04-05", 1.0, "CRITICAL"),
                ("CONTRACT-005", "School Building Construction", 3500000.00, "BuildCorp", "Pakistan", "2023-05-12", 0.35, "MEDIUM")
            ]
            
            cursor.executemany("""
            INSERT OR IGNORE INTO contracts 
            (contract_number, description, amount, supplier, country, date_signed, risk_score, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_contracts)
            
            print("✅ Sample contracts created")
        
        # Commit changes
        conn.commit()
        
        # Display statistics
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bills")
        bill_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contracts")
        contract_count = cursor.fetchone()[0]
        
        print("\n📈 Database Statistics:")
        print(f"  👥 Users: {user_count:,}")
        print(f"  🧾 Bills: {bill_count:,}")
        print(f"  📋 Contracts: {contract_count:,}")
        print(f"\n💾 Database created: {db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🎉 Database initialization completed successfully!")
    else:
        print("\n❌ Database initialization failed!")