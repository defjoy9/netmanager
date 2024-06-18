
- otworzenie pliku data.json
- !!! Wczytanie danych z Bazdy Danych SQLite zamiast .json
w petli do wszyskich urzadzniach MT 
    - polaczenie SSH do mikrotik
    - zebrac info o wersji softu i nazwie urzadzenia
    - przygotuje polecenie do eksportu / backup
    - odpalenie polecenie wczesniej przygotownaie po stronie PY
    - wykorzystanie SCP (copy over SSH) do skopiownaia plikow z MT do PC
    - zapis plikow do GDrive
    - [] !!! usuwanie plików z Mikrotika
        - zobaczenie ile/jakie są pliki
        - sprawdzenie czy data z nazwy pliku przekracza 1 dzien
        jak tak
            usuwamy
        jak nie
            zostawiamy
    - zamkniecie polaczenia SSH -->






----------------------------------------------
był sobie plik JSON z danymi o urzadzeniach

    router_ip = '192.168.137.28'
    router_user = 'python'
    router_password = 'zaq1@WSX'

ładujemy ten plik do zmiennej (json.load(plik))

with open('data.json', 'r') as json_file:
    data = json.load(json_file)

byla juz petla ktora robi backup na wielu urzadzeniach (2-3 urzadzenia do testow)




