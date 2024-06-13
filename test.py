import paramiko
from scp import SCPClient

def create_ssh_client(server, user, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=user, password=password)
    return ssh

def list_files_on_router(ssh):
    stdin, stdout, stderr = ssh.exec_command('file print')
    files = stdout.read().decode()
    print("Files on the router:\n", files)
    return files

def fetch_files_from_router(ssh, local_export_file, local_backup_file, remote_export_file, remote_backup_file):
    with SCPClient(ssh.get_transport()) as scp:
        # Fetch files from the router and save to the local path
        print(f"Fetching {remote_export_file} to {local_export_file}")
        scp.get(remote_export_file, local_export_file)
        print(f"Fetching {remote_backup_file} to {local_backup_file}")
        scp.get(remote_backup_file, local_backup_file)
        scp.close()

def main():
    # MikroTik Router Details
    router_ip = '192.168.137.28'
    router_user = 'python'
    router_password = 'zaq1@WSX'

    # File names and paths (update the remote paths if needed)
    remote_export_file = 'example_export.rsc'  # File on the router
    remote_backup_file = 'example_backup.backup'  # File on the router
    local_export_file = r'C:\Users\User\Desktop\example_export.rsc'  # Local path where the file will be saved
    local_backup_file = r'C:\Users\User\Desktop\example_backup.backup'  # Local path where the file will be saved

    # Create SSH client
    ssh = create_ssh_client(router_ip, router_user, router_password)

    # List files on the router for debugging
    list_files_on_router(ssh)
    
    # Fetch files from MikroTik router to local PC
    fetch_files_from_router(ssh, local_export_file, local_backup_file, remote_export_file, remote_backup_file)
    
    # Close SSH connection
    ssh.close()

if __name__ == '__main__':
    main()
