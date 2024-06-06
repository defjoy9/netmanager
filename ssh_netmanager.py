import paramiko
from ftplib import FTP


def ssh_connect(ip,port,user,password,command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,port=port,username=user,password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read()
    ssh.close()
    return result

def ftp_retrieve_file(ftp_host, ftp_user, ftp_password, remote_filepath, local_filepath):
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_password)
    
    with open(local_filepath, 'wb') as local_file:
        ftp.retrbinary(f'RETR {remote_filepath}', local_file.write)
    
    ftp.quit()


# SSH details
router_ip = '192.168.137.138'
ssh_port = 22
username = "python"
password = "zaq1@WSX"
command = "system resource print"

# FTP details
ftp_user = "ftp"
ftp_password = "ftp"



output = ssh_connect(router_ip,ssh_port,username,password,command)



print(output)