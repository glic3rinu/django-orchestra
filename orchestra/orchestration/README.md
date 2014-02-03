#Orchestration


This module handles the server management of the services controlled by Orchestra.

Orchestration module has the following pieces:

* `Operation` encapsulates an operation, storing the object, the action and the backend
* `collector` collects a bunch of operations into a _unit of work_, usually all operations triggered on the same request
* `manager` it manage the execution of the operations
* `backends` defines the logic that will be executed on the servers in order to control a particular service
* `router` determines in which server an operation should be executed
* `Server` defines a server hosting services
* `methods` script execution methods, e.g. SSH
* `ScriptLog` it logs the script execution



Execution steps:

1. Collect all save and delete model signals of an HTTP request
2. Find related daemon instances using the routing backend
3. Generate per instance scripts
4. Send the task to Celery just before commiting the transacion to the DB Make sure Celery will execute the scripts in FIFO order (single process?)


### Task vs Synchronization
Orchestra considers two approaches for service configuration management:


#### Task based configuration management
Changes on the data model are translated to chanes on the service configuration. For example `save` or `delete` data operations have sibiling configuration management operations.

This model is intuitive and efficient, but it is prone to inconsistencies when:
- A failure occur while appling the configuration
- Scripts are executed out of order


#### Synchronization based configuration management
The configuration is kept in sync with the server database, in order to apply changes the full service configuration is **regenerated**.

This model is highly consistent since it keeps the servers synchronized with the data model:
- Changes on the server are deleted on synchronization
- Eventual consistency property, the system will eventualy apply the configuration even when temporary failures occur


#### Additional notes

The script that manage the services need to be idepmpotents, the outcome of running the same script multiple time has to be the same.

Renaming of attributes may lead to undesirable effects, i.e. rename a database name will create a new database rather than migrate its name.

If the service route changes the system does not manage data migrations between servers

