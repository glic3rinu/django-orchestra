from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor


class MailmanBackend(ServiceController):
    verbose_name = "Mailman"
    model = 'lists.List'


class MailmanTraffic(ServiceMonitor):
    model = 'lists.List'
    resource = ServiceMonitor.TRAFFIC
    
    def process(self, output):
        for line in output.readlines():
            listname, value = line.strip().slpit()
    
    def monitor(self, mailinglist):
        self.append(
            "LISTS=$(grep -v 'post to mailman' /var/log/mailman/post"
            "  | grep size | cut -d'<' -f2 | cut -d'>' -f1 | sort | uniq"
            "  | while read line; do \n"
            "     grep \"$line\" post | head -n1 | awk {'print $8\" \"$11'}"
            "       | sed 's/size=//' | sed 's/,//'\n"
            "done)"
        )
        self.append(
            'SUBS=""\n'
            'while read LIST; do\n'
            '   NAME=$(echo "$LIST" | awk {\'print $1\'})\n'
            '   SIZE=$(echo "$LIST" | awk {\'print $2\'})\n'
            '   if [[ ! $(echo -e "$SUBS" | grep "$NAME") ]]; then\n'
            '       SUBS="${SUBS}${NAME} $(list_members "$NAME" | wc -l)\n"\n'
            '   fi\n'
            '   SUBSCRIBERS=$(echo -e "$SUBS" | grep "$NAME" | awk {\'print $2\'})\n'
            '   echo "$NAME $(($SUBSCRIBERS*$SIZE))"\n'
            'done <<< "$LISTS"'
        )
