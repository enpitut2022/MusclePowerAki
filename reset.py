import sqlite3

conn = sqlite3.connect('muscle.db')
cur = conn.cursor()
cur.execute('UPDATE member SET status ="finish"')
conn.commit()
conn.close()