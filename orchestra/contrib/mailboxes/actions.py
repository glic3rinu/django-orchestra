from orchestra.admin.actions import SendEmail


class SendMailboxEmail(SendEmail):
    def get_queryset_emails(self):
        for mailbox in self.queryset.all():
            yield mailbox.get_local_address()
