import os
import json
import time
import sqlite3
import logging
import paramiko
from scp import SCPClient
from datetime import datetime, timedelta
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

def upload_to_drive(service, local_file_path, drive_folder_id):
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

def delete_oldest_files_in_googledrive(service, folder_id, max_file_count=30):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        pageSize=1000, # The maximum number of files to return per page.
        fields="nextPageToken, files(id, name, createdTime)"
    ).execute()
    files = results.get('files', [])

    # Sort files by creation date (oldest first)
    files.sort(key=lambda x: x['createdTime'])
    
    print(f"Files in folder ID {folder_id} sorted by creation date (oldest to newest):")
    for file in files:
        print(f"ID: {file['id']}, Name: {file['name']}, Created Time: {file['createdTime']}")

    file_count = len(files)
    # Delete the specified number of oldest files
    if file_count > max_file_count:
        num_files_to_delete = file_count - max_file_count 
        for file in files[:num_files_to_delete]:
            try:
                service.files().delete(fileId=file['id']).execute()
                print(f"File ID: {file['id']} has been deleted.")
            except Exception as e:
                print(f"An error occurred: {e}")

def delete_files(file_path):
    if os.path.exists(file_path):
        print(f"Removing {file_path}")
        os.remove(file_path)
        return 1
    else:
        print(f"Coudn't delete {file_path}")
        return 0

# tu stant programu
def main(): 
    # log file setup
    LogFilePath = "NetManagerLog.txt"
    logging.basicConfig(filename=LogFilePath, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Accessing database
    conn = sqlite3.connect('network_devices.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM devices')
    device_info = cur.fetchall()

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S")
    

    googledrive_folderid = "1jIkJ-v9g3z94cLAGFSkBKSI_zrX-_y7C"

    try:
        #connect and authenticate to Google Drive
        google_drive_service = get_drive_service()
    except Exception as error:
        print(f"--------------!! ERROR !! -------------- Can't authenticate.\nDetails:\n{error}")

    for item in device_info:
        router_ip = f'{item[1]}'
        router_user = f'{item[2]}'
        router_password = f'{item[3]}'
    
        # Przetwarzanie lub wyświetlanie wartości
        print(f"--------------\nNow accessing ---> \nSource IP: {router_ip}, Logging in as: {router_user}\n--------------")

        
        try:
            # Create SSH client
            ssh = create_ssh_client(router_ip, router_user, router_password)
            
            path = f"{os.getcwd()}\\"
            
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

            time.sleep(5)

            # Delete files from MikroTik
            try:
                print(f"Deleting {export_filename} in MikroTik...")
                run_mikrotik_command_viaSSH(ssh,f'file/remove {export_filename}')
                print(f"Deleting {backup_filename} in MikroTik...")
                run_mikrotik_command_viaSSH(ssh,f'file/remove {backup_filename}')
            except Exception:
                print(f"Error occured: {Exception}")

            # Delete files locally
            if delete_files(local_export_file) == 1:
                # file has been deleted
                print()
            if delete_files(local_backup_file) == 0:
                #file was not deleted
                print()
            # Delete X amount of files inside GoogleDrive
            delete_oldest_files_in_googledrive(google_drive_service,googledrive_folderid,30)

        except TimeoutError:
            print(f"TIMEOUT - Can't reach host {router_ip}")
        except Exception as error:
            print(f"--------------!! ERROR !! --------------\nDetails:\n{error}")
        finally:
            ssh.close()
            conn.close()

    print ("^^^^^^^^^^^^^^\nScript finished.")


if __name__ == '__main__':
    main()
