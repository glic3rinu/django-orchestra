from django import db


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
