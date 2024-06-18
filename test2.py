import sqlite3

# Connect to the database
conn = sqlite3.connect('network_devices.db')
cur = conn.cursor()

# Query to select all users
cur.execute('SELECT * FROM devices')

# Fetch all rows from the executed query
rows = cur.fetchall()

# Iterate through the rows and print each one
for row in rows:
    print(f"ID: {row[0]}, IP Address: {row[1]}, User Login: {row[2]}, Password: {row[3]}, Producent: {row[4]}")

# Close the connection
conn.close()
