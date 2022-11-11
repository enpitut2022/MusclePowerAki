import sqlite3

conn = sqlite3.connect('muscle.db')
# デプロイ先でreset.pyを動かすための3行目に代わるコード
# conn = sqlite3.connect('/home/musclepowerapp/mysite/muscle.db')
cur = conn.cursor()
cur.execute('UPDATE member SET status ="finish"')
conn.commit()
conn.close()