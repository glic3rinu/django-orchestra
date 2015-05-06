from orchestra.admin.actions import SendEmail


class SendMailboxEmail(SendEmail):
    def get_email_addresses(self):
        for mailbox in self.queryset.all():
            yield mailbox.get_local_address()


class SendAddressEmail(SendEmail):
    def get_email_addresses(self):
        for address in self.queryset.all():
            yield address.email
