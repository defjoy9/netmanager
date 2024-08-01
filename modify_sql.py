# 1. id
# 2. ip_address
# 3. user_login
# 4. password
# 5. producent


# network_devices.db

# -------------------------------------------

import sqlite3

conn = sqlite3.connect('network_devices.db')


cur = conn.cursor()
cur.execute('''
    UPDATE devices
    SET enable = "1"
    WHERE ip_address = "192.168.137.182"
''')
# cur.execute('''
#     UPDATE devices
#     SET ip_address="192.168.137.92"
#     WHERE ip_address="192.168.137.168"
# ''')
#cur.execute('''
#     UPDATE devices
#     SET user_login="python"
#     WHERE user_login="py"
# ''')
# cur.execute('''
#     UPDATE devices
#     SET user_login="python"
#     WHERE ip_address="192.168.137.40"
# ''')

conn.commit()

cur.execute('SELECT * FROM devices')
rows = cur.fetchall()


for row in rows:
    print(row)
    


conn.close()
