import paramiko

def execute_ssh(script, ip, user, password, host_keys):
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(host_keys)
    ssh.connect(ip, username=user, password=password)
    channel = ssh.get_transport().open_session()
    channel.exec_command(script)
    stderr = channel.recv_stderr(1024)
    #TODO use sterr or exit code? 
    if stderr: 
        raise paramiko.SSHException('The command returns the following error: %s' % stderr)

