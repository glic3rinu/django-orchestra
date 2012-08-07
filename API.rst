=================================
 Orchestra REST API Specification
=================================

:Version: 0.1


Contents
--------

.. contents::
    :local:

Panel [application/vnd.orchestra.Panel+json]
============================================

A Panel represents a user's view of all accessible resources.
A "Panel" resource model contains the following fields:

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
uri                         URI          0..1        A GET against this URI refreshes the client representation of the resources accessible to this user.
==========================  ===========  ==========  ===========================


Contact [application/vnd.orchestra.Contact+json]
================================================

A Contact represents 

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
uri                         URI          1 
name                        String       1  
surname                     String       0..1   
second surname              String       0..1     
national id                 String       1         
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
phon es                     String[]     1     
billing contact             Contact      0..1  
technical contact           Contact      0..1    
administrative contact      Contact      0..1  
payment    
==========================  ===========  ==========  ===========================

TODO: phone and emails for this contacts
TODO: this contacts should be equal to Contact on Django models


User [application/vnd.orchestra.User+json]
==========================================

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
username                    String 
contact                     Contact 
password                    String 
first name                  String 
last name                   String 
email address               String 
active                      Boolean 
staff status                Boolean 
superuser status            Boolean 
groups                      Group 
user permissions            Permission[] 
last login                  String 
date joined                 String 
system user                 SystemUser 
virtual user                VirtualUser
==========================  ===========  ==========  ===========================


SystemUser [application/vnd.orchestra.SystemUser+json]
======================================================

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
user                        User 
user shell                  String 
user uid                    Number 
primary group               Group 
homedir                     String 
only ftp                    Boolean 
==========================  ===========  ==========  ===========================


VirtualUser [application/vnd.orchestra.VirtualUser+json]
========================================================

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
user                        User 
emailname                   String 
domain                      Name                     <VirtualDomain?>
home                        String 
==========================  ===========  ==========  ===========================

Zone [application/vnd.orchestra.Zone+json]
==========================================

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
origin                      String 
contact                     Contact 
primary ns                  String 
hostmaster email            String 
serial                      Number 
slave refresh               Number 
slave retry                 Number 
slave expiration            Number 
min caching time            Number 
records                     Object[]                 Domain record i.e. {'name': ('type', 'value') }
==========================  ===========  ==========  ===========================

Name [application/vnd.orchestra.Name+json]
==========================================
==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
name                        String 
contact                     Contact 
extension                   String 
register provider           String 
name server                 Object[]                 Name server key/value i.e. {'ns1.pangea.org': '1.1.1.1'}
virtual domain              Boolean                  <TODO: is redundant with virtual domain type?>
virtual domain type         String 
zone                        Zone 
==========================  ===========  ==========  ===========================

VirtualHost [application/vnd.orchestra.VirtualHost+json]
========================================================
<TODO: REST and dynamic attributes (resources, contacts)>
A VirtualHost represents an Apache-like virtualhost configuration, which is useful for generating all the configuration files on the web server.
A VirtualHost resource model contains the following fields:

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
server name                 String 
uri                         URI 
contact                     Contact 
ip                          String 
port                        Number 
domains                     Name[] 
document root               String 
custom directives           String[] 
fcgid user                  String 
fcgid group string          String 
fcgid directives            Object                   Fcgid custom directives represented on a key/value pairs i.e. {'FcgidildeTimeout': 1202}
php version                 String   
php directives              Object                   PHP custom directives represented on key/value pairs i.e. {'display errors': 'True'}
resource swap current       Number                   PHP custom directives represented on key/value pairs i.e. {'display errors': 'True'}
resource swap limit         Number                   PHP custom directives represented on key/value pairs i.e. {'display errors': 'True'}
resource cpu current        Number 
resource cpu limit          Number 
==========================  ===========  ==========  ===========================

Daemon [application/vnd.orchestra.Daemon+json]
==============================================

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
name                        String 
content type                String 
active                      Boolean 
save template               String 
save method                 String 
delete template             String 
delete method               String 
daemon instances            Object[]                 {'host': 'expression'}
==========================  ===========  ==========  ===========================

Monitor [application/vnd.orchestra.Monitor+json]
================================================

==========================  ===========  ==========  ===========================
**Name**                    **Type**     **Occurs**  **Description**
==========================  ===========  ==========  ===========================
daemon                      Daemon 
resource                    String 
monitoring template         String 
monitoring method           String 
exceed template             String                   <TODO: rename on monitor django model>
exceed method               String 
recover template            String 
recover method              String 
allow limit                 Boolean 
allow unlimit               Boolean 
default initial             Number 
block size                  Number 
algorithm                   String 
period                      String 
interval                    String       0..1
crontab                     String       0..1
==========================  ===========  ==========  ===========================

