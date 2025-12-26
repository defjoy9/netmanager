# NetManager

A production-grade Python automation tool I designed and built to eliminate manual network device management across multiple sites. It handles SSH access, version-aware configuration backups, AES-encrypted credential storage, and automated cloud archiving.

---

## The Problem

Managing backups for 140+ MikroTik routers across multiple sites was:
- **Time-consuming**: Manual SSH connections and backup exports took hours weekly
- **Error-prone**: Human errors led to missed backups and inconsistent configurations
- **Insecure**: Plaintext password storage and manual credential management
- **Unscalable**: No way to reliably track backup history or audit changes

Every missed backup was a potential disaster waiting to happen.

---

## The Solution

I designed and built NetManager from scratch to automate the entire backup workflow:

**My Role:**
- Architected the complete system (database schema, encryption layer, backup workflow)
- Wrote 100% of the codebase (SSH automation, credential management, Google Drive integration)
- Deployed and maintained the solution in production
- Handled RouterOS version detection for backward compatibility (v6 vs v7)

**What It Does:**
- Automatically connects to MikroTik devices daily
- Creates version-aware configuration exports and full system backups
- Encrypts and stores credentials securely in SQLite
- Uploads backups to Google Drive with retention policies
- Generates detailed audit logs and JSON reports for every run

---

## Tech Stack

**Core Technologies:**
- Python 3.10+
- paramiko (SSH/SCP automation)
- SQLite (device & credential database)
- pycryptodome (AES-256 encryption)
- Google Drive API (cloud backup storage)
- python-dotenv (environment configuration)

**Standard Library:**
- `smtplib` (email notifications)
- `logging` (audit trails)
- `json` (structured reporting)

---

## System Architecture

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

## Key Technical Decisions

### 1. SQLite + AES Encryption for Credentials
**Why:** Lightweight, zero-configuration database with full encryption at rest
- No external database server required (easy deployment)
- AES-256 encryption ensures credentials are never stored in plaintext
- Encryption keys generated separately and excluded from version control
- Decryption only happens in-memory during runtime

### 2. Version Detection for RouterOS 6 vs 7
**Why:** MikroTik changed export command syntax between major versions
- RouterOS 6: Uses `/export file=config`
- RouterOS 7: Uses `/export show-sensitive file=config`
- Automatic version detection prevents failed backups
- Ensures sensitive data (passwords, keys) is included in exports

### 3. Sequential Connection Handling
**Why:** Stability over speed for production reliability
- SSH connections can fail unpredictably on network devices
- Sequential processing provides better error isolation and logging
- Easier to debug and retry individual device failures
- Lower resource footprint on the automation server

---

## Biggest Technical Challenge

**Challenge:** Handling SSH timeouts and device inconsistencies across 140+ routers

Many devices were:
- Behind unreliable WAN connections
- Running different RouterOS versions with varying behaviors
- Configured with different security policies

**Solution:**
1. Implemented robust error handling with detailed logging for each connection
2. Added version detection to dynamically adjust commands per device
3. Created retry logic with exponential backoff for network failures
4. Built comprehensive JSON reporting to track success/failure patterns
5. Used connection pooling and proper cleanup to prevent resource exhaustion

This approach reduced backup failures from ~15% to <2%.

---

## What I Learned

**SSH Automation at Scale:**
- Managing persistent SSH connections and proper cleanup
- Handling different device firmware versions programmatically
- Building resilient automation that gracefully handles network failures

**Security Best Practices:**
- Implementing AES encryption for credential storage
- Key management and separation from codebase
- Never logging or exposing plaintext passwords

**Production System Design:**
- Importance of comprehensive logging and audit trails
- Building idempotent operations (safe to retry)
- Balancing automation speed vs reliability
- Creating actionable reports for monitoring and debugging

---

## Measurable Impact

- **140+ devices** fully automated
- **Daily backups** save ~8-10 hours of manual work per week
- **Zero password exposure** through AES encryption
- **Historical backup retention** with automated cleanup (configurable FIFO)
- **<2% failure rate** with detailed error reporting for quick resolution
- **100% audit trail** via JSON reports and structured logging

---

## Features

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

## Scripts Overview

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

## Environment Configuration

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

## Installation & Requirements

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

## Usage

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

## Future Improvements

Potential enhancements under consideration:

* **Testing**: Add unit tests for core backup and encryption logic
* **Retry Logic**: Implement more sophisticated retry mechanisms for network failures
* **Web Dashboard**: Build monitoring interface for device status and backup history
* **Scheduling**: Integrate APScheduler for flexible backup scheduling
* **Parallel Processing**: Add concurrent connection handling with configurable limits
* **Alerting**: Enhanced email notifications with success/failure summaries

---

## License

MIT License - see LICENSE file for details.

---

## Disclaimer

This tool is intended for **authorized network administration use only**.

Ensure you have proper authorization before connecting to any network devices. Misuse of this tool may violate security policies or laws. The author is not responsible for unauthorized or malicious use.
