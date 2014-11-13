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


class _AttributeUnicode(unicode):
    """ Simple string subclass to allow arbitrary attribute access. """
    @property
    def stdout(self):
        return unicode(self)


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
            return u''


def runiterator(command, display=False, error_codes=[0], silent=False, stdin=''):
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
    
    stdout = unicode()
    stderr = unicode()
    
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
        
        return_code = p.poll()
        state = _AttributeUnicode(stdoutPiece.decode("utf8"))
        state.stderr = stderrPiece.decode("utf8")
        state.return_code = return_code
        yield state
        
        if return_code != None:
            p.stdout.close()
            p.stderr.close()
            raise StopIteration


def run(command, display=False, error_codes=[0], silent=False, stdin='', async=False):
    iterator = runiterator(command, display, error_codes, silent, stdin)
    iterator.next()
    if async:
        return iterator
    
    stdout = ''
    stderr = ''
    for state in iterator:
        stdout += state.stdout
        stderr += state.stderr
    
    return_code = state.return_code
    
    out = _AttributeUnicode(stdout.strip())
    err = stderr.strip()
    
    out.failed = False
    out.return_code = return_code
    out.stderr = err
    if return_code not in error_codes:
        out.failed = True
        msg = "\nrun() encountered an error (return code %s) while executing '%s'\n"
        msg = msg % (p.returncode, command)
        if display:
            sys.stderr.write("\n\033[1;31mCommandError: %s %s\033[m\n" % (msg, err))
        if not silent:
            raise CommandError("%s %s %s" % (msg, err, out))
    
    out.succeeded = not out.failed
    return out


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
