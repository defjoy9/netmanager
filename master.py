import os
import paramiko
from scp import SCPClient
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# MikroTik Router Details
router_ip = '192.168.137.61'
router_user = 'python'
router_password = 'zaq1@WSX'


current_time = datetime.now().strftime("%H-%M-%S")
current_date = datetime.now().strftime("%Y-%m-%d")

# Paths for local files
local_export_file = fr'C:\Users\User\Desktop\configexport-{identity}-{system_version}-{current_date}-{current_time}.rsc'
local_backup_file = fr'C:\Users\User\Desktop\configBackup-{identity}-{system_version}-{current_date}-{current_time}.backup'

def create_ssh_client(server, user, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=user, password=password)
    return ssh

def run_mikrotik_script(ssh):
    # Commands to run
    command = """
    :local identity [/system identity get name];:local date [system/clock/get date];:local time [system/clock/get time];:local version [system/package/update/get installed-version];:local fileNameExport;:local fileNameBackup;:set fileNameExport ("configExport-".$identity."-".$version."-".$date."-".$time);:set fileNameBackup ("configBackup-".$identity."-".$version."-".$date."-".$time);/export file=$fileNameExport;/system backup save name=$fileNameBackup;
    """
    # log  executing
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    # log  errors/output
    if errors:
        raise Exception(f"Error running MikroTik script: {errors}")
    return output

def fetch_files_from_router(ssh, local_export, local_backup, identity, system_version):
    with SCPClient(ssh.get_transport()) as scp:
        # List .rsc files on the router with detailed information
        stdin, stdout, stderr = ssh.exec_command(f'ls -l /configExport-{identity}-{system_version}-{current_date}*.rsc')
        remote_rsc_files_info = stdout.read().decode().splitlines()

        # Fetch each matching .rsc file individually
        for remote_file_info in remote_rsc_files_info:
            # Extract the file name from the detailed information
            remote_file_name = remote_file_info.split()[-1]

            # Check if the remote file is a regular file (not a directory)
            if remote_file_info.startswith('-'):
                # Fetch the .rsc file
                scp.get(remote_file_name, local_export)

        # List .backup files on the router with detailed information
        stdin, stdout, stderr = ssh.exec_command(f'ls -l /configBackup-{identity}-{system_version}-{current_date}*.backup')
        remote_backup_files_info = stdout.read().decode().splitlines()

        # Fetch each matching .backup file individually
        for remote_file_info in remote_backup_files_info:
            # Extract the file name from the detailed information
            remote_file_name = remote_file_info.split()[-1]

            # Check if the remote file is a regular file (not a directory)
            if remote_file_info.startswith('-'):
                # Fetch the .backup file
                scp.get(remote_file_name, local_backup)

def get_drive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(service, local_file_path, drive_folder_id=None):
    file_metadata = {
        'name': os.path.basename(local_file_path),
        'parents': [drive_folder_id] if drive_folder_id else []
    }
    media = MediaFileUpload(local_file_path, mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')} uploaded to Google Drive.")

def main():
    # Create SSH client
    ssh = create_ssh_client(router_ip, router_user, router_password)

    # Run MikroTik script to generate export and backup files
    output = run_mikrotik_script(ssh)

    # Fetch files from MikroTik router to local PC
    fetch_files_from_router(ssh, local_export_file, local_backup_file, identity, system_version)

    ssh.close()

if __name__ == '__main__':
    main()
