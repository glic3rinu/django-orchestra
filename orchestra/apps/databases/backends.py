import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from . import settings


class MySQLBackend(ServiceController):
    verbose_name = "MySQL database"
    model = 'databases.Database'
    
    def save(self, database):
        context = self.get_context(database)
        # Not available on delete()
        context['owner'] = database.owner
        self.append(
            "mysql -e 'CREATE DATABASE `%(database)s`;' || true" % context
        )
        # clean previous privileges
        self.append("""mysql mysql -e 'DELETE FROM db WHERE db = "%(database)s";'""" % context)
        for user in database.users.all():
            context.update({
                'username': user.username,
                'grant': 'WITH GRANT OPTION' if user == context['owner'] else ''
            })
            self.append(textwrap.dedent("""\
                mysql -e 'GRANT ALL PRIVILEGES ON `%(database)s`.* TO "%(username)s"@"%(host)s" %(grant)s;' \
                """ % context
            ))
    
    def delete(self, database):
        context = self.get_context(database)
        self.append("mysql -e 'DROP DATABASE `%(database)s`;'" % context)
        
    def commit(self):
        self.append("mysql -e 'FLUSH PRIVILEGES;'")
    
    def get_context(self, database):
        return {
            'database': database.name,
            'host': settings.DATABASES_DEFAULT_HOST,
        }


class MySQLUserBackend(ServiceController):
    verbose_name = "MySQL user"
    model = 'databases.DatabaseUser'
    
    def save(self, user):
        context = self.get_context(user)
        self.append(textwrap.dedent("""\
            mysql -e 'CREATE USER "%(username)s"@"%(host)s";' || true \
            """ % context
        ))
        self.append(textwrap.dedent("""\
            mysql -e 'UPDATE mysql.user SET Password="%(password)s" WHERE User="%(username)s";' \
            """ % context
        ))
    
    def delete(self, user):
        context = self.get_context(user)
        self.append(textwrap.dedent("""\
            mysql -e 'DROP USER "%(username)s"@"%(host)s";' \
            """ % context
        ))
    
    def commit(self):
        self.append("mysql -e 'FLUSH PRIVILEGES;'")
    
    def get_context(self, user):
        return {
            'username': user.username,
            'password': user.password,
            'host': settings.DATABASES_DEFAULT_HOST,
        }


class MysqlDisk(ServiceMonitor):
    model = 'databases.Database'
    verbose_name = _("MySQL disk")
    
    def exceeded(self, db):
        context = self.get_context(db)
        self.append(textwrap.dedent("""\
            mysql -e 'UPDATE db SET Insert_priv="N", Create_priv="N" WHERE Db="%(db_name)s";' \
            """ % context
        ))
    
    def recovery(self, db):
        context = self.get_context(db)
        self.append(textwrap.dedent("""\
            mysql -e 'UPDATE db SET Insert_priv="Y", Create_priv="Y" WHERE Db="%(db_name)s";' \
            """ % context
        ))
    
    def monitor(self, db):
        context = self.get_context(db)
        self.append(textwrap.dedent("""\
            echo %(db_id)s $(mysql -B -e '"
               SELECT sum( data_length + index_length ) "Size"
                  FROM information_schema.TABLES
                  WHERE table_schema = "gisp"
                  GROUP BY table_schema;' | tail -n 1) \
            """ % context
        ))
    
    def get_context(self, db):
        return {
            'db_name': db.name,
            'db_id': db.pk,
        }
