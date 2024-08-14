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

def get_google_service(api_name, api_version, scopes, credentials_file):
    creds = None
    # Check if the token file exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)

    # If no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            # Run the console flow for headless environments
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f'Please go to this URL: {auth_url}')
            code = input('Enter the authorization code: ')
            creds = flow.fetch_token(code=code)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build(api_name, api_version, credentials=creds)
    return service


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
            drive_service = get_google_service('drive', 'v3', ["https://www.googleapis.com/auth/drive.file"],'credentials.json')
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

        #logging.in{router_ip}: Copying via SCP - {scp_fail}, GoogleDrive upload - {gd_api_fail}, Deleting files from MikroTik - {command_del_fail}, Deleting files loocally - {local_del_fail}, Deleting files from GoogleDrive - {gd_del_fail}")
        except Exception as e:
            logging.error(f"An error occured while trying to authenticate to Google API: {e}")

    except Exception as e:
        msg = f"Problem occured while trying to access Database: {e}"
        logging.error(msg)


        print ("^^^^^^^^^^^^^^\nScript finished.")
        logging.info("---------------------------- Finished script ---------------------------")

if __name__ == '__main__':
    main()