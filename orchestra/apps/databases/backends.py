from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from . import settings


class MySQLBackend(ServiceController):
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
    
    def save(self, user):
        if user.type == user.MYSQL:
            context = self.get_context(user)
            self.append(
                "mysql -e 'CREATE USER \"%(username)s\"@\"%(host)s\";' || true" % context
            )
            self.append(
                "mysql -e 'UPDATE mysql.user SET Password=\"%(password)s\" "
                "  WHERE User=\"%(username)s\";'" % context
            )
    
    def delete(self, user):
        if user.type == user.MYSQL:
            context = self.get_context(database)
            self.append(
                "mysql -e 'DROP USER \"%(username)s\"@\"%(host)s\";'" % context
            )
    
    def get_context(self, user):
        return {
            'username': user.username,
            'password': user.password,
            'host': settings.DATABASES_DEFAULT_HOST,
        }


class MySQLPermissionBackend(ServiceController):
    model = 'databases.UserDatabaseRelation'
    verbose_name = "MySQL permission"


class MysqlDisk(ServiceMonitor):
    model = 'databases.Database'
    verbose_name = _("MySQL disk")
    
    def exceeded(self, db):
        context = self.get_context(db)
        self.append("mysql -e '"
            "UPDATE db SET Insert_priv=\"N\", Create_priv=\"N\""
            "   WHERE Db=\"%(db_name)s\";'" % context
        )
    
    def recovery(self, db):
        context = self.get_context(db)
        self.append("mysql -e '"
            "UPDATE db SET Insert_priv=\"Y\", Create_priv=\"Y\""
            "   WHERE Db=\"%(db_name)s\";'" % context
        )
    
    def monitor(self, db):
        context = self.get_context(db)
        self.append(
            "echo %(db_id)s $(mysql -B -e '"
            "   SELECT sum( data_length + index_length ) \"Size\"\n"
            "      FROM information_schema.TABLES\n"
            "      WHERE table_schema=\"gisp\"\n"
            "      GROUP BY table_schema;' | tail -n 1)" % context
        )
    
    def get_context(self, db):
        return {
            'db_name': db.name,
            'db_id': db.pk,
        }
