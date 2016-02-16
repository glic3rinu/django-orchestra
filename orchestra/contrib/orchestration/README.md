# Orchestration

This module handles the management of the services controlled by Orchestra. This app provides the means for detecting changes on the data model and execute scripts on the servers to reflect those changes.

Orchestration module has the following pieces:

* `Operation` encapsulates an operation, storing the related object, the action and the backend
* `OperationsMiddleware` collects and executes all save and delete operations, more on [next section](#operationsmiddleware)
* `manager` it manage the execution of the operations
* `backends` defines the logic that will be executed on the servers in order to control a particular service
* `router` determines in which server an operation should be executed
* `Server` defines a server hosting services
* `methods` script execution methods, e.g. SSH
* `ScriptLog` it logs the script execution

Routes
======

This application provides support for mapping Orchestra service instances to server machines accross the network.

It supports _routing_ based on Python expression, which means that you can efectively
control services that are distributed accross several machines. For example, different
websites that are distributed accross _n_ web servers on a _shared hosting_
environment.

### OperationsMiddleware

`middlewares.OperationsMiddleware` automatically executes the service backends when a change on the data model occurs. The main steps that performs are:

1. Collect all `save` and `delete` model signals triggered on each HTTP request
2. Find related backends using the routing backend
3. Generate a single script per server (_unit of work_)
4. Execute the generated scripts on the servers via SSH


### Service Management Properties

We can identify three different characteristics regarding service management:

* **Authority**: Whether or not Orchestra is the only source of the service configuration. When Orchestra is the authority then service configuration is _completely generated_ from the Orchestra database (or services are configured to read their configuration directly from Orchestra database). Otherwise Orchestra will execute small tasks translating model changes into configuration changes, allowing manual configurations to be preserved.
* **Flow**: _push_, when Orchestra drives the execution or _pull_, when external services connects to Orchestra.
* **Execution**: _synchronous_, when the execution blocks the HTTP request, or _asynchronous_ when it doesn't. Asynchronous execution means concurrency, and concurrency scalability and complexity (i.e. reporting user feedback of success/failed backend executions).


### Registry vs Synchronization vs Task
From the above management properties we can extract three main service management strategies: (a) _task based management_, (b) _synchronization based management_ and (c) _registry based management_. Orchestra provides support for all of them, it is left to you to decide which one suits your requirements better.

Following a brief description and evaluation of the tradeoffs to help on your decision making.

#### a. Task Based Management (prefered)
This model refers when Orchestra is _not the only source of configuration_. Therefore, Orchestra translates isolated data model changes directly into localized changes on the service configuration, and executing them using a **push** strategy. For example `save()` or `delete()` object-level operations may have sibling configuration management operations. In contrast to _synchronization_, tasks are able to preserve configuration not performed by Orchestra.

This model is intuitive, efficient and also very consistent when tasks are execute **synchronously** with the request/response cycle. However, **asynchronous** task execution can have _consistency issues_; tasks have state, and this state can be lost when:
- A failure occur while applying some changes, e.g. network error or worker crash while deleting a service
- Scripts are executed out of order, e.g. create and delete a service is applied in inverse order

In general, _synchornous execution of tasks is preferred_ over asynchornous, unless response delays are not tolerable.


#### b. Synchronization Based Management
When Orchestra is the configuration **authority** and also _the responsible of applying the changes_ on the servers (**push** flow). The configuration files are **regenerated** every time by Orchestra, deleting any existing manual configuration. This model is very consistent since it only depends on the current state of the system (_memoryless_). Therefore, it makes sense to execute the synchronization operation in **asynchronous** fashion.

In contrast to registry based management, synchronization management is _fully centralized_, all the management operations are driven by Orchestra so you don't need to install nor configure anything on your servers.

#### c. Registry Based Management
When Orchestra acts as a pure **configuration registry (authority)**, doing nothing more than store service's configuration on the database. The configuration is **pulled** from Orchestra by the servers themselves, so it is **asynchronous** by nature.

This strategy considers two different implementations:

- The service is configured to read the configuration directly from Orchestra database (or REST API). This approach simplifies configuration management but also can make Orchestra a single point of failure on your architecture.
- An application (_agent_) periodically fetches the service configuration from the Orchestra database and regenerates the service configuration files. This approach is very tolerant to failures, since the services will keep working independenlty from orchestra, and the new configuration will be applied after recovering. A delay may occur until the changes are applied to the services (_eventual consistency_), but it can be mitigated by notifying the application when a relevant change occur. User feedback about the success or failure of appling the configuration needs to be implemented by the agent.

##### What state does actually mean?
Lets assume you have deleted a mailbox, and Orchestra has created an script that deletes that mailbox on the mail server. However a failure has occurred and the mailbox deletion task has been lost. Since the state has also been lost it is not easy to tell what to do now in order to maintain consistency.


### Additional Notes
* The script that manage the service needs to be idempotent, i.e. the outcome of running the script is always the same, no matter how many times it is executed.
* Renaming of attributes may lead to undesirable effects, e.g. changing a database name will create a new database rather than just changing its name.
* The system does not magically perform data migrations between servers when its _route_ has changed
