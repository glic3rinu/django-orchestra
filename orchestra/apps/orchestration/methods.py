import hashlib
import json
import os
import socket
import sys
import select

import paramiko
from celery.datastructures import ExceptionInfo

from . import settings


def BashSSH(backend, log, server, cmds):
    from .models import BackendLog
    script = '\n\n'.join(['set -e'] + cmds + ['exit 0'])
    script = script.replace('\r', '')
    log.script = script
    log.save()
    
    try:
        # In order to avoid "Argument list too long" we while generate first a
        # script file, then scp the escript and safely execute in remote
        digest = hashlib.md5(script).hexdigest()
        path = os.path.join(settings.ORCHESTRATION_TEMP_SCRIPT_PATH, digest)
        with open(path, 'w') as script_file:
            script_file.write(script)
        # ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        addr = server.get_address()
        try:
            ssh.connect(addr, username='root',
                        key_filename=settings.ORCHESTRATION_SSH_KEY_PATH)
        except socket.error:
            log.state = BackendLog.TIMEOUT
            log.save()
            return
        transport = ssh.get_transport()
        channel = transport.open_session()
        
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(path, "%s.remote" % path)
        sftp.close()
        os.remove(path)
        
        context = {
            'path': "%s.remote" % path,
            'digest': digest
        }
        cmd = (
            "[[ $(md5sum %(path)s|awk {'print $1'}) == %(digest)s ]] && bash %(path)s\n"
            "RETURN_CODE=$?\n"
#            "rm -fr %(path)s\n"
            "exit $RETURN_CODE" % context
        )
        channel.exec_command(cmd)
        if True: # TODO if not async
            log.stdout += channel.makefile('rb', -1).read().decode('utf-8')
            log.stderr += channel.makefile_stderr('rb', -1).read().decode('utf-8')
        else:
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
        log.state = BackendLog.SUCCESS if exit_code == 0 else BackendLog.FAILURE
        channel.close()
        ssh.close()
        log.save()
    except:
        log.state = BackendLog.ERROR
        log.traceback = ExceptionInfo(sys.exc_info()).traceback
        log.save()


def Python(backend, log, server, cmds):
    from .models import BackendLog
    script = [ str(cmd.func.func_name) + str(cmd.args) for cmd in cmds ]
    script = json.dumps(script, indent=4).replace('"', '')
    log.script = '\n'.join([log.script, script])
    log.save()
    stdout = ''
    try:
        for cmd in cmds:
            result = cmd(server)
            stdout += str(result)
    except:
        log.exit_code = 1
        log.state = BackendLog.FAILURE
        log.traceback = ExceptionInfo(sys.exc_info()).traceback
    else:
        log.exit_code = 0
        log.state = BackendLog.SUCCESS
    log.stdout += stdout
    log.save()
