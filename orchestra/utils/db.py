import sys

from django import db
from django.conf import settings as djsettings


def running_syncdb():
    return 'migrate' in sys.argv or 'syncdb' in sys.argv or 'makemigrations' in sys.argv


def database_ready():
    return (
        not running_syncdb() and
        'setuppostgres' not in sys.argv and
        'test' not in sys.argv and
        # Celerybeat has yet to stablish a connection at AppConf.ready()
        'celerybeat' not in sys.argv and
        # Allow to run python manage.py without a database
        sys.argv != ['manage.py'] and '--help' not in sys.argv
    )


def close_connection(execute):
    """ Threads have their own connection pool, closing it when finishing """
    def wrapper(*args, **kwargs):
        try:
            log = execute(*args, **kwargs)
        except:
            raise
        else:
            wrapper.log = log
        finally:
            db.connection.close()
    return wrapper


class clone(object):
    """
    clone database in order to have fresh connections and make queries outside the current transaction
    
        with db.clone(model=BackendLog) as handle:
            log = BackendLog.objects.using(handle.target).create()
            log._state.db = handle.origin
    
    """
    def __init__(self, model=None, origin='', target=''):
        if model is not None:
            origin = db.router.db_for_write(model)
        self.origin = origin or db.DEFAULT_DB_ALIAS
        self.target = target or 'other_' + origin
    
    def __enter__(self):
        djsettings.DATABASES[self.target] = djsettings.DATABASES[self.origin]
        # Because db.connections.datases is a cached property
        self.old_connections = db.connections
        db.connections = db.utils.ConnectionHandler()
        return self
    
    def __exit__(self, type, value, traceback):
        db.connections[self.target].close()
        djsettings.DATABASES.pop(self.target)
        db.connections = self.old_connections
