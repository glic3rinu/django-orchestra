#Orchestration


This module handles the server management of the services controlled by Orchestra.

Orchestration module has the following pieces:

* `Operation` encapsulates an operation, storing the related object, the action and the backend
* `collector` collects a bunch of operations into a _unit of work_, usually all operations triggered on the same request
* `manager` it manage the execution of the operations
* `backends` defines the logic that will be executed on the servers in order to control a particular service
* `router` determines in which server an operation should be executed
* `Server` defines a server hosting services
* `methods` script execution methods, e.g. SSH
* `ScriptLog` it logs the script execution

Execution steps:

1. Collect all `save` and `delete` model signals of an HTTP request
2. Find related daemon instances using the routing backend
3. Generate a single script per server (_unit of work_)
4. Send the task to Celery just before commiting the transacion to the DB, and make sure multiple script will execute in FIFO order (single worker per server)


### Task vs Synchronization
Orchestra considers two approaches for service management depending on the strategy used for reaching the current state: (a) _task based management_ and (b) _synchronization based management_.


#### a. Task Based Management
Isolated changes on the data model are directly translated to chanes on the related service configuration. For example `save` or `delete` object-level operations have sibiling configuration management operations. Tasks are driven by the Orchestra server using a _push_ strategy.

This model is intuitive and efficient, but it is prone to inconsistencies becuase tasks maintain state, and this state can be lost when:
- A failure occur while appling some changes, e.g. network error or worker crash while deleting a database
- Scripts are executed out of order, e.g. create and delete a database is applied in the inverse order


#### b. Synchronization Based Management
The entire service configuration is kept in sync with the server database, synchronization can be done periodically or triggered by a change on the data model. In contrast to tasks, here the full service configuration is **regenerated** every time. In general synchronization works more at "model" level, while tasks works at "object" level.

This model is not very efficient, but highly consistent, since the configuration is fully regenerated from the current state. Notice that Orchestra will act as the only configuration authority, _out of band_ configuration changes can be lost during synchronization.

Service management can be driven by both, Orchestra server or a client application that _pulls_ the current state via Orchestra's REST API.


#### Additional Notes
* The script that manage the service needs to be idepmpotent, i.e. the outcome of running the script is always the same, no matter how many times it is executed.

* Renaming of attributes may lead to undesirable effects, e.g. changing a database name will create a new database rather than just changing its name.

* The system does not manage data migrations between servers when the _route_ has changed
