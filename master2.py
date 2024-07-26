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
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

#SCOPES = ['https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/gmail.send']

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
        print(f"Authentication failed for {user}@{server}")
    except paramiko.SSHException as sshException:
        print(f"Unable to establish SSH connection: {sshException}")
    except Exception as e:
        print(f"Exception in connecting to SSH: {e}")
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
    output = stdout.read().decode('utf-8')
    
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

def create_message_with_attachment(sender, to, subject, message_text, file_path):
    """Create a message for an email with an attachment."""
    # Create the base message container
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Attach the message text
    msg = MIMEText(message_text)
    message.attach(msg)

    # Attach the file
    with open(file_path, 'rb') as f:
        mime_base = MIMEBase('application', 'octet-stream')
        mime_base.set_payload(f.read())
    encoders.encode_base64(mime_base)
    mime_base.add_header('Content-Disposition', 'attachment', filename=file_path.split('/')[-1])
    message.attach(mime_base)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        logging.info(f"Message Id: {message['id']}")
        return message
    except Exception as error:
        logging.error(f'An error occurred: {error}')
        return None


# tu stant programu
def main(): 
    print("Starting program...")
    # variables
    delay_time = 5 # how many seconds should the program wait for: creating files, uploads etc.
    googledrive_folderid = "1jIkJ-v9g3z94cLAGFSkBKSI_zrX-_y7C" 
    database_file = "network_devices.db"
    LogFilePath = "NetManagerLog.log"
    max_file_count_googledrive = 140  # Maximum number of files in googledrive_folderid
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S")
    files_to_upload = []
    script_report = {"devices": []}

    logging.basicConfig(filename=LogFilePath, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("---------------------------- Starting script ----------------------------")
    
    # Accessing database
    try:
        conn = sqlite3.connect(database_file)
        cur = conn.cursor()
        cur.execute('SELECT * FROM devices where enable = 1')
        device_info = cur.fetchall()
        logging.info(f"Accessing {database_file}")

        # Authenticating to Google APIs
        try:
            gmail_service = get_google_service('gmail', 'v1', "https://www.googleapis.com/auth/gmail.send")
            drive_service = get_google_service('drive', 'v3', "https://www.googleapis.com/auth/drive.file")
            logging.info("Succesfully authenticated to Google API")
            
            
            # Gathering information about current device
            for item in device_info:
                router_ip = f'{item[1]}'
                router_user = f'{item[2]}'
                router_password = f'{item[3]}'
                
                #json raport
                device_report = {
                    "name": item[1],
                    "actions": {}
                }

                print(f"--------------\nNow accessing ---> \nSource IP: {router_ip}, Logging in as: {router_user}\n--------------")
                logging.info(f"Trying to access Router IP: {router_ip} as User: {router_user}")


                # Create SSH client for current device
                try:
                    ssh = create_ssh_client(router_ip, router_user, router_password)
                    logging.info(f"Successfully logged in to Router IP: {router_ip} as User: {router_user}")

                    device_report["actions"]["SSH Connection"] = {
                        "status": "success",
                        "message": f"Successfully logged in to Router IP: {router_ip} as User: {router_user}"
                    }
                except Exception as e:
                    logging.error(f"An error occured while trying to connect to {router_ip} as {router_user} via SSH: {e}")
                    
                    device_report["actions"]["SSH Connection"] = {
                        "status": "failed",
                        "message": f"An error occured while trying to connect to {router_ip} as {router_user}: {e}"
                    }
                    script_report["devices"].append(device_report)
                    continue
                path = f"{os.getcwd()}\\"
                info = json.loads(retrieve_about_info(ssh))

                export_filename = f"configExport-{info['identity']}-{info['version']}-{current_date}-{current_time}.rsc"
                backup_filename = f"configBackup-{info['identity']}-{info['version']}-{current_date}-{current_time}.backup"
                logging.info(f"Gathered information about {router_ip}: Identity: {info['identity']} System Version: {info['version']}")

                local_export_file = f'{path}\\{export_filename}'
                local_backup_file = f'{path}\\{backup_filename}'

                commands =[
                    f"/export file={export_filename};",
                    f"/system backup save name={backup_filename};"
                ]

                command_fail = 0
                device_report["actions"]["Backup Commands"] = []

                for command in commands:

                    output, error_msg = run_mikrotik_command_viaSSH(ssh, command)
                    if error_msg:
                        msg = f"An error occured while trying to execute a command {command} Error message: {error_msg}"
                        logging.error(msg)
                        
                        device_report["actions"]["Backup Commands"].append({
                        "command": command,
                        "status": "failed",
                        "message": msg
                        })
                        command_fail += 1
                    else:
                        msg = f"Command '{command}' has been executed successfully. Output: {output}"
                        logging.info(msg)

                        device_report["actions"]["Backup Commands"].append({
                            "command": command,
                            "status": "success",
                            "message": msg
                        })
                if command_fail > 0:
                    logging.info(f"Skipping script for this device. Error count: {command_fail}")
                    script_report["devices"].append(device_report)
                    continue
                
                time.sleep(delay_time)


                # Copying files via SCP    --- loop?
                device_report["actions"]["Copying files via SCP"] = []
                scp_fail = 0
                status, scp_error = get_file_viaSCP (ssh, export_filename, local_export_file)
                if status == 1:
                    msg = f"Successfully copied {export_filename} to {local_export_file} via SCP"
                    logging.info(msg)
                    device_report["actions"]["Copying files via SCP"].append({
                        "command": f"Copying {export_filename} to {local_export_file} via SCP",
                        "status": "success",
                        "message": msg
                    })
                else:
                    msg = f"An error occured while trying to copy {export_filename} via SCP: {scp_error}"
                    logging.error(msg)
                    scp_fail +=1
                    device_report["actions"]["Copying files via SCP"].append({
                        "command": f"Copying {export_filename} to {local_export_file} via SCP",
                        "status": "failed",
                        "message": msg
                    })
                
                status, scp_error = get_file_viaSCP(ssh, backup_filename, local_backup_file)
                
                if status == 1:
                    msg = f"Successfully copied {backup_filename} to {local_backup_file} via SCP"
                    logging.info(msg)
                    device_report["actions"]["Copying files via SCP"].append({
                        "command": f"Copying {backup_filename} to {local_backup_file} via SCP",
                        "status": "success",
                        "message": msg
                    })


                else:
                    msg = f"An error occured while trying to copy {backup_filename} via SCP: {scp_error}"
                    logging.error(msg)
                    scp_fail +=1

                    device_report["actions"]["Copying files via SCP"].append({
                        "command": f"Copying {backup_filename} to {local_backup_file} via SCP",
                        "status": "failed",
                        "message": msg
                    })
                
                if scp_fail > 0:
                    logging.info(f"Skipping script for this device. Error count {scp_fail}")
                    script_report["devices"].append(device_report)
                    continue
                time.sleep(delay_time)

                # Uploading files to GoogleDrive via API
                # add variables that says x out of x files uploaded successfully??           
                device_report["actions"]["Uploading files to GoogleDriveAPI"] = []
                files_to_upload = [local_export_file,local_backup_file]
                gd_api_fail = 0
                for file in files_to_upload:
                    try:
                        upload_to_drive(drive_service,file,googledrive_folderid)
                        msg = f"Successfully uploaded {file}, to GoogleDrive folderID: {googledrive_folderid}"
                        logging.info(msg)
                        device_report["actions"]["Uploading files to GoogleDriveAPI"].append({
                        "command": f"Uploading {file}, to GoogleDrive folderID: {googledrive_folderid}",
                        "status": "success",
                        "message": msg
                    })
                    except Exception as e:
                        msg = f"An error occured while trying to upload {file} to GoogleDrive API: {e}"
                        logging.error(msg)
                        gd_api_fail += 1
                        device_report["actions"]["Uploading files to GoogleDriveAPI"].append({
                        "command": f"Uploading {file}, to GoogleDrive folderID: {googledrive_folderid}",
                        "status": "failed",
                        "message": msg
                    })

                
                # Delete files from MikroTik
                # delete commands are variables?
                logging.info(f"Proceeding with deleting files from MikroTik...")
                command_del_fail = 0
                output, error_msg = run_mikrotik_command_viaSSH(ssh, f'file/remove {export_filename}')
                device_report["actions"]["Deleting files from MikroTik"] = []

                if error_msg:
                    msg = f"An error occured while trying to execute a command: file/remove {export_filename}"
                    print(msg)
                    logging.error(msg)
                    command_del_fail += 1

                    device_report["actions"]["Deleting files from MikroTik"].append({
                        "command": f'file/remove {export_filename}',
                        "status": "failed",
                        "message": msg
                    })

                else:
                    msg = f"Successfully executed command 'file/remove {export_filename}' Output: {output}"
                    logging.info(msg)
                    device_report["actions"]["Deleting files from MikroTik"].append({
                        "command": f'file/remove {export_filename}',
                        "status": "success",
                        "message": msg
                    })

                output, error_msg = run_mikrotik_command_viaSSH(ssh,f'file/remove {backup_filename}')

                if error_msg:
                    msg = f"An error occured while trying to execute a command file/remove {backup_filename} Error message: {error_msg}"
                    print(msg)
                    logging.error(msg)
                    command_del_fail += 1
                    device_report["actions"]["Deleting files from MikroTik"].append({
                        "command": f'file/remove {backup_filename}',
                        "status": "failed",
                        "message": msg
                    })
                else:
                    msg = f"Successfully executed command 'file/remove {backup_filename}' Output: {output}"
                    logging.info(msg)
                    device_report["actions"]["Deleting files from MikroTik"].append({
                        "command": f'file/remove {backup_filename}',
                        "status": "success",
                        "message": msg
                    })

                if gd_api_fail > 0:
                    logging.info(f"Terminating script for this device. Count of errors: GoogleDrive API - {gd_api_fail}, Deleting files from Mikrotik - {command_del_fail}")
                    
                    continue
                
                time.sleep(delay_time)

                device_report["actions"]["Deleting files locally"] = []
                local_del_fail = 0
                # Delete files locally
                logging.info(f"Proceeding with deleting files locally...")
                try:
                    delete_files(local_export_file)
                    print(f"{local_export_file} has been deleted")
                    msg = f"Deleting {local_export_file} in {path}"
                    logging.info(msg)
                    device_report["actions"]["Deleting files locally"].append({
                        "command": "",
                        "status": "success",
                        "message": msg
                    })
                except Exception as e:
                    msg = f"Problem occured while trying to delete {local_export_file} locally: {e}"
                    logging.error(msg)
                    local_del_fail += 1
                    device_report["actions"]["Deleting files locally"].append({
                        "comannd": "",
                        "status": "failed",
                        "message": msg
                    })
                try:
                    delete_files(local_backup_file)
                    msg = f"Deleting {local_backup_file} in {path}"
                    print(f"{local_export_file} has been deleted")
                    logging.info(msg)
                    device_report["actions"]["Deleting files locally"].append({
                        "comannd": "",
                        "status": "success",
                        "message": msg
                    })
                except Exception as e:
                    msg = f"Problem occured while trying to delete {local_backup_file} locally: {e}"
                    logging.error(msg)
                    local_del_fail += 1
                    device_report["actions"]["Deleting files locally"].append({
                        "comannd": "",
                        "status": "failed",
                        "message": msg
                    })
                gd_del_fail = 0
                # Delete X amount of files inside GoogleDrive
                logging.info(f"Proceeding with deleting files from GoogleDrive")
                device_report["actions"]["Deleting files from GoogleDriveAPI"] = []

                try:
                    # Assuming this function returns a list of deleted files
                    deleted_files = delete_oldest_files_in_googledrive(drive_service, googledrive_folderid, max_file_count_googledrive)
                    
                    if deleted_files:  # Check if the list is not empty
                        for file in deleted_files:
                            msg = f"Deleted file ID: {file['id']}, Name: {file['name']}, Created Time: {file['createdTime']}"
                            logging.info(msg)

                            device_report["actions"]["Deleting files from GoogleDriveAPI"].append({
                                "command": "",
                                "status": "success",
                                "message": msg
                            })
                    else:
                        msg = f"Skipping this step. Max file count has not yet been reached. {max_file_count_googledrive}"
                        device_report["actions"]["Deleting files from GoogleDriveAPI"].append({
                            "command": "",
                            "status": "success",
                            "message": msg
                        })

                except Exception as e:
                    msg = f"An error occurred while trying to delete files from GoogleDrive: {e}"
                    logging.error(msg)
                    gd_del_fail += 1
                    device_report["actions"]["Deleting files from GoogleDriveAPI"].append({
                        "command": "",
                        "status": "failed",
                        "message": msg
                    })

                script_report["devices"].append(device_report)
                
                #logging.in{router_ip}: Copying via SCP - {scp_fail}, GoogleDrive upload - {gd_api_fail}, Deleting files from MikroTik - {command_del_fail}, Deleting files locally - {local_del_fail}, Deleting files from GoogleDrive - {gd_del_fail}")
        except Exception as e:
            logging.error(f"An error occured while trying to authenticate to Google API: {e}")
    
    except Exception as e:
        msg = f"Problem occured while trying to access Database: {e}"
        logging.error(msg)
    
    file_path = "report.json"

    # Write the JSON report to a file
    with open(file_path, "w") as json_file:
        json.dump(script_report, json_file, indent=4)

    # send mail (in progress):
    try:
        
        sender = "***REMOVED***"
        to = "***REMOVED***"
        subject = "NetManager Script Alert"
        message_text = "This is a test email sent from a Python script."
        attachment_file = os.path.join(os.getcwd(), 'report.json')
        message = create_message_with_attachment(sender, to, subject, message_text, attachment_file)
        
        send_message(gmail_service, 'me', message)
        logging.info("Successfully sent an email")
        print("Successfully sent an email")
    except Exception as e:
        print("There was an error while trying to send an email")
        logging.error(f"An error occurred while trying to send an email: {e}")

    print ("^^^^^^^^^^^^^^\nScript finished.")
    logging.info("---------------------------- Finished script ---------------------------")


if __name__ == '__main__':
    main()