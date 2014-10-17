import hashlib
import json
import logging
import os
import socket
import sys
import select

import paramiko
from celery.datastructures import ExceptionInfo

from . import settings


logger = logging.getLogger(__name__)

transports = {}


def BashSSH(backend, log, server, cmds):
    from .models import BackendLog
    # TODO save remote file into a root read only directory to avoid users sniffing passwords and stuff
    
    script = '\n'.join(['set -e', 'set -o pipefail'] + cmds + ['exit 0'])
    script = script.replace('\r', '')
    digest = hashlib.md5(script).hexdigest()
    path = os.path.join(settings.ORCHESTRATION_TEMP_SCRIPT_PATH, digest)
    remote_path = "%s.remote" % path
    log.script = '# %s\n%s' % (remote_path, script)
    log.save(update_fields=['script'])
    
    channel = None
    ssh = None
    try:
        logger.debug('%s is going to be executed on %s' % (backend, server))
        # Avoid "Argument list too long" on large scripts by genereting a file
        # and scping it to the remote server
        with open(path, 'w') as script_file:
            script_file.write(script)
        
        # ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        addr = server.get_address()
        try:
            # TODO timeout
            ssh.connect(addr, username='root', key_filename=settings.ORCHESTRATION_SSH_KEY_PATH, timeout=10)
        except socket.error:
            logger.error('%s timed out on %s' % (backend, server))
            log.state = BackendLog.TIMEOUT
            log.save(update_fields=['state'])
            return
        transport = ssh.get_transport()
        
        # Copy script to remote server
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(path, remote_path)
        sftp.close()
        os.remove(path)
        
        # Execute it
        context = {
            'remote_path': remote_path,
            'digest': digest
        }
        cmd = (
            "[[ $(md5sum %(remote_path)s|awk {'print $1'}) == %(digest)s ]] && bash %(remote_path)s\n"
            "RETURN_CODE=$?\n"
# TODO            "rm -fr %(remote_path)s\n"
            "exit $RETURN_CODE" % context
        )
        channel = transport.open_session()
        channel.exec_command(cmd)
        
        # Log results
        logger.debug('%s running on %s' % (backend, server))
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
                log.save(update_fields=['stdout', 'stderr'])
                if channel.exit_status_ready():
                    break
        log.exit_code = exit_code = channel.recv_exit_status()
        log.state = BackendLog.SUCCESS if exit_code == 0 else BackendLog.FAILURE
        logger.debug('%s execution state on %s is %s' % (backend, server, log.state))
        log.save()
    except:
        log.state = BackendLog.ERROR
        log.traceback = ExceptionInfo(sys.exc_info()).traceback
        logger.error('Exception while executing %s on %s' % (backend, server))
        logger.debug(log.traceback)
        log.save()
    finally:
        if channel is not None:
            channel.close()
        if ssh is not None:
            ssh.close()


def Python(backend, log, server, cmds):
    from .models import BackendLog
    script = [ str(cmd.func.func_name) + str(cmd.args) for cmd in cmds ]
    script = json.dumps(script, indent=4).replace('"', '')
    log.script = '\n'.join([log.script, script])
    log.save(update_fields=['script'])
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
