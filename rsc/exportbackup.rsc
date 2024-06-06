# Function that replaces all special characters in a string with the '-' character.
# Here it's used to convert date and time to more readable format.
# Example: from jul/16//2018 11:33:22 to jul-16--2018-11-33-22
:global replaceStringFunc do={
    :local textBefore $text
    :local textAfter
    :local znaki {" "="-";"/"="-";":"="-";}

    :for i from=0 to=([:len $textBefore] -1) do={ 
        :local char [:pick $textBefore $i]

        :foreach zly,dobry in=$znaki do={
            :if ($char=$zly) do={
                :set $char $dobry;
            }
        }
        :set textAfter ($textAfter . $char)
    }
    :return $textAfter
}

#:put [$replaceStringFunc text="jul/16//2018 11:33:22"];
# ------------------------------------------------------

:global replaceStringFunc

:local fileNameExport ""
:local fileNameBackup ""

# FTP settings
:local ftpHost "192.168.137.200"
:local ftpUser "python"
:local ftpPass "zaq1@WSX"
:local ftpDstPath "C:\Users\User\Desktop"

# Get system information
:local identity [/system identity get name]
:local date [system/clock/get date];
:local time [system/clock/get time];
:local version [system/package/update/get installed-version]

:set date [$replaceStringFunc text=$date];
:set time [$replaceStringFunc text=$time];


# Set file names
:set fileNameExport ("configExport-".$identity."-".$version."-".$date."-".$time)
:set fileNameBackup ("configBackup-".$identity."-".$version."-".$date."-".$time)

# Commands
/export file=$fileNameExport;
/system backup save name=$fileNameBackup

# Upload files to Destination path
/tool fetch address=$ftpHost src-path=($fileNameExport.".rsc") dst-path=($ftpDstPath . "Uploaded-export-".$fileNameExport.".rsc") \
 upload=yes mode=ftp user=$ftpUser  password=$ftpPass

/tool fetch address=$ftpHost src-path=($fileNameBackup.".backup") dst-path=($ftpDstPath . "Uploaded-backup-".$fileNameBackup.".backup") \
 upload=yes mode=ftp user=$ftpUser  password=$ftpPass

:put "Waiting..."
:delay 5s;

:local tmpEx ($fileNameExport.".rsc")
:local tmpBc ($fileNameBackup.".backup")


# file/remove $tmpEx
# file/remove $tmpBc
# :put "Deleted"