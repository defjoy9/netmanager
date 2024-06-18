import sqlite3

# Step 1: Connect to the database (creates the database if it doesn't exist)
conn = sqlite3.connect('network_devices.db')

# Step 2: Create a cursor object
cur = conn.cursor()

# Step 3: Create a table
cur.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL,
        user_login TEXT NOT NULL,
        password TEXT NOT NULL,
        producent TEXT NOT NULL
    )
''')

# Step 4: Insert data into the table
cur.execute('''
    INSERT INTO devices (ip_address, user_login, password, producent)
    VALUES ('192.168.137.97', 'python', '123', 'Mikrotik')
''')
cur.execute('''
    INSERT INTO devices (ip_address, user_login, password, producent)
    VALUES ('192.168.1.2', 'py', '123', 'Mikrotik')
''')

# Commit the changes
conn.commit()

# Step 5: Query data from the table
cur.execute('SELECT * FROM devices')
rows = cur.fetchall()

# Print the results
for row in rows:
    print(row)
    

# Close the connection
conn.close()


# 0 - ID
# 1 - IP Address
# 2 - User Login
# 3 - Password
# 4 - Producent