import hashlib
import json
import logging
import os
import socket
import sys
import select

import paramiko
from celery.datastructures import ExceptionInfo
from django.conf import settings as djsettings

from . import settings


logger = logging.getLogger(__name__)

transports = {}


def SSH(backend, log, server, cmds, async=False):
    """
    Executes cmds to remote server using SSH
    
    The script is first copied using SCP in order to overflood the channel with large scripts
    Then the script is executed using the defined backend.script_executable
    """
    script = '\n'.join(cmds)
    script = script.replace('\r', '')
    digest = hashlib.md5(script).hexdigest()
    path = os.path.join(settings.ORCHESTRATION_TEMP_SCRIPT_PATH, digest)
    remote_path = "%s.remote" % path
    log.script = '# %s\n%s' % (remote_path, script)
    log.save(update_fields=['script'])
    if not cmds:
        return
    channel = None
    ssh = None
    try:
        logger.debug('%s is going to be executed on %s' % (backend, server))
        # Avoid "Argument list too long" on large scripts by genereting a file
        # and scping it to the remote server
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT, 0600), 'w') as handle:
            handle.write(script)
        
        # ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        addr = server.get_address()
        key = settings.ORCHESTRATION_SSH_KEY_PATH
        try:
            ssh.connect(addr, username='root', key_filename=key, timeout=10)
        except socket.error:
            logger.error('%s timed out on %s' % (backend, server))
            log.state = log.TIMEOUT
            log.save(update_fields=['state'])
            return
        transport = ssh.get_transport()
        
        # Copy script to remote server
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(path, remote_path)
        sftp.chmod(remote_path, 0600)
        sftp.close()
        os.remove(path)
        
        # Execute it
        context = {
            'executable': backend.script_executable,
            'remote_path': remote_path,
            'digest': digest,
            'remove': '' if djsettings.DEBUG else "rm -fr %(remote_path)s\n",
        }
        cmd = (
            "[[ $(md5sum %(remote_path)s|awk {'print $1'}) == %(digest)s ]] && %(executable)s %(remote_path)s\n"
            "RETURN_CODE=$?\n"
            "%(remove)s"
            "exit $RETURN_CODE" % context
        )
        channel = transport.open_session()
        channel.exec_command(cmd)
        
        # Log results
        logger.debug('%s running on %s' % (backend, server))
        if async:
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
        else:
            log.stdout += channel.makefile('rb', -1).read().decode('utf-8')
            log.stderr += channel.makefile_stderr('rb', -1).read().decode('utf-8')
        
        log.exit_code = exit_code = channel.recv_exit_status()
        log.state = log.SUCCESS if exit_code == 0 else log.FAILURE
        logger.debug('%s execution state on %s is %s' % (backend, server, log.state))
        log.save()
    except:
        log.state = log.ERROR
        log.traceback = ExceptionInfo(sys.exc_info()).traceback
        logger.error('Exception while executing %s on %s' % (backend, server))
        logger.debug(log.traceback)
        log.save()
    finally:
        if channel is not None:
            channel.close()
        if ssh is not None:
            ssh.close()


def Python(backend, log, server, cmds, async=False):
    # TODO collect stdout?
    script = [ str(cmd.func.func_name) + str(cmd.args) for cmd in cmds ]
    script = json.dumps(script, indent=4).replace('"', '')
    log.script = '\n'.join([log.script, script])
    log.save(update_fields=['script'])
    try:
        for cmd in cmds:
            result = cmd(server)
            log.stdout += str(result)
            if async:
                log.save(update_fields=['stdout'])
    except:
        log.exit_code = 1
        log.state = log.FAILURE
        log.traceback = ExceptionInfo(sys.exc_info()).traceback
    else:
        log.exit_code = 0
        log.state = log.SUCCESS
    log.save()
