from django import db


def close_connection(execute):
    """ Threads have their own connection pool, closing it when finishing """
    def wrapper(*args, **kwargs):
        try:
            log = execute(*args, **kwargs)
        except Exception as e:
            pass
        else:
            wrapper.log = log
        finally:
            db.connection.close()
    return wrapper


def get_settings(settings_file):
    """ get db settings from settings.py file without importing """
    settings = {'__file__': settings_file}
    with open(settings_file) as f:
        __file__ = 'rata'
        exec(f.read(), settings)
    settings = settings['DATABASES']['default']
    if settings['ENGINE'] not in  ('django.db.backends.sqlite3', 'django.db.backends.postgresql_psycopg2'):
        raise ValueError("%s engine not supported." % settings['ENGINE'])
    return settings


def get_connection(settings):
    if settings['ENGINE'] == 'django.db.backends.sqlite3':
        import sqlite3
        return sqlite3.connect(settings['NAME'])
    elif settings['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        import psycopg2
        return psycopg2.connect("dbname='{NAME}' user='{USER}' host='{HOST}' password='{PASSWORD}'".format(**settings))
    return conn


def run_query(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    return result
