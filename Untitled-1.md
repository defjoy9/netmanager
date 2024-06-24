
Wczytanie danych urządzeń z Bazdy Danych SQLite
    (log - 'Opening Database)
pobiera i pakuje do zmiennych dzisiejszą datę i czas
Autentykuje się z googleDrive API (tylko pierwsze uruchomienie wymaga akcji)
    (log - succesfully authenticated with googledrive api)
w petli do wszyskich urzadzniach MT 
    - polaczenie SSH do mikrotik
        (log - conected to ???)
    - zebrac info o wersji softu i nazwie urzadzenia
        (log - what info did he gather)
    - przygotuje polecenie do eksportu / backup
    - odpalenie polecenie wczesniej przygotownaie po stronie PY
        (log - commands running)
    - wykorzystanie SCP (copy over SSH) do skopiownaia plikow z MT do PC
        (log - did it succesfully scp files)
    - zapis plikow do GDrive
        (log - did it sucessfully save files in googleDrive)
    - Robi cleanup:
        - usuwa pliki z MikroTika
        (log - deleting file)
        - usuwa pliki lokalne
        (log - deleting file)
        - usuwa najstarsze pliki z googledrvie po przekroczeniu X ilości plików w folderze
        (log - deleting file)
    - zamkniecie polaczenia SSH -->
    - zamknięcie połączenia z bazą danych -->
    (log - exiting)



    
Teraz:


log