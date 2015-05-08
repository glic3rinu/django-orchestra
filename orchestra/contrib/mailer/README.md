This is a simplified clone of [django-mailer](https://github.com/pinax/django-mailer).

Using `orchestra.contrib.mailer.backends.EmailBackend` as your email backend will have the following effects:
 * E-mails sent with Django's `send_mass_mail()` will be queued and sent by an out-of-band perioic task.
 * E-mails sent with Django's `send_mail()` will be sent right away by an asynchronous background task.
