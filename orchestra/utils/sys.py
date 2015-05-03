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


class _Attribute(object):
    """ Simple string subclass to allow arbitrary attribute access. """
    def __init__(self, stdout):
        self.stdout = stdout


def make_async(fd):
    """ Helper function to add the O_NONBLOCK flag to a file descriptor """
    fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)


def read_async(fd):
    """
    Helper function to read some data from a file descriptor, ignoring EAGAIN errors
    """
    try:
        return fd.read()
    except IOError as e:
        if e.errno != errno.EAGAIN:
            raise e
        else:
            return ''


def runiterator(command, display=False, stdin=b''):
    """ Subprocess wrapper for running commands concurrently """
    if display:
        sys.stderr.write("\n\033[1m $ %s\033[0m\n" % command)
    
    p = subprocess.Popen(command, shell=True, executable='/bin/bash',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
    p.stdin.write(stdin)
    p.stdin.close()
    yield
    
    make_async(p.stdout)
    make_async(p.stderr)
    
    # Async reading of stdout and sterr
    while True:
        stdout = b''
        stderr = b''
        # Get complete unicode chunks
        select.select([p.stdout, p.stderr], [], [])
        
        stdoutPiece = read_async(p.stdout)
        stderrPiece = read_async(p.stderr)
        
        stdout += (stdoutPiece or b'')
        #.decode('ascii'), errors='replace')
        stderr += (stderrPiece or b'')
        #.decode('ascii'), errors='replace')
        
        if display and stdout:
            sys.stdout.write(stdout.decode('utf8'))
        if display and stderr:
            sys.stderr.write(stderr.decode('utf8'))
        
        state = _Attribute(stdout)
        state.stderr = stderr
        state.return_code =  p.poll()
        state.command = command
        yield state
        
        if state.return_code != None:
            p.stdout.close()
            p.stderr.close()
            raise StopIteration

def join(iterator, display=False, silent=False, error_codes=[0]):
    """ joins the iterator process """
    stdout = b''
    stderr = b''
    for state in iterator:
        stdout += state.stdout
        stderr += state.stderr
    
    return_code = state.return_code
    
    out = _Attribute(stdout.strip())
    err = stderr.strip()
    
    out.failed = False
    out.return_code = return_code
    out.stderr = err
    if return_code not in error_codes:
        out.failed = True
        msg = "\nrun() encountered an error (return code %s) while executing '%s'\n"
        msg = msg % (return_code, state.command)
        if display:
            sys.stderr.write("\n\033[1;31mCommandError: %s %s\033[m\n" % (msg, err))
        if not silent:
            raise CommandError("%s %s %s" % (msg, err, out))
    
    out.succeeded = not out.failed
    return out


def run(command, display=False, error_codes=[0], silent=False, stdin=b'', async=False):
    iterator = runiterator(command, display, stdin)
    next(iterator)
    if async:
        return iterator
    return join(iterator, display=display, silent=silent, error_codes=error_codes)


def sshrun(addr, command, *args, **kwargs):
    command = command.replace("'", """'"'"'""")
    cmd = "ssh -o stricthostkeychecking=no -C root@%s '%s'" % (addr, command)
    return run(cmd, *args, **kwargs)


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
