import sqlite3
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Data to be encrypted
data = b'123'

# Generate encryption key and encrypt data
key = get_random_bytes(32)
cipher = AES.new(key, AES.MODE_EAX)
ciphertext, tag = cipher.encrypt_and_digest(data)
nonce = cipher.nonce
with open("key.txt", "wb") as f:
    f.write(key)
# Connect to the database
conn = sqlite3.connect('network_devices1.2.db')
cur = conn.cursor()

# Update the database with the encrypted password, nonce, and tag
cur.execute("UPDATE devices SET password=?, nonce=?, tag=? WHERE ip_address=?", 
            (sqlite3.Binary(ciphertext), sqlite3.Binary(nonce), sqlite3.Binary(tag), '192.168.137.122'))

# Commit the transaction
conn.commit()

# Retrieve and print all rows from the devices table
cur.execute('SELECT * FROM devices')
rows = cur.fetchall()

for row in rows:
    print(row)

# Close the connection
conn.close()
