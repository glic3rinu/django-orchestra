from django.utils.translation import ugettext_lazy as _

from orchestra.orchestration import ServiceBackend


class MySQLBackend(ServiceBackend):
    name = 'MySQL'
    verbose_name = _("MySQL")
    models = ['databases.Database']
    
    def save(self, database):
        context = self.get_context(database)
        self.append("mysql -c 'CREATE DATABASE \\\"%(name)s\\\";'" % context)
        self.append("mysql -c 'GRANT ALL PRIVILEGES ON \\\"%(database)s\\\""
                    "  TO \\\"%(username)s@%(host)s\\\""
                    "  IDENTIFIED BY \\\"$(password)s\\\";'" % context)
    
    def delete(self, database):
        context = self.get_context(database)
        self.append("mysql -c 'DROP DATABASE \\\"%(name)s\\\";'" % context)
    
    def commit(self):
        self.append("mysql -c 'FLUSH PRIVILEGES;'")
    
    def get_context(self, database):
        return {
            'name': database.name,
            'username': database.username,
            'password': database.password,
            'host': database.host,
        }
