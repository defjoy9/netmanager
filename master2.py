import os
import json
import time
import logging
import paramiko
from scp import SCPClient
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def create_ssh_client(server, user, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=user, password=password)
    return ssh

def retrieve_about_info(ssh):

    get_system_version = ':put [system/package/update/get installed-version];'
    get_identity = ':put [system/identity/get name]'

    # Execute the commands
    stdin, stdout, stderr = ssh.exec_command(get_system_version)
    system_version = stdout.read().decode().strip()

    stdin, stdout, stderr = ssh.exec_command(get_identity)
    identity = stdout.read().decode().strip()
# Tworzenie pustego słownika z kluczami 'version' i 'identity'
    result = {
        'version': system_version,
        'identity': identity
    }

    return json.dumps(result)

def run_mikrotik_command_viaSSH (ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    # log  errors/output ???
    if errors:
        raise Exception(f"Error running MikroTik script: {errors}")
    return output

def get_file_viaSCP (ssh, src, dst):
    with SCPClient(ssh.get_transport()) as scp:
        # Fetch files from the router and save to the local path
        print(f"Fetching {src} to {dst}")
        scp.get(src, dst)
        scp.close()
    
    return 1

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
    file = service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
    print(f"File ID: {file.get('id')}, Name: {file.get('name')} uploaded to Google Drive.")
    if drive_folder_id:
        print(f"Uploaded to folder ID: {drive_folder_id}")
    else:
        print("Uploaded to the root directory.")
# tu stant programu

def main():
    # MikroTik Router Details
    with open('data.json','r') as json_file:
        data = json.load(json_file)

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S")
    
    try:
        #connect and authenticate to Google Drive
        google_drive_service = get_drive_service()
    except Exception as error:
        print(f"--------------!! ERROR !! -------------- Can't authenticate.\nDetails:\n{error}")

    for entry in data:
        router_ip = entry.get('source_ip')
        router_user = entry.get('user')
        router_password = entry.get('password')
    
        # Przetwarzanie lub wyświetlanie wartości
        print(f"--------------\nNow accessing ---> \nSource IP: {router_ip}, Logging in as: {router_user}\n--------------")

        
        
        try:
            # Create SSH client
            ssh = create_ssh_client(router_ip, router_user, router_password)
            
            path = r'C:\Users\User\Desktop'
            
            info = json.loads(retrieve_about_info(ssh))

            export_filename = f"configExport-{info['identity']}-{info['version']}-{current_date}-{current_time}.rsc"
            backup_filename = f"configBackup-{info['identity']}-{info['version']}-{current_date}-{current_time}.backup"

            local_export_file = f'{path}\\{export_filename}'
            local_backup_file = f'{path}\\{backup_filename}'

            commands =[
                f"/export file={export_filename};",
                f"/system backup save name={backup_filename};"
            ]

            for command in commands:
                run_mikrotik_command_viaSSH(ssh, command)

            time.sleep(5)

            # downloading the backup/export files from router
            get_file_viaSCP (ssh, export_filename, local_export_file)
            get_file_viaSCP (ssh, backup_filename, local_backup_file)

            time.sleep(5)

            upload_to_drive(google_drive_service, local_export_file)
            upload_to_drive(google_drive_service, local_backup_file)

        except TimeoutError:
            print(f"TIMEOUT - Can't reach host {router_ip}")
        except Exception as error:
            print(f"--------------!! ERROR !! --------------\nDetails:\n{error}")

    print ("^^^^^^^^^^^^^^\nScript finished.")


if __name__ == '__main__':
    main()
