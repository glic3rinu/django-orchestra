import datetime


def generate_zone_serial():
    today = datetime.date.today()
    return int("%.4d%.2d%.2d%.2d" % (today.year, today.month, today.day, 1))
