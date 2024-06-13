import json

# Tworzenie słownika z przypisanymi wartościami
device_data = {
    'source_ip': '192.168.137.28',
    'user': 'python',
    'password': 'zaq1@WSX'
}
with open('data.json', 'w') as json_file:
    json.dump(device_data, json_file, indent=4)