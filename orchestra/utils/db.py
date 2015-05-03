import ast

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
    settings = {}
    with open(settings_file, 'r') as handler:
        body = ast.parse(handler.read()).body
        for var in body:
            targets = getattr(var, 'targets', None)
            if targets and targets[0].id == 'DATABASES':
                keys = var.value.values[0].keys
                values = var.value.values[0].values
                for key, value in zip(keys, values):
                    if key.s == 'ENGINE':
                        if not 'postgresql' in value.s:
                            raise ValueError("%s engine not supported." % value)
                    settings[key.s] = getattr(value, 's', None)
                return settings


def get_connection(settings):
    import psycopg2
    conn = psycopg2.connect("dbname='{NAME}' user='{USER}' host='{HOST}' password='{PASSWORD}'".format(**settings))
    return conn


def run_query(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    return result
