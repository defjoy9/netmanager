# 2024-06-19 14:13:28 by RouterOS 7.15
# software id = Q3HR-X5V6
#
# model = RB760iGS
# serial number = A36A0B4C8A9A
/port
set 0 name=serial0
/ip firewall connection tracking
set udp-timeout=10s
/ip address
add address=192.168.1.7/24 interface=ether1 network=192.168.1.0
/ip dhcp-client
add interface=ether1
add interface=ether4
/ip hotspot profile
set [ find default=yes ] html-directory=hotspot
/system clock
set time-zone-name=Europe/Warsaw
/system identity
set name=test-cyfrowe
/system note
set show-at-login=no
/system routerboard settings
set auto-upgrade=yes
/system script
add dont-require-permissions=no name=exportbackup owner=admin policy=\
    ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source=":\
    global replaceStringFunc\r\
    \n\r\
    \n:local fileNameExport \"\"\r\
    \n:local fileNameBackup \"\"\r\
    \n\r\
    \n:local ftpHost \"192.168.137.200\"\r\
    \n:local ftpUser \"python\"\r\
    \n:local ftpPass \"zaq1@WSX\"\r\
    \n:local ftpDstPath \"\"\r\
    \n\r\
    \n\r\
    \n:local identity [/system identity get name]\r\
    \n:local date [system/clock/get date];\r\
    \n:local time [system/clock/get time];\r\
    \n:local version [system/package/update/get installed-version]\r\
    \n\r\
    \n:set date [\$replaceStringFunc text=\$date];\r\
    \n:set time [\$replaceStringFunc text=\$time];\r\
    \n\r\
    \n\r\
    \n\r\
    \n:set fileNameExport (\"configExport-\".\$identity.\"-\".\$version.\"-\".\
    \$date.\"-\".\$time)\r\
    \n:set fileNameBackup (\"configBackup-\".\$identity.\"-\".\$version.\"-\".\
    \$date.\"-\".\$time)\r\
    \n\r\
    \n\r\
    \n/export file=\$fileNameExport;\r\
    \n/system backup save name=\$fileNameBackup\r\
    \n\r\
    \n/tool fetch address=\$ftpHost src-path=(\$fileNameExport.\".rsc\") dst-p\
    ath=(\$ftpDstPath . \"Uploaded-export-\".\$fileNameExport.\".rsc\") \\\r\
    \n upload=yes mode=ftp user=\$ftpUser  password=\$ftpPass\r\
    \n\r\
    \n/tool fetch address=\$ftpHost src-path=(\$fileNameBackup.\".backup\") ds\
    t-path=(\$ftpDstPath . \"Uploaded-backup-\".\$fileNameBackup.\".backup\") \
    \\\r\
    \n upload=yes mode=ftp user=\$ftpUser  password=\$ftpPass\r\
    \n\r\
    \n:put \"Waiting...\"\r\
    \n:delay 5s;\r\
    \n\r\
    \n:local tmpEx (\$fileNameExport.\".rsc\")\r\
    \n:local tmpBc (\$fileNameBackup.\".backup\")\r\
    \n\r\
    \n\r\
    \n# file/remove \$tmpEx\r\
    \n# file/remove \$tmpBc\r\
    \n# :put \"Deleted\""
add dont-require-permissions=no name=test owner=admin policy=\
    ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source=":\
    global strReplaceFunc do={\r\
    \n\t:local stringBefore \$text\r\
    \n\t:local stringAfter\r\
    \n\t:local zleznaki {\" \"=\"-\";\"/\"=\"-\";\":\"=\"-\";}\r\
    \n\r\
    \n\t:for i from=0 to=([:len \$stringBefore] - 1) do={ \r\
    \n\t\t:local char [:pick \$stringBefore \$i]\r\
    \n\r\
    \n\t\t:foreach zly,nowy in=\$zleznaki do={\r\
    \n\t\t\t:if (\$char=\$zly) do={\r\
    \n\t\t\t\t:set \$char \$nowy;\r\
    \n\t\t\t}\r\
    \n\t\t}\r\
    \n\t\t:set stringAfter (\$stringAfter . \$char)\r\
    \n\t}\r\
    \n\t:return \$stringAfter\r\
    \n}\r\
    \n\r\
    \n# :put [\$strReplaceFunc text=\"jul/16/2018 11:33:22\"];\r\
    \n\r\
    \n# \r\
    \n\r\
    \n#Zmienna na przechowanie nawzwy pliku\r\
    \n:local fileNameExport \"\";\r\
    \n:local fileNameBackup \"\";\r\
    \n\r\
    \n#dane do polaczenia FTP\r\
    \n:local ftpHost \"192.168.137.28\"\r\
    \n:local ftpUser \"python\"\r\
    \n:local ftpPass \"zaq1@WSX\"\r\
    \n\r\
    \n:local ftp2Host \"\"\r\
    \n:local ftp2User \"\"\r\
    \n:local ftp2Pass \"\"\r\
    \n\r\
    \n#zapisanie do zmienneje identity routera\r\
    \n:local identity [/system identity get name];\r\
    \n#zapisanie daty do zmiennej\r\
    \n:local date [/system clock get date];\r\
    \n#zapisanie czasu do zmiennej\r\
    \n:local time [/system clock get time];\r\
    \n#zapisanie wersji routerOS\r\
    \n:local version [/system package update get installed-version];\r\
    \n\r\
    \n:local stringBefore \$date\r\
    \n:local stringAfter\r\
    \n\r\
    \n#czysczenie daty, wczesniej zapisanej jako stringBefore\r\
    \n:for i from=0 to=([:len \$stringBefore] - 1) do={ \r\
    \n  :local char [:pick \$stringBefore \$i]\r\
    \n  :if (\$char = \"/\") do={\r\
    \n    :set \$char \"-\"\r\
    \n  }\r\
    \n  :if (\$char = \":\") do={\r\
    \n    :set \$char \"-\"\r\
    \n  }\r\
    \n\r\
    \n  :set stringAfter (\$stringAfter . \$char)\r\
    \n    \r\
    \n}\r\
    \n\r\
    \n# to wyszlo z oczyszczanai daty\r\
    \n:put \$stringAfter;\r\
    \n\r\
    \n#data po usunieciu niechcianych znakow\r\
    \n:set date \$stringAfter;\r\
    \n\r\
    \n#ustalenie nazwy pliku skladajacego sie z identity, daty i czasu\r\
    \n:set fileNameExport (\"configExport-\".\$identity.\"-\".\$version.\"-\".\
    \$date.\"-\".\$time);\r\
    \n:set fileNameBackup (\"configExport-\".\$identity.\"-\".\$version.\"-\".\
    \$date.\"-\".\$time);\r\
    \n\r\
    \n#eksport konfiguracji do pliku\r\
    \n/export file=\$fileNameExport;\r\
    \n/system backup save name=\$filenameBackup\r\
    \n\r\
    \n#wyslanie pliku do zdalnego serwera FTP\r\
    \n/tool fetch address=\$ftpHost src-path=(\$fileNameExport.\".rsc\") dst-p\
    ath=(\"C:\\Users\\User\\Desktop\\Uploaded-export-\".\$fileNameExport.\".rs\
    c\") upload=yes mode=ftp user=\$ftpUser  password=\$ftpPass\r\
    \n/tool fetch address=\$ftpHost src-path=(\$fileNameBackup.\".rsc\") dst-p\
    ath=(\"C:\\Users\\User\\Desktop\\Uploaded-export-\".\$fileNameBackup.\".rs\
    c\") upload=yes mode=ftp user=\$ftpUser  password=\$ftpPass\r\
    \n\r\
    \n#wysylania na zapasowy serwer FTP, jesli zostal zdefiniowany\r\
    \n:if ([:len \$ftp2Host] != 0) do={\r\
    \n  /tool fetch address=\$ftp2Host src-path=(\$fileNameExport.\".rsc\") ds\
    t-path=(\"Uploaded-export-\".\$fileNameExport.\".rsc\") upload=yes mode=ft\
    p user=\$ftp2User  password=\$ftp2Pass\r\
    \n  /tool fetch address=\$ftp2Host src-path=(\$fileNameBackup.\".rsc\") ds\
    t-path=(\"Uploaded-export-\".\$fileNameBackup.\".rsc\") upload=yes mode=ft\
    p user=\$ftp2User  password=\$ftp2Pass\r\
    \n}"
add dont-require-permissions=no name=exporti owner=admin policy=\
    ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source=":\
    local identity [/system identity get name]\r\
    \n:local date [system/clock/get date];\r\
    \n:local time [system/clock/get time];\r\
    \n:local version [system/package/update/get installed-version];\r\
    \n:set \$fileNameExport (\"configExport-\".\$identity.\"-\".\$version.\"-\
    \".\$date.\"-\".\$time);\r\
    \n:set \$fileNameBackup (\"configBackup-\".\$identity.\"-\".\$version.\"-\
    \".\$date.\"-\".\$time);\r\
    \n/export file=\$fileNameExport;\r\
    \n/system backup save name=\$fileNameBackup"
add dont-require-permissions=no name=starwars owner=admin policy=\
    ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source=":\
    beep frequency=500 length=500ms;\r\
    \n:delay 500ms;\r\
    \n \r\
    \n:beep frequency=500 length=500ms;\r\
    \n:delay 500ms;\r\
    \n\r\
    \n:beep frequency=500 length=500ms;\r\
    \n:delay 500ms;\r\
    \n\r\
    \n:beep frequency=400 length=500ms;\r\
    \n:delay 400ms;\r\
    \n\r\
    \n:beep frequency=600 length=200ms;\r\
    \n:delay 100ms;\r\
    \n\r\
    \n:beep frequency=500 length=500ms;\r\
    \n:delay 500ms;\r\
    \n\r\
    \n:beep frequency=400 length=500ms;\r\
    \n:delay 400ms;\r\
    \n\r\
    \n:beep frequency=600 length=200ms;\r\
    \n:delay 100ms;\r\
    \n\r\
    \n:beep frequency=500 length=500ms;\r\
    \n:delay 1000ms;\r\
    \n\r\
    \n\r\
    \n\r\
    \n:beep frequency=750 length=500ms;\r\
    \n:delay 500ms;\r\
    \n\r\
    \n:beep frequency=750 length=500ms;\r\
    \n:delay 500ms;\r\
    \n\r\
    \n:beep frequency=750 length=500ms;\r\
    \n:delay 500ms;\r\
    \n\r\
    \n:beep frequency=810 length=500ms;\r\
    \n:delay 400ms;\r\
    \n\r\
    \n:beep frequency=600 length=200ms;\r\
    \n:delay 100ms;\r\
    \n\r\
    \n:beep frequency=470 length=500ms;\r\
    \n:delay 500ms;\r\
    \n\r\
    \n:beep frequency=400 length=500ms;\r\
    \n:delay 400ms;\r\
    \n\r\
    \n:beep frequency=600 length=200ms;\r\
    \n:delay 100ms;\r\
    \n\r\
    \n:beep frequency=500 length=500ms;\r\
    \n:delay 1000ms;"
