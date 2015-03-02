import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from .. import settings


class WebalizerBackend(ServiceController):
    verbose_name = _("Webalizer")
    model = 'websites.Content'
    
    def save(self, content):
        context = self.get_context(content)
        self.append(textwrap.dedent("""\
            mkdir -p %(webalizer_path)s
            if [[ ! -e %(webalizer_path)s/index.html ]]; then
                echo 'Webstats are coming soon' > %(webalizer_path)s/index.html
            fi
            echo '%(webalizer_conf)s' > %(webalizer_conf_path)s
            chown %(user)s:www-data %(webalizer_path)s""" % context
        ))
    
    def delete(self, content):
        pass
        # TODO delete has to be done on webapp deleteion, not content deletion
#        context = self.get_context(content)
#        self.append("rm -fr %(webalizer_path)s" % context)
#        self.append("rm %(webalizer_conf_path)s" % context)
    
    def get_context(self, content):
        conf_file = "%s.conf" % content.website.unique_name
        context = {
            'site_logs': content.website.get_www_access_log_path(),
            'site_name': content.website.name,
            'webalizer_path': os.path.join(content.webapp.get_path(), content.website.name),
            'webalizer_conf_path': os.path.join(settings.WEBSITES_WEBALIZER_PATH, conf_file),
            'user': content.webapp.account.username,
            'banner': self.get_banner(),
        }
        context['webalizer_conf'] = textwrap.dedent("""\
            # %(banner)s
            LogFile            %(site_logs)s
            LogType            clf
            OutputDir          %(webalizer_path)s
            HistoryName        webalizer.hist
            Incremental        yes
            IncrementalName    webalizer.current
            ReportTitle        Stats of
            HostName           %(site_name)s
            
            PageType       htm*
            PageType       php*
            PageType       shtml
            PageType       cgi
            PageType       pl
            
            DNSCache       /var/lib/dns_cache.db
            DNSChildren    15
            
            HideURL        *.gif
            HideURL        *.GIF
            HideURL        *.jpg
            HideURL        *.JPG
            HideURL        *.png
            HideURL        *.PNG
            HideURL        *.ra
            
            IncludeURL     *
            
            SearchEngine   yahoo.com       p=
            SearchEngine   altavista.com   q=
            SearchEngine   google.com      q=
            SearchEngine   eureka.com      q=
            SearchEngine   lycos.com       query=
            SearchEngine   hotbot.com      MT=
            SearchEngine   msn.com         MT=
            SearchEngine   infoseek.com    qt=
            SearchEngine   webcrawler      searchText=
            SearchEngine   excite          search=
            SearchEngine   netscape.com    search=
            SearchEngine   mamma.com       query=
            SearchEngine   alltheweb.com   query=
            
            DumpSites      yes""" % context
        )
        return context
