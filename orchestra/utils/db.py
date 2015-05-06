import sys

from django import db


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
        except Exception as e:
            raise
        else:
            wrapper.log = log
        finally:
            db.connection.close()
    return wrapper
