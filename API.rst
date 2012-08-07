=================================
 Orchestra REST API Specification
=================================

:Version: 0.1

.. contents::
    :local:

Panel [application/vnd.orchestra.Panel+json]
============================================

A Panel represents a user's view of all accessible resources.
A "Panel" resource model contains the following fields:

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
uri                         URI          0..1        A GET against this URI refreshes the client representation of the resources accessible to this user.
==========================  ===========  ==========  ===========================


Contact [application/vnd.orchestra.Contact+json]
================================================

A Contact represents 

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
uri                         URI          1 
name                        String       1  
surname                     String       0..1   
second_surname              String       0..1     
national_id                 String       1         
type                        String       1     
language                    String       1    
address                     String       1        
city                        String       1      
zipcode                     Number       1  
province                    String       1        
country                     String       1       
fax                         String       0..1     
comments                    String       0..1   
emails                      String[]     1       
phones                      String[]     1     
billing_contact             Contact      0..1  
technical_contact           Contact      0..1    
administrative_contact      Contact      0..1  
payment    
==========================  ===========  ==========  ===========================

TODO: phone and emails for this contacts
TODO: this contacts should be equal to Contact on Django models


User [application/vnd.orchestra.User+json]
==========================================

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
username                    String
contact                     Contact
password                    String
first_name                  String
last_name                   String
email_address               String
active                      Boolean
staff_status                Boolean
superuser_status            Boolean
groups                      Group
user_permissions            Permission[]
last_login                  String
date_joined                 String
system_user                 SystemUser
virtual_user                VirtualUser
==========================  ===========  ==========  ===========================


SystemUser [application/vnd.orchestra.SystemUser+json]
======================================================

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
user                        User 
user_shell                  String 
user_uid                    Number 
primary_group               Group 
homedir                     String 
only_ftp                    Boolean 
==========================  ===========  ==========  ===========================


VirtualUser [application/vnd.orchestra.VirtualUser+json]
========================================================

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
user                        User 
emailname                   String 
domain                      Name                     <VirtualDomain?>
home                        String 
==========================  ===========  ==========  ===========================

Zone [application/vnd.orchestra.Zone+json]
==========================================

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
origin                      String 
contact                     Contact 
primary_ns                  String 
hostmaster_email            String 
serial                      Number 
slave_refresh               Number 
slave_retry                 Number 
slave_expiration            Number 
min_caching_time            Number 
records                     Object[]                 Domain record i.e. {'name': ('type', 'value') }
==========================  ===========  ==========  ===========================

Name [application/vnd.orchestra.Name+json]
==========================================
==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
name                        String 
contact                     Contact 
extension                   String 
register_provider           String 
name_server                 Object[]                 Name server key/value i.e. {'ns1.pangea.org': '1.1.1.1'}
virtual_domain              Boolean                  <TODO: is redundant with virtual domain type?>
virtual_domain_type         String 
zone                        Zone 
==========================  ===========  ==========  ===========================

VirtualHost [application/vnd.orchestra.VirtualHost+json]
========================================================
<TODO: REST and dynamic attributes (resources, contacts)>
A VirtualHost represents an Apache-like virtualhost configuration, which is useful for generating all the configuration files on the web server.
A VirtualHost resource model contains the following fields:

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
server_name                 String 
uri                         URI 
contact                     Contact 
ip                          String 
port                        Number 
domains                     Name[] 
document_root               String 
custom_directives           String[] 
fcgid_user                  String 
fcgid_group string          String 
fcgid_directives            Object                   Fcgid custom directives represented on a key/value pairs i.e. {'FcgidildeTimeout': 1202}
php_version                 String   
php_directives              Object                   PHP custom directives represented on key/value pairs i.e. {'display errors': 'True'}
resource_swap_current       Number                   PHP custom directives represented on key/value pairs i.e. {'display errors': 'True'}
resource_swap_limit         Number                   PHP custom directives represented on key/value pairs i.e. {'display errors': 'True'}
resource_cpu_current        Number 
resource_cpu_limit          Number 
==========================  ===========  ==========  ===========================

Daemon [application/vnd.orchestra.Daemon+json]
==============================================

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
name                        String 
content_type                String 
active                      Boolean 
save_template               String 
save_method                 String 
delete_template             String 
delete_method               String 
daemon_instances            Object[]                 {'host': 'expression'}
==========================  ===========  ==========  ===========================

Monitor [application/vnd.orchestra.Monitor+json]
================================================

==========================  ===========  ==========  ===========================
**Field name**              **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
daemon                      Daemon 
resource                    String 
monitoring_template         String 
monitoring method           String 
exceed_template             String                   <TODO: rename on monitor django model>
exceed_method               String 
recover_template            String 
recover_method              String 
allow_limit                 Boolean 
allow_unlimit               Boolean 
default_initial             Number 
block_size                  Number 
algorithm                   String 
period                      String 
interval                    String       0..1
crontab                     String       0..1
==========================  ===========  ==========  ===========================

