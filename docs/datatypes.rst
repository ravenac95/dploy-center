Data Types
==========

The following is a list of data structures that are necessary for the
dploy-center.  Eventually this will be included in a single repository. For
now, this will suffice to keep some documentation. These data structures are
generally used in communication protocols. They should be language agnostic.

DeployOrder
-----------

Used to describe deployment jobs. These are sent to the DeployQueue.

Schema
~~~~~~

- app: (str) app name
- commit: (str) commit hash [optional]


AppBuildOrder
-------------

Used to describe app build jobs. These are sent to the BuildCenter. 
They are created by processing DeployOrders.

Schema
~~~~~~

- app_metadata_snapshot: (dict) an AppMetadataSnapshot. *See Below*
- git_uri: (str) uri to most recently used git server [optional]


AppMetadataSnapshot
-------------------

Used throughout different sections of the build process. It is also a major
component of the cargo file. These snapshots are also used to track versions of
a particular app.

Schema
~~~~~~

- app: (str) app name
- commit: (str) current commit hash
- env: (dict) current dict of environment variables. This is an EnvVars
  structure


EnvVars
-------

Dictionary of services and their environment variables. This is meant to be
persisted in some kind of database. 

Schema
~~~~~~

*service_name*: EnvDict

EnvDict
-------

A simple key/value storage for environment variables.


ZoneDeployOrder
---------------

Instructions for a dploy-zone to deploy an app given its cargo file.

Schema
~~~~~~

- app: (str) app name
- cargo_uri: (uri) uri to a downloadable cargo file


ZoneStopDeploy
--------------

Stop a set of running apps

Schema
~~~~~~

- apps: (list) list of app names to stop
