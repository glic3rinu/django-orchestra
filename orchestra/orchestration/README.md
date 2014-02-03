Orchestration
=============


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
