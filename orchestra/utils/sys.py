import errno
import fcntl
import getpass
import os
import re
import select
import subprocess
import sys
import time

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


def check_non_root(func):
    """ Function decorator that checks if user not has root permissions """
    def wrapped(*args, **kwargs):
        if getpass.getuser() == 'root':
            cmd_name = func.__module__.split('.')[-1]
            raise CommandError("Sorry, you don't want to execute '%s' as superuser (root)." % cmd_name)
        return func(*args, **kwargs)
    return wrapped


def confirm(msg):
    confirmation = input(msg)
    while True:
        if confirmation not in ('yes', 'no'):
            confirmation = input('Please enter either "yes" or "no": ')
            continue
        if confirmation == 'no':
            return False
        return True


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
        state.exit_code =  p.poll()
        state.command = command
        yield state
        
        if state.exit_code != None:
            p.stdout.close()
            p.stderr.close()
            raise StopIteration


def join(iterator, display=False, silent=False, valid_codes=(0,)):
    """ joins the iterator process """
    stdout = b''
    stderr = b''
    for state in iterator:
        stdout += state.stdout
        stderr += state.stderr
    
    exit_code = state.exit_code
    
    out = _Attribute(stdout.strip())
    err = stderr.strip()
    
    out.failed = False
    out.exit_code = exit_code
    out.stderr = err
    if exit_code not in valid_codes:
        out.failed = True
        msg = "\nrun() encountered an error (return code %s) while executing '%s'\n"
        msg = msg % (exit_code, state.command)
        if display:
            sys.stderr.write("\n\033[1;31mCommandError: %s %s\033[m\n" % (msg, err))
        if not silent:
            raise CommandError("%s %s" % (msg, err))
    
    out.succeeded = not out.failed
    return out


def joinall(iterators, **kwargs):
    results = []
    for iterator in iterators:
        out = join(iterator, **kwargs)
        results.append(out)
    return results


def run(command, display=False, valid_codes=(0,), silent=False, stdin=b'', async=False):
    iterator = runiterator(command, display, stdin)
    next(iterator)
    if async:
        return iterator
    return join(iterator, display=display, silent=silent, valid_codes=valid_codes)


def sshrun(addr, command, *args, executable='bash', persist=False, options=None, **kwargs):
    from .. import settings
    base_options = {
        'stricthostkeychecking': 'no',
        'BatchMode': 'yes',
        'EscapeChar': 'none',
    }
    if persist:
        base_options.update({
            'ControlMaster': 'auto',
            'ControlPersist': 'yes',
            'ControlPath': settings.ORCHESTRA_SSH_CONTROL_PATH,
        })
    base_options.update(options or {})
    options = ['%s=%s' % (k, v) for k, v in base_options.items()]
    options = ' -o '.join(options)
    user = kwargs.get('user', settings.ORCHESTRA_SSH_DEFAULT_USER)
    cmd = 'ssh -o {options} -C {user}@{addr} {executable}'.format(
        options=options, addr=addr, user=user, executable=executable)
    return run(cmd, *args, stdin=command.encode('utf8'), **kwargs)


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


def touch(fname, mode=0o666, dir_fd=None, **kwargs):
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(f.fileno() if os.utime in os.supports_fd else fname,
            dir_fd=None if os.supports_fd else dir_fd, **kwargs)


class OperationLocked(Exception):
    pass


class LockFile(object):
    """ File-based lock mechanism used for preventing concurrency problems """
    def __init__(self, lockfile, expire=5*60, unlocked=False):
        # /dev/shm/ can be a good place for storing locks
        self.lockfile = lockfile
        self.expire = expire
        self.unlocked = unlocked
    
    def acquire(self):
        if os.path.exists(self.lockfile):
            lock_time = os.path.getmtime(self.lockfile)
            # lock expires to avoid starvation
            if time.time()-lock_time < self.expire:
                return False
        touch(self.lockfile)
        return True
    
    def release(self):
        os.remove(self.lockfile)
    
    def __enter__(self):
        if not self.unlocked:
            if not self.acquire():
                raise OperationLocked("%s lock file exists and its mtime is less than %s seconds" %
                    (self.lockfile, self.expire))
        return True
    
    def __exit__(self, type, value, traceback):
        if not self.unlocked:
            self.release()


def touch_wsgi(delay=0):
    from . import paths
    run('{ sleep %i && touch %s/wsgi.py; } &' % (delay, paths.get_project_dir()), async=True)
