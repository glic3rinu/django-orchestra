DNS
===

This app implements functionality for managing domain names.

It is composed by three _subapplications_.


1. Zones
--------

This application manages the [zone files](http://en.wikipedia.org/wiki/Zone_file) 
of hosted domains.


2. Names
--------

This application manages all the domains that points to your organization servers,
these can be domains (or subdomains) that your DNS server is hosting, or domains
that other servers are hosting but are referencing your servers.

This application is usefult for other applications in order to reference to domain
names in a consistent way. For example the server names of a web server virtual host or the
virtual domains managed by a mail server.


3. Domain Registration
----------------------

This application acts as a broker between your infrastructure an a domain registrar.
