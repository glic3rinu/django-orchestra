import re
import glob


print "from orchestra.apps.accounts.models import Account"
print "from orchestra.apps.domains.models import Domain"
print "from orchestra.apps.webapps.models import WebApp"
print "from orchestra.apps.websites.models import Website, Content"


for conf in glob.glob('/etc/apache2/sites-enabled/*'):
    username = conf.split('/')[-1].split('.')[0]
    with open(conf, 'rb') as conf:
        print "account = Account.objects.get(user__username='%s')" % username
        for line in conf.readlines():
            line = line.strip()
            if line.startswith('<VirtualHost'):
                port = 80
                domains = []
                apps = []
                if line.endswith(':443>'):
                    port = 443
            elif line.startswith("ServerName"):
                domain = line.split()[1]
                name = domain
                domains.append("'%s'" % domain)
            elif line.startswith("ServerAlias"):
                for domain in line.split()[1:]:
                    domains.append("'%s'" % domain)
            elif line.startswith("Alias /fcgi-bin/"):
                fcgid = line.split('/')[-1] or line.split('/')[-2]
                fcgid = fcgid.split('-')[0]
                apps.append((name, fcgid, '/'))
            elif line.startswith("Alias /webalizer"):
                apps.append(('webalizer', 'webalizer', '/webalizer'))
            elif line == '</VirtualHost>':
                if port == 443:
                    name += '-ssl'
                print "# SITE"
                print "website, __ = Website.objects.get_or_create(name='%s', account=account, port=%d)" % (name, port)
                domains = ', '.join(domains)
                print "for domain in [%s]:" % str(domains)
                print "    try:"
                print "        domain = Domain.objects.get(name=domain)"
                print "    except:"
                print "        domain = Domain.objects.create(name=domain, account=account)"
                print "    else:"
                print "        domain.account = account"
                print "        domain.save()"
                print "    website.domains.add(domain)"
                print ""
                for name, type, path in apps:
                    print "try:"
                    print "    webapp = WebApp.objects.get(account=account, name='%s')" % name
                    print "except:"
                    print "    webapp = WebApp.objects.create(account=account, name='%s', type='%s')" % (name, type)
                    print "else:"
                    print "    webapp.type = '%s'" % type
                    print "    webapp.save()"
                    print ""
                    print "Content.objects.get_or_create(website=website, webapp=webapp, path='%s')" % path
    print '\n'
