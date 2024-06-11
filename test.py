get_system_version = ':put [system/package/update/get installed-version];'
    get_identity = ':put [system/identity/get name]'
    stdin, stdout, stderr = ssh.exec_command(get_system_version)
    system_version = stdout.read().decode().strip()
    stdin, stdout, stderr = ssh.exec_command(get_identity)
    identity = stdout.read().decode().strip()   
    
    print(f"Identity - {identity}; System version {system_version}")