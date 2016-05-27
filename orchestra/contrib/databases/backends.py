import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace
from orchestra.contrib.resources import ServiceMonitor

from . import settings


class MySQLController(ServiceController):
    """
    Simple backend for creating MySQL databases using <tt>CREATE DATABASE</tt> statement.
    """
    verbose_name = "MySQL database"
    model = 'databases.Database'
    default_route_match = "database.type == 'mysql'"
    doc_settings = (settings,
        ('DATABASES_DEFAULT_HOST',)
    )
    
    def save(self, database):
        if database.type != database.MYSQL:
            return
        context = self.get_context(database)
        # Not available on delete()
        context['owner'] = database.owner
        self.append(textwrap.dedent("""
            # Create database and re-set permissions
            mysql -e 'CREATE DATABASE `%(database)s`;' || true
            mysql mysql -e 'DELETE FROM db WHERE db = "%(database)s";'\
            """) % context
        )
        for user in database.users.all():
            context.update({
                'username': user.username,
                'grant': 'WITH GRANT OPTION' if user == context['owner'] else ''
            })
            self.append(textwrap.dedent("""\
                mysql -e 'GRANT ALL PRIVILEGES ON `%(database)s`.* TO "%(username)s"@"%(host)s" %(grant)s;'\
                """) % context
            )
    
    def delete(self, database):
        if database.type != database.MYSQL:
            return
        context = self.get_context(database)
        self.append(textwrap.dedent("""
            # Remove database %(database)s
            mysql -e 'DROP DATABASE `%(database)s`;' || exit_code=$?
            mysql mysql -e 'DELETE FROM db WHERE db = "%(database)s";'\
            """) % context
        )
    
    def commit(self):
        self.append(textwrap.dedent("""
            # Apply permissions
            mysql -e 'FLUSH PRIVILEGES;'\
            """)
        )
        super(MySQLController, self).commit()
    
    def get_context(self, database):
        context = {
            'database': database.name,
            'host': settings.DATABASES_DEFAULT_HOST,
        }
        return replace(replace(context, "'", '"'), ';', '')


class MySQLUserController(ServiceController):
    """
    Simple backend for creating MySQL users using <tt>CREATE USER</tt> statement.
    """
    verbose_name = "MySQL user"
    model = 'databases.DatabaseUser'
    default_route_match = "databaseuser.type == 'mysql'"
    doc_settings = (settings,
        ('DATABASES_DEFAULT_HOST',)
    )
    
    def save(self, user):
        if user.type != user.MYSQL:
            return
        context = self.get_context(user)
        self.append(textwrap.dedent("""\
            # Create user %(username)s
            mysql -e 'CREATE USER "%(username)s"@"%(host)s";' || true # User already exists
            mysql -e 'UPDATE mysql.user SET Password="%(password)s" WHERE User="%(username)s";'\
            """) % context
        )
    
    def delete(self, user):
        if user.type != user.MYSQL:
            return
        context = self.get_context(user)
        self.append(textwrap.dedent("""
            # Delete user %(username)s
            mysql -e 'DROP USER "%(username)s"@"%(host)s";' || exit_code=$? \
            """) % context
        )
    
    def commit(self):
        self.append("# Apply permissions")
        self.append("mysql -e 'FLUSH PRIVILEGES;'")
    
    def get_context(self, user):
        context = {
            'username': user.username,
            'password': user.password,
            'host': settings.DATABASES_DEFAULT_HOST,
        }
        return replace(replace(context, "'", '"'), ';', '')


class MysqlDisk(ServiceMonitor):
    """
    <tt>du -bs &lt;database_path&gt;</tt>
    Implements triggers for resource limit exceeded and recovery, disabling insert and create privileges.
    """
    model = 'databases.Database'
    verbose_name = _("MySQL disk")
    delete_old_equal_values = True
    doc_settings = (settings,
        ('DATABASES_MYSQL_DB_DIR',)
    )
    mysql_db_dir = settings.DATABASES_MYSQL_DB_DIR
    
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
        super().prepare()
        context = {
            'mysql_db_dir': self.mysql_db_dir,
        }
        self.append(textwrap.dedent("""\
            function monitor_mysql () {
                { SIZE=$(du -bs "%(mysql_db_dir)s/$1") && echo $SIZE || echo 0; } | awk {'print $1'}
            }""") % context)
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
        self.append('echo %(db_id)s $(monitor_%(db_type)s "%(db_dirname)s")' % context)
    
    def get_context(self, db):
        context = {
            'db_name': db.name,
            'db_dirname': db.name.replace('-', '@003f'),
            'db_id': db.pk,
            'db_type': db.type,
        }
        return replace(replace(context, "'", '"'), ';', '')
