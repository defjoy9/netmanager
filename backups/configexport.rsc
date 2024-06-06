# 2024-06-05 16:00:43 by RouterOS 7.15
# software id = Q3HR-X5V6
#
# model = RB760iGS
# serial number = A36A0B4C8A9A
/port
set 0 name=serial0
/ip firewall connection tracking
set udp-timeout=10s
/ip dhcp-client
add interface=ether1
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
