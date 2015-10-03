# Roadmap

Note `*` _for sustancial progress_


### 1.0a1 Milestone (first alpha release on ~~Oct '14~~ Apr '15)

1. [x] Automated deployment of the development environment
2. [x] Automated installation and upgrading
2. ~~[ ] Testing framework for running unittests and functional tests with LXC containers~~
2. [ ] Continuous integration with Jenkins
2. [x] Admin interface based on django.contrib.admin
3. [x] REST API for users
2. [x] [Orchestra-orm](https://github.com/glic3rinu/orchestra-orm) a Python library for easily interacting with Orchestra REST API
3. [x] Service orchestration framework
4. [x] Data model, crazy input validation, admin and REST interfaces, permissions, unit and functional tests, service management, migration scripts and documentation of:
    1. [x] PHP/static Web applications
    1. [x] Websites with Apache
    2. [x] FTP/rsync/scp/shell system accounts
    2. [x] Databases and database users with MySQL
    1. [x] Mail accounts, aliases, forwards with Postfix and Dovecot
    1. [x] DNS with Bind
    1. [x] Mailing lists with Mailman
1. [x] Contact management and service contraction
1. [ ] *Unittests of the bussines logic
2. [x] Functional tests of Admin UI and REST interations
1. [ ] Initial documentation


### 1.0b1 Milestone (first beta release on ~~Dec '14~~ Jun '15)

1. [x] Resource allocation and monitoring
1. [x] Order tracking
2. [x] Service definition framework, service plans and pricing
3. [ ] *Billing
    3. [x] Invoice
    3. [x] Membership fee
    3. [x] Amendment invoice
    3. [x] Amendment fee
    3. [x] Pro Forma
    3. [ ] *Advanced bill handling (move lines, undo billing, ...)
1. [x] Payment methods
  1. [x] SEPA Direct Debit
  2. [x] SEPA Credit Transfer
2. [ ] Additional services
    2. [ ] *VPS with Proxmox/OpenVZ
    2. [x] SaaS (Software as a Service) Gitlab/phpList/BSCW/Wordpress/Moodle/Drupal
    2. [x] Wordpress webapps
    3. [ ] uwsgi-emperor Python webapps
    2. [x] Miscellaneous services
2. [x] Issue tracking system


### 1.0 Milestone (first stable release on Sep '15)

1. [ ] Stabilize data model, internal APIs and REST API
3. [ ] Spanish and Catalan translations
1. [ ] Complete documentation for developers


### 2.0 Milestone (unscheduled)

1. [ ] Integration with third-party service providers, e.g. Gandi
2. [ ] Scheduling of service cancellations and deactivations
1. [ ] Object-level permission system
2. [ ] REST API functionality for superusers
3. [ ] Responsive user interface, based on a JS framework.
4. [ ] Full development documentation
5. [ ] [Ansible](http://www.ansible.com/home) orchestration method, which synchronizes the whole service config everytime instead of incremental changes.
