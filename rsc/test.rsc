:local identity [/system identity get name]
:local date [system/clock/get date];
:local time [system/clock/get time];
:local version [system/package/update/get installed-version];
:set $fileNameExport ("export-".$identity."-".$version."-".$date."-".$time);
:set $fileNameBackup ("backup-".$identity."-".$version."-".$date."-".$time);
/export file=$fileNameExport;
/system backup save name=$fileNameBackup

