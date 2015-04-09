import os

from django.core.management.commands import makemessages

from orchestra.core.translations import ModelTranslation
from orchestra.utils.paths import get_site_dir


class Command(makemessages.Command):
    """ Provides database translations support """
    def handle(self, *args, **options):
        self.database_files = []
        try:
            if os.getcwd() == get_site_dir():
                self.generate_database_files()
            super(Command, self).handle(*args, **options)
        finally:
            self.remove_database_files()
    
    def get_contents(self):
        for model, fields in ModelTranslation._registry.items():
            for field in fields:
                contents = []
                for content in model.objects.values_list('id', field):
                    pk, value = content
                    contents.append(
                        (pk, "_(u'%s')" % value)
                    )
                if contents:
                    yield ('_'.join((model._meta.db_table, field)), contents)
    
    def generate_database_files(self):
        """
        Tmp files are generated because:
            1) having a nice gettext location
                # database_db_table_field.sql.py:id
            
            2) Django's makemessages will work with no modifications
        """
        for name, contents in self.get_contents():
            name = str(name)
            maximum = None
            content = {}
            for pk, value in contents:
                if not maximum or pk > maximum:
                    maximum = pk
                content[pk] = value
            tmpcontent = []
            for ix in range(maximum+1):
                tmpcontent.append(content.get(ix, ''))
            tmpcontent = '\n'.join(tmpcontent) + '\n'
            filename = 'database_%s.sql.py' % name
            self.database_files.append(filename)
            with open(filename, 'wb') as tmpfile:
                tmpfile.write(tmpcontent.encode('utf-8'))
    
    def remove_database_files(self):
        for path in self.database_files:
            os.unlink(path)
