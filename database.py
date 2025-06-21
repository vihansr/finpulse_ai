import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")

def create_connection():
    return psycopg2.connect(DB_HOST)

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def add_subscriber(email):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subscribers (email) VALUES (%s)", (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.errors.UniqueViolation:
        return False
    except Exception as e:
        print("Database error:", e)
        return False
