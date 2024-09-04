import os
import sys
import json
import time
import base64
import sqlite3
import logging
import paramiko
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
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

def retrieve_about_info(ssh,version):

    if version == '6':
        get_system_version = ':put [system package update get installed-version];'
        get_identity = ':put [system identity get name]'
    if version == '7':
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

def get_google_service(api_name, api_version, scopes):
    # Load the service account key file
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
    
    # Build the service object
    return build(api_name, api_version, credentials=creds)


# tu stant programu
def main(): 
    print("Starting program...")
    # variables
    database_file = "network_devices1.2.db"
    LogFilePath = "netmanagerlog.log"
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
                cur.execute("SELECT password, nonce, tag FROM devices WHERE ip_address=?", ('192.168.137.122',))
                row = cur.fetchone()
                ciphertext, nonce, tag = row
                
                with open("key.txt", "rb") as f:
                    key = f.read()
                
                cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
                data = cipher.decrypt_and_verify(ciphertext, tag)
                
                router_ip = f'{item[2]}'
                router_user = f'{item[3]}'
                #router_password = decrypt_password(enc_password)
                router_password = data.decode()
                router_version = f'{item[5]}'
                
                print(f"--------------\nNow accessing ---> \nSource IP: {router_ip}, Logging in as: {router_user}\n--------------")
                logging.info(f"Trying to access Router IP: {router_ip} as User: {router_user} ----------------------------")

                # Create SSH client for current device -------------------------------------------------------------------------------
                try:
                    ssh = create_ssh_client(router_ip, router_user, router_password)
                    
                except Exception as e:
                    logging.error(f"An error occured while trying to connect to {router_ip} as {router_user} via SSH: {e}")
                    continue

                info = json.loads(retrieve_about_info(ssh,router_version))
                logging.info(f"Gathered information about {router_ip}: Identity: {info['identity']} System Version: {info['version']}")
                logging.info("_----------------------Script Finished----------------------")

        except Exception as e:
            logging.error(f"An error occured while trying to authenticate to Google API: {e}")
    
    except Exception as e:
        msg = f"Problem occured while trying to access Database: {e}"
        logging.error(msg)

if __name__ == '__main__':
    main()