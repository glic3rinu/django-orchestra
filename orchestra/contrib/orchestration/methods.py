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

from orchestra.utils.python import CaptureStdout

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
    bscript = script.encode('utf-8')
    digest = hashlib.md5(bscript).hexdigest()
    path = os.path.join(settings.ORCHESTRATION_TEMP_SCRIPT_PATH, digest)
    remote_path = "%s.remote" % path
    log.script = '# %s\n%s' % (remote_path, script)
    log.save(update_fields=['script'])
    if not cmds:
        return
    channel = None
    ssh = None
    try:
        # Avoid "Argument list too long" on large scripts by genereting a file
        # and scping it to the remote server
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT, 0o600), 'wb') as handle:
            handle.write(bscript)
        
        # ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        addr = server.get_address()
        key = settings.ORCHESTRATION_SSH_KEY_PATH
        try:
            ssh.connect(addr, username='root', key_filename=key, timeout=10)
        except socket.error as e:
            logger.error('%s timed out on %s' % (backend, addr))
            log.state = log.TIMEOUT
            log.stderr = str(e)
            log.save(update_fields=['state', 'stderr'])
            return
        transport = ssh.get_transport()
        
        # Copy script to remote server
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(path, remote_path)
        sftp.chmod(remote_path, 0o600)
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
            second = False
            while True:
                # Non-blocking is the secret ingridient in the async sauce
                select.select([channel], [], [])
                if channel.recv_ready():
                    part = channel.recv(1024).decode('utf-8')
                    while part:
                        log.stdout += part
                        part = channel.recv(1024).decode('utf-8')
                if channel.recv_stderr_ready():
                    part = channel.recv_stderr(1024).decode('utf-8')
                    while part:
                        log.stderr += part
                        part = channel.recv_stderr(1024).decode('utf-8')
                log.save(update_fields=['stdout', 'stderr'])
                if channel.exit_status_ready():
                    if second:
                        break
                    second = True
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
        if log.state == log.STARTED:
            log.state = log.ABORTED
            log.save(update_fields=['state'])
        if channel is not None:
            channel.close()
        if ssh is not None:
            ssh.close()


def Python(backend, log, server, cmds, async=False):
    # TODO collect stdout?
    script = [ str(cmd.func.__name__) + str(cmd.args) for cmd in cmds ]
    script = json.dumps(script, indent=4).replace('"', '')
    log.script = '\n'.join([log.script, script])
    log.save(update_fields=['script'])
    try:
        for cmd in cmds:
            with CaptureStdout() as stdout:
                result = cmd(server)
            for line in stdout:
                log.stdout += line + '\n'
            if async:
                log.save(update_fields=['stdout'])
    except:
        log.exit_code = 1
        log.state = log.FAILURE
        log.traceback = ExceptionInfo(sys.exc_info()).traceback
        logger.error('Exception while executing %s on %s' % (backend, server))
    else:
        log.exit_code = 0
        log.state = log.SUCCESS
        logger.debug('%s execution state on %s is %s' % (backend, server, log.state))
    log.save()
