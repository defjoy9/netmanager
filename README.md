# NetManager

A Python-based automation tool I built to manage MikroTik devices across multiple sites.
It handles SSH access, configuration backups, secure credential storage, and automated uploading to Google Drive.

This project was originally created for the company I worked for, and I’ve continued improving it as a way to sharpen my automation and scripting skills.

---

# 1. Purpose

I built NetManager to solve a simple recurring problem:
**manually backing up dozens of MikroTik routers was slow, error-prone, and inconsistent.**

I wanted a tool that could:

* connect to many routers automatically
* run version-aware commands
* pull backups reliably
* store them securely
* keep historical logs
* and avoid ever exposing passwords in plaintext

This script replaced a manual workflow and saved our team a significant amount of time.

---

# 2. How the System Works (Architecture)

```
┌───────────────────────┐
│  SQLite Database       │  ← stores encrypted credentials & device records
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  AES Encryption Layer  │  ← decrypts only at runtime
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  SSH / SCP (Paramiko) │  ← connects to MikroTik routers
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  Backup & Export Ops   │  ← version-aware commands for RouterOS 6/7
└───────────┬───────────┘
            │
            ▼
┌────────────────────────────┐
│ Google Drive Upload (API)  │  ← stores backups, deletes old ones
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ Logging + JSON Reporting   │  ← full audit trail for each run
└────────────────────────────┘
```

---

# 3. Key Features

### SSH & SCP Automation

* Connects to MikroTik devices using `paramiko`
* Detects RouterOS version (v6 vs v7)
* Runs appropriate export/backup commands
* Transfers backup files via SCP

### Automated Backup Workflow

* Creates configuration exports + full backups
* Uploads backups to Google Drive
* Keeps a fixed number of backups (FIFO deletion)
* Generates a JSON report for each run

### Secure Credential Management

* AES-encrypted passwords stored in SQLite
* Keys generated separately and never committed
* Decryption happens only during execution

### Device Database

Stores:

* device IP
* login details (encrypted)
* RouterOS version
* timestamps
* backup history

### Logging & Reporting

* Detailed log file (`netmanager.log`)
* JSON report describing each device’s actions, errors, and results

---

# 4. Scripts

### `master2.py`

Main automation script:

* decrypts credentials
* establishes SSH connections
* exports backups
* uploads to Google Drive
* cleans old backups
* logs everything

### `modify_sql.py`

Utility script for updating device entries in the SQLite database.

### `create_keys.py`

Creates AES encryption keys for securely storing passwords.

---

# 5. Environment Configuration

The script uses a `.env` file for all sensitive settings:

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
```

---

# 6. Requirements

Python 3.10+
Dependencies:

* `paramiko`
* `scp`
* `python-dotenv`
* `google-api-python-client`
* `google-auth`
* `pycryptodome`
* Standard library: `smtplib`, `logging`, `sqlite3`

Install with:

```bash
pip install -r requirements.txt
```

---

# 7. Usage

Clone the repo:

```bash
git clone https://github.com/defjoy9/netmanager.git
cd netmanager
```

Run backups:

```bash
python master2.py
```

After execution:

* backup files will be uploaded
* logs are stored in `netmanager.log`
* results are written to `report.json`

---

# 8. Known Limitations / Future Improvements

I’m currently planning or considering:

* adding unit tests
* improving error-handling during SSH failures
* retry logic for unstable network connections
* optional web dashboard for device status
* better scheduling with cron or APScheduler

---

# 9. License

MIT License.

---

# 10. Disclaimer

This tool is intended for authorized use only. Misuse may lead to security risks. I am not responsible for unauthorized or malicious use.
