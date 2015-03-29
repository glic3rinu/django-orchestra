import os

from django.core.management.commands import makemessages

from orchestra.core.translations import ModelTranslation
from orchestra.utils.paths import get_site_root


class Command(makemessages.Command):
    """ Provides database translations support """
    
    def handle(self, *args, **options):
        do_database = os.getcwd() == get_site_root()
        self.generated_database_files = []
        if do_database:
            self.project_locale_path = get_site_root()
            self.generate_database_files()
        super(Command, self).handle(*args, **options)
        self.remove_database_files()
    
    def get_contents(self):
        for model, fields in ModelTranslation._registry.iteritems():
            contents = []
            for field in fields:
                for content in model.objects.values_list('id', field):
                    pk, value = content
                    contents.append(
                        (pk, u"_(u'%s')" % value)
                    )
                yield ('_'.join((model._meta.db_table, field)), contents)
    
    def generate_database_files(self):
        """ tmp files are generated because of having a nice gettext location """
        for name, contents in self.get_contents():
            name = unicode(name)
            maximum = None
            content = {}
            for pk, value in contents:
                if not maximum or pk > maximum:
                    maximum = pk
                content[pk] = value
            tmpcontent = []
            for ix in xrange(maximum+1):
                tmpcontent.append(content.get(ix, ''))
            tmpcontent = u'\n'.join(tmpcontent) + '\n'
            filepath = os.path.join(self.project_locale_path, 'database_%s.sql.py' % name)
            self.generated_database_files.append(filepath)
            with open(filepath, 'w') as tmpfile:
                tmpfile.write(tmpcontent.encode('utf-8'))
    
    def remove_database_files(self):
        for path in self.generated_database_files:
            os.unlink(path)
