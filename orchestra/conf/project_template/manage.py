#!/usr/bin/env python3
import os
import sys


if __name__ == "__main__":
    if sys.version_info < (3, 3):
        cmd = ' '.join(sys.argv)
        sys.stderr.write("Sorry, Orchestra requires at least Python 3.3, try with:\n$ python3 %s\n" % cmd)
        sys.exit(1)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
