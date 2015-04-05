from django.utils import timezone


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
