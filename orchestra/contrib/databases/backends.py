import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController
from orchestra.contrib.resources import ServiceMonitor

from . import settings


class MySQLBackend(ServiceController):
    verbose_name = "MySQL database"
    model = 'databases.Database'
    default_route_match = "database.type == 'mysql'"
    
    def save(self, database):
        if database.type != database.MYSQL:
            return
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
                """) % context
            )
    
    def delete(self, database):
        if database.type != database.MYSQL:
            return
        context = self.get_context(database)
        self.append("mysql -e 'DROP DATABASE `%(database)s`;' || exit_code=1" % context)
        self.append("mysql mysql -e 'DELETE FROM db WHERE db = \"%(database)s\";'" % context)
        
    def commit(self):
        self.append("mysql -e 'FLUSH PRIVILEGES;'")
        super(MySQLBackend, self).commit()
    
    def get_context(self, database):
        return {
            'database': database.name,
            'host': settings.DATABASES_DEFAULT_HOST,
        }


class MySQLUserBackend(ServiceController):
    verbose_name = "MySQL user"
    model = 'databases.DatabaseUser'
    default_route_match = "databaseuser.type == 'mysql'"
    
    def save(self, user):
        if user.type != user.MYSQL:
            return
        context = self.get_context(user)
        self.append(textwrap.dedent("""\
            mysql -e 'CREATE USER "%(username)s"@"%(host)s";' || true \
            """) % context
        )
        self.append(textwrap.dedent("""\
            mysql -e 'UPDATE mysql.user SET Password="%(password)s" WHERE User="%(username)s";' \
            """) % context
        )
    
    def delete(self, user):
        if user.type != user.MYSQL:
            return
        context = self.get_context(user)
        self.append(textwrap.dedent("""\
            mysql -e 'DROP USER "%(username)s"@"%(host)s";' \
            """) % context
        )
    
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
        if db.type != db.MYSQL:
            return
        context = self.get_context(db)
        self.append(textwrap.dedent("""\
            mysql -e 'UPDATE db SET Insert_priv="N", Create_priv="N" WHERE Db="%(db_name)s";'\
            """) % context
        )
    
    def recovery(self, db):
        if db.type != db.MYSQL:
            return
        context = self.get_context(db)
        self.append(textwrap.dedent("""\
            mysql -e 'UPDATE db SET Insert_priv="Y", Create_priv="Y" WHERE Db="%(db_name)s";'\
            """) % context
        )
        
    def prepare(self):
        super(MysqlDisk, self).prepare()
        self.append(textwrap.dedent("""\
            function monitor () {
                { du -bs "/var/lib/mysql/$1" || echo 0; } | awk {'print $1'}
            }"""))
        # Slower way
        #self.append(textwrap.dedent("""\
        #    function monitor () {
        #        mysql -B -e "
        #            SELECT IFNULL(sum(data_length + index_length), 0) 'Size'
        #            FROM information_schema.TABLES
        #            WHERE table_schema = '$1';
        #        " | tail -n 1
        #    }"""))
    
    def monitor(self, db):
        if db.type != db.MYSQL:
            return
        context = self.get_context(db)
        self.append('echo %(db_id)s $(monitor "%(db_name)s")' % context)
    
    def get_context(self, db):
        return {
            'db_name': db.name,
            'db_id': db.pk,
        }
