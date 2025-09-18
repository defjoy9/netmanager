# NetManager Script

## Overview
**NetManager** is a Python-based automation suite designed to manage MikroTik network devices efficiently. This suite allows users to:

- Connect to MikroTik routers via SSH
- Execute configuration and backup commands
- Retrieve and store device information securely
- Upload backups to Google Drive
- Maintain a historical record of device operations
- Encrypt and manage sensitive data such as passwords

It is aimed at network administrators or IT teams looking for a streamlined solution to manage multiple MikroTik devices while ensuring sensitive information is encrypted and stored safely.

---

## Features

### 1. **SSH and SCP Access**
- Connects to MikroTik routers via SSH using `paramiko`.
- Executes commands based on the router's OS version (6 or 7).
- Retrieves system identity and version information.
- Transfers files from the router to the local system using SCP.

### 2. **Backup Management**
- Exports router configuration and creates backups.
- Automatically uploads backups to a Google Drive folder.
- Maintains a maximum number of backups in Google Drive by deleting the oldest files.
- Optionally sends a JSON report via email containing all device actions and statuses.

### 3. **Secure Password Handling**
- Passwords are encrypted using AES encryption before being stored in the database.
- Decryption occurs only during the execution of the script for authentication purposes.
- Keys are stored in `key.txt`, which is never uploaded to public repositories.

### 4. **Database Integration**
- Uses SQLite (`network_devices.db`) to store:
  - Device information (IP, version, identity)
  - Login credentials (usernames, encrypted passwords)
  - Backup schedules and statuses

### 5. **Logging and Reporting**
- All actions, errors, and script progress are logged in a local log file.
- Generates a detailed JSON report of all device operations.
- Provides structured logs for troubleshooting or auditing purposes.

---

## Scripts

### `master2.py`
- Main script that coordinates the entire automation process.
- Connects to devices, executes backup commands, uploads files, and deletes old backups.
- Handles decryption of passwords, SCP transfers, Google Drive uploads, and logging.

### `modify_sql.py`
- Example script to modify database entries.
- Allows updating IP addresses or other device-specific information.
- Useful for testing or updating records without manual SQLite editing.

### `create_keys.py`
- Generates AES encryption keys.
- Encrypts device passwords before storing them in the database.
- Ensures sensitive data is securely stored and never exposed in plaintext.

---

## Environment Variables
The script relies on a `.env` file to securely store credentials and configuration. Example variables include:

```dotenv
SSHPORT=22
MAIL_FROM=youremail@example.com
MAIL_FROM_PASSWORD=yourpassword
MAIL_TO=recipient@example.com
HOST_SMTP=smtp.example.com
GOOGLEDRIVE_FOLDERID=your_folder_id
SERVICE_ACCOUNT_FILE=path/to/service_account.json
DATABASE_FILE=network_devices.db
LOG_FILEPATH=netmanager.log
````

---

## Requirements

* Python 3.10+
* Dependencies:

  * `paramiko`
  * `scp`
  * `python-dotenv`
  * `google-api-python-client`
  * `google-auth`
  * `pycryptodome`
  * `smtplib` (standard library)

---

## How to Use

1. Clone the repository:

```bash
git clone https://github.com/defjoy9/netmanager.git
cd netmanager
```

2. Install dependencies:

3. Create and configure the `.env` file with your credentials.

4. Ensure your SQLite database (`network_devices.db`) contains your devices and encrypted passwords.

5. Run the main script:

```bash
python master2.py
```

6. Check logs and `report.json` for detailed actions and statuses.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Disclaimer

This tool is intended for authorized network administration only. Misuse may lead to security risks or legal consequences. The developer is not responsible for unauthorized use.

```
