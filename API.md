
=== Panel [application/vnd.orchestra.Panel+json] ===
A Panel represents a user's view of all accessible resources.
A "Panel" resource model contains the following fields:

uri                     URI         A GET against this URI refreshes the client representation of the resources accessible to this user.


=== VirtualHost [application/vnd.orchestra.VirtualHost+json] ===
#TODO: REST and dynamic attributes (resources, contacts)
A VirtualHost represents an Apache-like virtualhost configuration, which is useful for generating all the configuration files on the web server.
A VirtualHost resource model contains the following fields:

server_name             String
uri                     URI
contact                 Contact
ip                      String
port                    Number
domains                 String[]
document_root           String
custom_directives       String[]
fcgid_user              String
fcgid_group string      String
fcgid_directives        Object      Fcgid custom directives represented on a key/value pairs i.e. {'FcgidildeTimeout': 1202}
php_version             String
php_directives          Object      PHP custom directives represented on key/value pairs i.e. {'display_errors': 'True'}
resource_swap_current   Number
resource_swap_limit     Number
resource_cpu_current    Number
resource_cpu_limit      Number
....


=== Contact == [application/vnd.orchestra.Contact+json] ===
A Contact represents 

uri                     URI
name                    String      1
surname                 String      0..1
second_surname          String      0..1
national_id             String      1
type                    String      1
language                String      1
address                 String      1
city                    String      1
zipcode                 Number      1
province                String      1
country                 String      1
fax                     String      0..1
comments                String      0..1
emails                  String[]    1
phones                  String[]    1
billing_contact         Contact     0..1 #TODO: phone and emails for this contacts !!
technical_contact       Contact     0..1 #TODO: this contacts should be equal to Contact on Django models!
administrative_contact  Contact     0..1
payment_


