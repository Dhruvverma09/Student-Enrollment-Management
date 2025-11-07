from dotenv import load_dotenv
import os
import mysql.connector

# Load environment variables
load_dotenv()

# MySQL config
db_config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME"),
    'port': os.getenv("DB_PORT")
}

try:
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("✅ Connection successful!")
except mysql.connector.Error as e:
    print(f"❌ Connection failed: {e}")
