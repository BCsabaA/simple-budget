# create_db.py

import sqlite3

conn = sqlite3.connect('expense.db')
conn.execute('''
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        description TEXT NOT NULL,
        type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
        date TEXT NOT NULL
    )
''')
conn.close()
print("Adatbázis létrehozva.")
