from django.utils.translation import ugettext_lazy as _

from orchestra.orchestration import ServiceBackend

from . import settings


class MySQLBackend(ServiceBackend):
    name = 'MySQL'
    verbose_name = _("MySQL")
    model = 'webdatabases.WebDatabase'
    
    def save(self, database):
        context = self.get_context(database)
        self.append("mysql -e 'CREATE DATABASE `%(database)s`;'" % context)
        self.append("mysql -e 'CREATE USER \"%(username)s\"@\"%(host)s\""
                    "  IDENTIFIED BY \"%(password)s\";'" % context)
        self.append("mysql -e 'GRANT ALL PRIVILEGES ON `%(database)s`.* "
                    "  TO \"%(username)s\"@\"%(host)s\" WITH GRANT OPTION;'" % context)
    
    def delete(self, database):
        context = self.get_context(database)
        self.append("mysql -e 'DROP DATABASE `%(database)s`;'" % context)
        self.append("mysql -e 'DROP USER \"%(username)s\"@\"%(host)s\";'" % context)
    
    def commit(self):
        self.append("mysql -e 'FLUSH PRIVILEGES;'")
    
    def get_context(self, database):
        return {
            'database': database.name,
            'username': database.username,
            'password': database.password,
            'host': settings.WEBDATABASES_DEFAULT_HOST,
        }
