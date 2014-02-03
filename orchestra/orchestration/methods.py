import socket
import sys
import select

import paramiko
from celery.datastructures import ExceptionInfo

from .settings import ORCHESTRATION_SSH_KEY_PATH


def SSH(backend, server, script):
    from .models import ScriptLog
    
    state = ScriptLog.STARTED
    log = ScriptLog.objects.create(state=state, script=script, server=server)
    
    try:
        # ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        addr = server.get_address()
        try:
            ssh.connect(addr, username='root', key_filename=ORCHESTRATION_SSH_KEY_PATH)
        except socket.error:
            log.state = ScriptLog.TIMEOUT
            log.save()
            return 'socket error'
        channel = ssh.get_transport().open_session()
        channel.exec_command(script.replace('\r', ''))
        while True:
            # Non-blocking is the secret ingridient in the async sauce
            select.select([channel], [], [])
            if channel.recv_ready():
                log.stdout += channel.recv(1024)
            if channel.recv_stderr_ready():
                log.stderr += channel.recv_stderr(1024)
            log.save()
            if channel.exit_status_ready():
                break
        log.exit_code = exit_code = channel.recv_exit_status()
        log.state = ScriptLog.SUCCESS if exit_code == 0 else ScriptLog.FAILURE
        channel.close()
        ssh.close()
        log.save()
    except:
        log.state = ScriptLog.ERROR
        log.traceback = ExceptionInfo(sys.exc_info()).traceback
        log.save()
