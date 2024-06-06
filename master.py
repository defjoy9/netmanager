import paramiko
from scp import SCPClient

# MikroTik Router Details
router_ip = '192.168.137.131'
router_user = 'python'
router_password = 'zaq1@WSX'

# Paths for local files
local_export_file = r'C:\Users\User\OneDrive - ORBITECH Sp. z o.o\Dokumenty\projects\cyfrowe - NetManager\backups\configexport.rsc'
local_backup_file = r'C:\Users\User\OneDrive - ORBITECH Sp. z o.o\Dokumenty\projects\cyfrowe - NetManager\backups\configBackup.backup'

def create_ssh_client(server, user, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=user, password=password)
    return ssh

def run_mikrotik_script(ssh):
    # Run MikroTik commands to create export and backup files
    commands = [
        '/export file=configExport',
        '/system backup save name=configBackup'
    ]

    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())
        print(stderr.read().decode())

def fetch_files_from_router(ssh, local_export, local_backup):
    with SCPClient(ssh.get_transport()) as scp:
        scp.get('/configExport.rsc', local_export)
        scp.get('/configBackup.backup', local_backup)

def main():
    # Create SSH client
    ssh = create_ssh_client(router_ip, router_user, router_password)

    # Run MikroTik script to generate export and backup files
    run_mikrotik_script(ssh)

    # Fetch files from MikroTik router to local PC
    fetch_files_from_router(ssh, local_export_file, local_backup_file)

    ssh.close()

if __name__ == '__main__':
    main()
