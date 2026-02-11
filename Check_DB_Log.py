import sqlite3
conn = sqlite3.connect('timesheet.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT 5")
for row in cursor.fetchall():
    print(row)
conn.close()