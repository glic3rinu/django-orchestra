from __future__ import unicode_literals

import re
import glob

import sys
import errno
import fcntl
import getpass
import os
import re
import select
import subprocess
import textwrap

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

def run(command, display=False, error_codes=[0], silent=False, stdin=''):
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
            raise AttributeError("%s %s %s" % (msg, err, out))
    
    out.succeeded = not out.failed
    return out



print "from orchestra.apps.accounts.models import Account"
print "from orchestra.apps.domains.models import Domain"
print "from orchestra.apps.webapps.models import WebApp"
print "from orchestra.apps.websites.models import Website, Content"


def print_webapp(context):
    print textwrap.dedent("""\
        try:
            webapp = WebApp.objects.get(account=account, name='%(name)s')
        except:"
            webapp = WebApp.objects.create(account=account, name='%(name)s', type='%(type)s')
        else:
            webapp.type = '%(type)s'
            webapp.save()"
        Content.objects.get_or_create(website=website, webapp=webapp, path='%(path)s')
        """ % context
    )


for conf in glob.glob('/etc/apache2/sites-enabled/*'):
    username = conf.split('/')[-1].split('.')[0]
    with open(conf, 'rb') as conf:
        print "account = Account.objects.get(username='%s')" % username
        for line in conf.readlines():
            line = line.strip()
            if line.startswith('<VirtualHost'):
                port = 80
                domains = []
                apps = []
                if line.endswith(':443>'):
                    port = 443
                wrapper_root = None
                webalizer = False
                webappname = None
            elif line.startswith("DocumentRoot"):
                __, path = line.split()
                webappname = path.rstrip('/').split('/')[-1]
                if webappname == 'public_html':
                    webappname = ''
            elif line.startswith("ServerName"):
                __, domain = line.split()
                sitename = domain
                domains.append("'%s'" % domain)
            elif line.startswith("ServerAlias"):
                for domain in line.split()[1:]:
                    domains.append("'%s'" % domain)
            elif line.startswith("Alias /fcgi-bin/"):
                __, __, wrapper_root = line.split()
            elif line.startswith('Action php-fcgi'):
                __, __, wrapper_name = line.split()
                wrapper_name = wrapper_name.split('/')[-1]
            elif line.startswith("Alias /webalizer"):
                webalizer = True
            elif line == '</VirtualHost>':
                if port == 443:
                    sitename += '-ssl'
                context = {
                    'sitename': sitename,
                    'port': port,
                    'domains': ', '.join(domains),
                }
                print textwrap.dedent("""\
                    # SITE"
                    website, __ = Website.objects.get_or_create(name='%(sitename)s', account=account, port=%(port)d)
                    for domain in [%(domains)s]:
                        try:
                            domain = Domain.objects.get(name=domain)
                        except:
                            domain = Domain.objects.create(name=domain, account=account)
                        else:
                            domain.account = account
                            domain.save()
                        website.domains.add(domain)
                    """ % context)
                if wrapper_root:
                    wrapper = os.join(wrapper_root, wrapper_name)
                    fcgid = run('grep "^\s*exec " %s' % wrapper).stdout
                    type = fcgid.split()[1].split('/')[-1].split('-')[0]
                    for option in fcgid.split('-d'):
                        print option
                    print_webapp({
                        'name': webappname,
                        'path': '/',
                        'type': type,
                    })
                if webalizer:
                    print_webapp({
                        'name': 'webalizer-%s' % sitename,
                        'path': '/webalizer',
                        'type': 'webalizer',
                    })
    print '\n'
