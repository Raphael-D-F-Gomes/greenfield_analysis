import sqlite3
import os


if os.path.exists('greenfield_analysis_data.db'):
    os.remove('greenfield_analysis_data.db')

conn = sqlite3.connect('greenfield_analysis_data.db')

cursor = conn.cursor()

cursor.execute("""
                    CREATE TABLE CUSTOMERS(
                    ID_CUSTUMERS INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    NAME TEXT NOT NULL,
                    FIXED_DEMAND REAL NOT NULL,
                    LATITUDE REAL NOT NULL,
                    LONGITUDE REAL NOT NULL
                    );
                """)

cursor.execute("""
                    CREATE TABLE SUPPLIERS(
                    ID_SUPPLIERS INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    NAME TEXT NOT NULL,
                    MAXIMUM_SUPPLY REAL NOT NULL,
                    LATITUDE REAL NOT NULL,
                    LONGITUDE REAL NOT NULL
                    );
                """)

print('Tabela criada com sucesso!')

conn.close()
