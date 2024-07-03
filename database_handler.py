# database_handler.py
import os
import sqlite3


DB_FOLDER = './database'
DB_FILE = os.path.join(DB_FOLDER, 'example.db')
# DB_FILE = 'example.db'

def create_table():
    try:
        if not os.path.exists(DB_FOLDER):
            os.makedirs(DB_FOLDER)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_det VARCHAR(220),
            summary VARCHAR(10000),
            path VARCHAR(40),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        '''
        
        c.execute(create_table_sql)
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

def insert_data(contact_det, summary, path):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        insert_sql = '''
        INSERT INTO data (contact_det, summary, path)
        VALUES (?, ?, ?);
        '''

        c.execute(insert_sql, (contact_det, summary, path))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    finally:
        conn.close()
