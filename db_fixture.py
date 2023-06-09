import sqlite3

conn = sqlite3.connect('db')
c = conn.cursor()
conn.commit()
