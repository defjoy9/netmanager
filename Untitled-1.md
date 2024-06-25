
Wczytanie danych urządzeń z Bazdy Danych SQLite
    (log - 'Opening Database)
pobiera i pakuje do zmiennych dzisiejszą datę i czas
Autentykuje się z googleDrive API (tylko pierwsze uruchomienie wymaga akcji)
    (log - succesfully authenticated with googledrive api)
w petli do wszyskich urzadzniach MT 
    - polaczenie SSH do mikrotik
        (log - conected to ???)
        (log - wrong credentials!!!!)
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


Start
Loading variables
1. Trying to connect to a database
	Fail: 
	- Stop the script
	
2. Trying to connect to a GoogleDrive API
	Fail:
	- Stop the script
3. Connecting to a device via SSH
	Fail:
	- Skip device
	(if still error) - Stop the script
4. Running commands
	Fail:
	- Stop the script
5. Copying files via SCP
	Fail:
	- Stop the script
6. Saving failes to GoogleDrive API
	Fail: Do step 7 -> Stop the script
7. Deleting files from MikroTik
	Fail:
	- Do step 8 and 9 -> Stop the script
8. Delete files locally
	Fail:
	- Do step 9 -> Stop the script
9. Delete old files in GoogleDrive
	Fail: Stop the script
10. Stop the script