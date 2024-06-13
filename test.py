import json

# Wczytanie pliku JSON
with open('data.json', 'r') as json_file:
    data = json.load(json_file)

# Iteracja przez każdy obiekt w liście
for entry in data:
    source_ip = entry.get('source_ip')
    user = entry.get('user')
    password = entry.get('password')
    
    # Przetwarzanie lub wyświetlanie wartości
    print(f"Source IP: {source_ip}, User: {user}, Password: {password}")
