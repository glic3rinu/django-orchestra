from daemons.plugins import DaemonMethod
import paramiko

class SSH(DaemonMethod):
    name = 'SSH'
    title = 'Run script through SSH'

    def execute(self, daemon_instance, script):
        host = daemon_instance.host
        if not host.sshoption: raise AttributeError
        else:
            ssh = paramiko.SSHClient()
            ssh.load_host_keys(host.sshoption.host_keys)
            key = {'key_filename': host.sshoption.private_key} if host.sshoption.private_key else {}
            ssh.connect(host.sshoption.ip, username=host.sshoption.user, password=host.sshoption.password, **key)
            channel = ssh.get_transport().open_session()
            channel.exec_command(script)
            return channel.makefile('rb', -1).readlines()
                
#            stderr = channel.recv_stderr(1024)
#            #TODO use sterr or exit code? 
#            if stderr: 
#                ssh.close()
#                raise paramiko.SSHException('The command returns the following error: %s' % stderr)
#            result = channel.recv(1024)
#            ssh.close()
