import os
import sys
import json
import time
import base64
import sqlite3
import logging
import paramiko
from scp import SCPClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

#SCOPES = ['https://www.googleapis.com/auth/drive.file']

def create_ssh_client(server, user, password):
    try:
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Set up SSH connection parameters
        ssh_config = {
            'hostname': server,
            'port': 22,
            'username': user,
            'password': password,
            'look_for_keys': False,
            'allow_agent': False,
            'disabled_algorithms': {
                'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']
            }
        }
        
        # Connect to the host
        client.connect(**ssh_config)
        
        print(f"Connected to {server}")
        
        # Return the client object
        return client
        
    except paramiko.AuthenticationException:
        logging.error(f"Authentication failed for {user}@{server}")
    except paramiko.SSHException as sshException:
        logging.error(f"Unable to establish SSH connection: {sshException}")
    except Exception as e:
        logging.error(f"Exception in connecting to SSH: {e}")
        return None

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

def run_mikrotik_command_viaSSH(ssh, command):

    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8').strip()
    
    error_patterns = ["bad command name","expected end of command", "invalid", "failure", "error"]
    error = None
    for pattern in error_patterns:
        if pattern in output.lower():
            error = output
            break
    
    return output, error

def get_file_viaSCP (ssh, src, dst):
    with SCPClient(ssh.get_transport()) as scp:
        # Fetch files from the router and save to the local path
        print(f"Fetching {src} to {dst}")
        
        try:
            scp.get(src, dst)
            scp.close()
            return 1,None
        except Exception as e:
            print(f"An error occured while trying to fetch files via scp: {e}")
            scp.close()
            return 0,e

def get_google_service(api_name, api_version, scopes):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build(api_name, api_version, credentials=creds)

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
    
    file_count = len(files)
    deleted_files = []

    # Delete the specified number of oldest files
    if file_count > max_file_count:
        logging.info(f"Deleting files from GoogleDrive. Exceeded max file count. {file_count}>{max_file_count}")
        num_files_to_delete = file_count - max_file_count 
        for file in files[:num_files_to_delete]:
            try:
                service.files().delete(fileId=file['id']).execute()
                deleted_files.append({
                    'id': file['id'],
                    'name': file['name'],
                    'createdTime': file['createdTime']
                })
            except Exception as e:
                logging.error(f"An error occurred while deleting file ID: {file['id']}: {e}")
    if file_count <= max_file_count:
        logging.info(f"Skipping deleting files from GoogleDrive. File Count {file_count} <= Max file count {max_file_count}")
        return 0
    return deleted_files

def delete_files(file_path):
    if os.path.exists(file_path):
        print(f"Removing {file_path}")
        os.remove(file_path)
        return 1
    else:
        print(f"Coudn't delete {file_path}")
        return 0

def email_send(username, password, mail_from, mail_to, mail_subject, mail_body, attach_filename):
    current_directory = os.getcwd()
    attach_filepath = os.path.join(current_directory, attach_filename)

    mimemsg = MIMEMultipart()
    mimemsg['From']=mail_from
    mimemsg['To']=mail_to
    mimemsg['Subject']=mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))

    # ------- Attachment
    with open(attach_filepath, "rb") as file:

        part1 = MIMEBase('application', 'octet-stream')
        part1.set_payload(file.read())
        encoders.encode_base64(part1)
        part1.add_header('Content-Disposition', f"attachment; filename={attach_filename}")
        mimemsg.attach(part1)

    connection = smtplib.SMTP(host='smtp.office365.com', port=587)
    connection.starttls()
    connection.login(username,password)
    connection.send_message(mimemsg)
    connection.quit()

# tu stant programu
def main(): 
    print("Starting program...")
    # variables
    delay_time = 5 # how many seconds should the program wait for: creating files, uploads etc.
    googledrive_folderid = "***REMOVED***" 
    database_file = "network_devices.db"
    LogFilePath = "net_manager_log.log"
    max_file_count_googledrive = 140  # Maximum number of files in googledrive_folderid
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S")

    logging.basicConfig(filename=LogFilePath, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("---------------------------- Starting script ----------------------------")
    
    # Accessing database -------------------------------------------------------------------------------
    try:
        conn = sqlite3.connect(database_file)
        cur = conn.cursor()
        cur.execute('SELECT * FROM devices where enable = 1')
        device_info = cur.fetchall()
        logging.info(f"Accessing {database_file}")

        # Authenticating to Google APIs -------------------------------------------------------------------------------
        try:
            drive_service = get_google_service('drive', 'v3', ["https://www.googleapis.com/auth/drive.file"])
            logging.info("Succesfully authenticated to Google API")
            
            # Gathering information about current device -------------------------------------------------------------------------------
            for item in device_info:
                router_ip = f'{item[1]}'
                router_user = f'{item[2]}'
                router_password = f'{item[3]}'
                
                print(f"--------------\nNow accessing ---> \nSource IP: {router_ip}, Logging in as: {router_user}\n--------------")
                logging.info(f"Trying to access Router IP: {router_ip} as User: {router_user}")

                # Create SSH client for current device -------------------------------------------------------------------------------
                try:
                    ssh = create_ssh_client(router_ip, router_user, router_password)
                    
                    if ssh is not None:                        
                        logging.info(f"Successfully logged in to Router IP: {router_ip} as User: {router_user}")

                except Exception as e:
                    logging.error(f"An error occured while trying to connect to {router_ip} as {router_user} via SSH: {e}")
                    continue

                path = f"{os.getcwd()}\\"
                info = json.loads(retrieve_about_info(ssh))

                export_filename = f"configExport-{info['identity']}-{info['version']}-{current_date}-{current_time}.rsc"
                backup_filename = f"configBackup-{info['identity']}-{info['version']}-{current_date}-{current_time}.backup"
                logging.info(f"Gathered information about {router_ip}: Identity: {info['identity']} System Version: {info['version']}")
                
                #logging.in{router_ip}: Copying via SCP - {scp_fail}, GoogleDrive upload - {gd_api_fail}, Deleting files from MikroTik - {command_del_fail}, Deleting files locally - {local_del_fail}, Deleting files from GoogleDrive - {gd_del_fail}")
        except Exception as e:
            logging.error(f"An error occured while trying to authenticate to Google API: {e}")
    
    except Exception as e:
        msg = f"Problem occured while trying to access Database: {e}"
        logging.error(msg)
    

    print ("^^^^^^^^^^^^^^\nScript finished.")
    logging.info("---------------------------- Finished script ---------------------------")


if __name__ == '__main__':
    main()