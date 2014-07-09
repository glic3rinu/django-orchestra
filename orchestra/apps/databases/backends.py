from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from . import settings


class MySQLDBBackend(ServiceController):
    verbose_name = "MySQL database"
    model = 'databases.Database'
    
    def save(self, database):
        if database.type == database.MYSQL:
            context = self.get_context(database)
            self.append(
                "mysql -e 'CREATE DATABASE `%(database)s`;'" % context
            )
            self.append(
                "mysql -e 'GRANT ALL PRIVILEGES ON `%(database)s`.* "
                "  TO \"%(owner)s\"@\"%(host)s\" WITH GRANT OPTION;'" % context
            )
    
    def delete(self, database):
        if database.type == database.MYSQL:
            context = self.get_context(database)
            self.append("mysql -e 'DROP DATABASE `%(database)s`;'" % context)
        
    def commit(self):
        self.append("mysql -e 'FLUSH PRIVILEGES;'")
    
    def get_context(self, database):
        return {
            'owner': database.owner.username,
            'database': database.name,
            'host': settings.DATABASES_DEFAULT_HOST,
        }


class MySQLUserBackend(ServiceController):
    verbose_name = "MySQL user"
    model = 'databases.DatabaseUser'
    
    def save(self, database):
        if database.type == database.MYSQL:
            context = self.get_context(database)
            self.append(
                "mysql -e 'CREATE USER \"%(username)s\"@\"%(host)s\";'" % context
            )
            self.append(
                "mysql -e 'UPDATE mysql.user SET Password=\"%(password)s\" "
                "  WHERE User=\"%(username)s\";'" % context
            )
    
    def delete(self, database):
        if database.type == database.MYSQL:
            context = self.get_context(database)
            self.append(
                "mysql -e 'DROP USER \"%(username)s\"@\"%(host)s\";'" % context
            )
    
    def get_context(self, database):
        return {
            'username': database.username,
            'password': database.password,
            'host': settings.DATABASES_DEFAULT_HOST,
        }


class MySQLPermissionBackend(ServiceController):
    model = 'databases.UserDatabaseRelation'
    verbose_name = "MySQL permission"


class MysqlDisk(ServiceMonitor):
    model = 'database.Database'
    resource = ServiceMonitor.DISK
    verbose_name = _("MySQL disk")
