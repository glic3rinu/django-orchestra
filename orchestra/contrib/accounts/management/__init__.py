import sys
import textwrap

from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError
from django.core.management import execute_from_command_line
from django.db import models


def create_initial_superuser(**kwargs):
    if '--noinput' not in sys.argv and '--fake' not in sys.argv and '--fake-initial' not in sys.argv:
        model = get_user_model()
        if not model.objects.filter(is_superuser=True).exists():
            sys.stdout.write(textwrap.dedent("""
                It appears that you just installed Accounts application.
                You can now create a superuser:
                
                """)
            )
            from ..models import Account
            try:
                Account.systemusers.field.related.model.objects.filter(account_id=1).exists()
            except FieldError:
                # avoid creating a systemuser when systemuser table is not ready
                Account.save = models.Model.save
            manager = sys.argv[0]
            execute_from_command_line(argv=[manager, 'createsuperuser'])
