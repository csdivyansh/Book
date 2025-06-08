import sqlite3

conn = sqlite3.connect('zdb.db')
cursor = conn.cursor()

# Update role of user 'Div' to 'Admin'
cursor.execute("UPDATE clients SET role = 'Admin' WHERE username = 'NS'")

conn.commit()

# Verify the update
cursor.execute("delete FROM clients")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
