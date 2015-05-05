from collections import defaultdict

from django.utils import timezone


class RecordStorage(object):
    """
    list-dict implementation for fast lookups of record types
    """
    
    def __init__(self, *args):
        self.records = list(*args)
        self.type = defaultdict(list)
    
    def __iter__(self):
        return iter(self.records)
    
    def append(self, record):
        self.records.append(record)
        self.type[record['type']].append(record)
    
    def insert(self, ix, record):
        self.records.insert(ix, record)
        self.type[record['type']].insert(ix, record)
    
    def by_type(self, type):
        return self.type[type]


def generate_zone_serial():
    today = timezone.now()
    return int("%.4d%.2d%.2d%.2d" % (today.year, today.month, today.day, 0))


def format_hostmaster(hostmaster):
    """
    The DNS encodes the <local-part> as a single label, and encodes the
    <mail-domain> as a domain name.  The single label from the <local-part>
    is prefaced to the domain name from <mail-domain> to form the domain
    name corresponding to the mailbox.  Thus the mailbox HOSTMASTER@SRI-
    NIC.ARPA is mapped into the domain name HOSTMASTER.SRI-NIC.ARPA.  If the
    <local-part> contains dots or other special characters, its
    representation in a master file will require the use of backslash
    quoting to ensure that the domain name is properly encoded.  For
    example, the mailbox Action.domains@ISI.EDU would be represented as
    Action\.domains.ISI.EDU.
    http://www.ietf.org/rfc/rfc1035.txt
    """
    name, domain = hostmaster.split('@')
    if '.' in name:
        name = name.replace('.', '\.')
    return "%s.%s." % (name, domain)
