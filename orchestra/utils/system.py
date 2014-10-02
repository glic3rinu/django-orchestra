import errno
import fcntl
import getpass
import os
import re
import select
import subprocess
import sys

from django.core.management.base import CommandError


def check_root(func):
    """ Function decorator that checks if user has root permissions """
    def wrapped(*args, **kwargs):
        if getpass.getuser() != 'root':
            cmd_name = func.__module__.split('.')[-1]
            msg = "Sorry, '%s' must be executed as a superuser (root)"
            raise CommandError(msg % cmd_name)
        return func(*args, **kwargs)
    return wrapped


class _AttributeString(str):
    """ Simple string subclass to allow arbitrary attribute access. """
    @property
    def stdout(self):
        return str(self)


def make_async(fd):
    """ Helper function to add the O_NONBLOCK flag to a file descriptor """
    fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)


def read_async(fd):
    """
    Helper function to read some data from a file descriptor, ignoring EAGAIN errors
    """
    try:
        return fd.read()
    except IOError, e:
        if e.errno != errno.EAGAIN:
            raise e
        else:
            return ''


def run(command, display=True, error_codes=[0], silent=False, stdin=''):
    """ Subprocess wrapper for running commands """
    if display:
        sys.stderr.write("\n\033[1m $ %s\033[0m\n" % command)
    
    p = subprocess.Popen(command, shell=True, executable='/bin/bash',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
    p.stdin.write(stdin)
    p.stdin.close()
    
    make_async(p.stdout)
    make_async(p.stderr)
    
    stdout = str()
    stderr = str()
    
    # Async reading of stdout and sterr
    while True:
        # Wait for data to become available 
        select.select([p.stdout, p.stderr], [], [])
        
        # Try reading some data from each
        stdoutPiece = read_async(p.stdout)
        stderrPiece = read_async(p.stderr)
        
        if display and stdoutPiece:
            sys.stdout.write(stdoutPiece)
        if display and stderrPiece:
            sys.stderr.write(stderrPiece)
        
        stdout += stdoutPiece
        stderr += stderrPiece
        returnCode = p.poll()
        
        if returnCode != None:
            break
    
    out = _AttributeString(stdout.strip())
    err = _AttributeString(stderr.strip())
    p.stdout.close()
    p.stderr.close()
    
    out.failed = False
    out.return_code = returnCode
    out.stderr = err
    if p.returncode not in error_codes:
        out.failed = True
        msg = "\nrun() encountered an error (return code %s) while executing '%s'\n"
        msg = msg % (p.returncode, command)
        if display:
            sys.stderr.write("\n\033[1;31mCommandError: %s %s\033[m\n" % (msg, err))
        if not silent:
            raise CommandError("%s %s" % (msg, err))
    
    out.succeeded = not out.failed
    return out


def get_default_celeryd_username():
    """ Introspect celeryd defaults file in order to get its username """
    user = None
    try:
        with open('/etc/default/celeryd') as celeryd_defaults:
            for line in celeryd_defaults.readlines():
                if 'CELERYD_USER=' in line:
                    user = re.findall('"([^"]*)"', line)[0]
    finally:
        if user is None:
            raise CommandError("Can not find the default celeryd username")
    return user
