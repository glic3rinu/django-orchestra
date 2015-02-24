import os

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from .. import settings


class WebalizerBackend(ServiceController):
    verbose_name = _("Webalizer")
    model = 'websites.Content'
    
    def save(self, content):
        context = self.get_context(content)
        self.append("mkdir -p %(webalizer_path)s" % context)
        self.append("[[ ! -e %(webalizer_path)s/index.html ]] && "
                    "echo 'Webstats are coming soon' > %(webalizer_path)s/index.html" % context)
        self.append("echo '%(webalizer_conf)s' > %(webalizer_conf_path)s" % context)
        self.append("chown %(user)s:www-data %(webalizer_path)s" % context)
    
    def delete(self, content):
        context = self.get_context(content)
        self.append("rm -fr %(webalizer_path)s" % context)
        self.append("rm %(webalizer_conf_path)s" % context)
    
    def get_context(self, content):
        conf_file = "%s.conf" % content.website.name
        context = {
            'site_logs': os.path.join(settings.WEBSITES_BASE_APACHE_LOGS, content.website.unique_name),
            'site_name': content.website.name,
            'webalizer_path': os.path.join(content.webapp.get_path(), content.website.name),
            'webalizer_conf_path': os.path.join(settings.WEBSITES_WEBALIZER_PATH, conf_file),
            'user': content.webapp.account.user,
            'banner': self.get_banner(),
        }
        context['webalizer_conf'] = (
            "# %(banner)s\n"
            "LogFile            %(site_logs)s\n"
            "LogType            clf\n"
            "OutputDir          %(webalizer_path)s\n"
            "HistoryName        webalizer.hist\n"
            "Incremental        yes\n"
            "IncrementalName    webalizer.current\n"
            "ReportTitle        Stats of\n"
            "HostName           %(site_name)s\n"
            "\n"
            "PageType       htm*\n"
            "PageType       php*\n"
            "PageType       shtml\n"
            "PageType       cgi\n"
            "PageType       pl\n"
            "\n"
            "DNSCache       /var/lib/dns_cache.db\n"
            "DNSChildren    15\n"
            "\n"
            "HideURL        *.gif\n"
            "HideURL        *.GIF\n"
            "HideURL        *.jpg\n"
            "HideURL        *.JPG\n"
            "HideURL        *.png\n"
            "HideURL        *.PNG\n"
            "HideURL        *.ra\n"
            "\n"
            "IncludeURL     *\n"
            "\n"
            "SearchEngine   yahoo.com       p=\n"
            "SearchEngine   altavista.com   q=\n"
            "SearchEngine   google.com      q=\n"
            "SearchEngine   eureka.com      q=\n"
            "SearchEngine   lycos.com       query=\n"
            "SearchEngine   hotbot.com      MT=\n"
            "SearchEngine   msn.com         MT=\n"
            "SearchEngine   infoseek.com    qt=\n"
            "SearchEngine   webcrawler      searchText=\n"
            "SearchEngine   excite          search=\n"
            "SearchEngine   netscape.com    search=\n"
            "SearchEngine   mamma.com       query=\n"
            "SearchEngine   alltheweb.com   query=\n"
            "\n"
            "DumpSites      yes\n"
        ) % context
        return context
