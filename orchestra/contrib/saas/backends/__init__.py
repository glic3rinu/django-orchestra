import pkgutil
import textwrap

from orchestra.contrib.resources import ServiceMonitor

from .. import settings


class ApacheTrafficByHost(ServiceMonitor):
    """
    Parses apache logs,
    looking for the size of each request on the last word of the log line.
    
    Compatible log format:
    <tt>LogFormat "%h %l %u %t \"%r\" %>s %O %{Host}i" host</tt>
    or if include_received_bytes:
    <tt>LogFormat "%h %l %u %t \"%r\" %>s %I %O %{Host}i" host</tt>
    <tt>CustomLog /home/pangea/logs/apache/host_blog.pangea.org.log host</tt>
    """
    model = 'saas.SaaS'
    script_executable = '/usr/bin/python'
    monthly_sum_old_values = True
    abstract = True
    include_received_bytes = False
    
    def prepare(self):
        access_log = self.log_path
        context = {
            'access_logs': str((access_log, access_log+'.1')),
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'ignore_hosts': str(settings.SAAS_TRAFFIC_IGNORE_HOSTS),
            'include_received_bytes': str(self.include_received_bytes),
        }
        self.append(textwrap.dedent("""\
            import sys
            from datetime import datetime
            from dateutil import tz
            
            def to_local_timezone(date, tzlocal=tz.tzlocal()):
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
                date = date.replace(tzinfo=tz.tzutc())
                date = date.astimezone(tzlocal)
                return date
            
            # Use local timezone
            end_date = to_local_timezone('{current_date}')
            end_date = int(end_date.strftime('%Y%m%d%H%M%S'))
            access_logs = {access_logs}
            sites = {{}}
            months = {{
                'Jan': '01',
                'Feb': '02',
                'Mar': '03',
                'Apr': '04',
                'May': '05',
                'Jun': '06',
                'Jul': '07',
                'Aug': '08',
                'Sep': '09',
                'Oct': '10',
                'Nov': '11',
                'Dec': '12',
            }}
            
            def prepare(object_id, site_domain, ini_date):
                global sites
                ini_date = to_local_timezone(ini_date)
                ini_date = int(ini_date.strftime('%Y%m%d%H%M%S'))
                sites[site_domain] = [ini_date, object_id, 0]
            
            def monitor(sites, end_date, months, access_logs):
                include_received = {include_received_bytes}
                for access_log in access_logs:
                    try:
                        with open(access_log, 'r') as handler:
                            for line in handler.readlines():
                                line = line.split()
                                host, __, __, date = line[:4]
                                if host in {ignore_hosts}:
                                    continue
                                size, hostname = line[-2:]
                                size = int(size)
                                if include_received:
                                    size += int(line[-3])
                                try:
                                    site = sites[hostname]
                                except KeyError:
                                    continue
                                else:
                                    # [16/Sep/2015:11:40:38
                                    day, month, date = date[1:].split('/')
                                    year, hour, min, sec = date.split(':')
                                    date = year + months[month] + day + hour + min + sec
                                    if site[0] < int(date) < end_date:
                                        site[2] += size
                    except IOError as e:
                        sys.stderr.write(str(e)+'\\n')
                for opts in sites.values():
                    ini_date, object_id, size = opts
                    sys.stdout.write('%s %s\\n' % (object_id, size))
            """).format(**context)
        )
    
    def monitor(self, saas):
        context = self.get_context(saas)
        self.append("prepare(%(object_id)s, '%(site_domain)s', '%(last_date)s')" % context)
    
    def commit(self):
        self.append('monitor(sites, end_date, months, access_logs)')
    
    def get_context(self, saas):
        return {
            'site_domain': saas.get_site_domain(),
            'last_date': self.get_last_date(saas.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'object_id': saas.pk,
        }


class ApacheTrafficByName(ApacheTrafficByHost):
    __doc__ = ApacheTrafficByHost.__doc__
    
    def get_context(self, saas):
        return {
            'site_domain': saas.name,
            'last_date': self.get_last_date(saas.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'object_id': saas.pk,
        }


for __, module_name, __ in pkgutil.walk_packages(__path__):
    # sorry for the exec(), but Import module function fails :(
    exec('from . import %s' % module_name)
