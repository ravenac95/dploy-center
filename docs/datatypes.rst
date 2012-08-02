Data Types
==========

The following is a list of data structures that are necessary for the
dploy-center.  Eventually this will be included in a single repository. For
now, this will suffice to keep some documentation. These data structures are
generally used in communication protocols. They should be language agnostic.

DeployRequest
-------------

Used to describe deployment jobs. These are sent to the DeployQueue.

Schema
~~~~~~

- broadcast_id: (str) a string composed of [random-uuid]:[commit]
- app: (str) app name
- archive_uri: (str) uri to a tar.gz of the app
- commit: (str) commit (hash|number)
- update_message: (str) message about the update
- metadata_version: (int) the metadata version to use. 0 means latest


BroadcastMessage
----------------

Used for broadcasting messages to the client

Schema
~~~~~~

- type: (str) *output* or *status*
- message: (dict) BroadcastOutputData or BroadcastStatusData

BroadcastOutputData Schema
^^^^^^^^^^^^^^^^^^^^^^^^^^

- type: (str) *line* or *raw*
- data: (str) output string

BroadcastStatusData Schema
^^^^^^^^^^^^^^^^^^^^^^^^^^

- type: (str) *error* or *completed*
- data: (str or null)


AppBuildAndDeployData
---------------------

Created by the AppService. It provides all the data needed to complete an app
build and deployment.

Schema
~~~~~~

- app_metadata_snapshot: (dict) the current AppMetadataSnapshot. *See Below*
- processes: (dict) a dict about this app's processes
    

AppBuildRequest
---------------

Used to describe app build jobs. These are sent to the BuildCenter.
They are created by processing DeployRequests.

Schema
~~~~~~

- app_metadata_snapshot: (dict) the current AppMetadataSnapshot. *See Below*
- archive_uri: (str) uri to a tar.gz file of the app's repository
- broadcast_descriptor: (dict) a BroadcastDescriptor *See Below*


AppMetadataSnapshot
-------------------

Used throughout different sections of the build process. It is also a major
component of the cargo file. These snapshots are also used to track versions of
a particular app.

Schema
~~~~~~

- release_version: (int) release version number
- app: (str) app name
- commit: (str) current commit (hash|number)
- env: (dict) current dict of environment variables. This is an EnvVars
  structure

BroadcastDescriptor
-------------------

Used in various sections to tell a service where to direct it's output.

Schema
~~~~~~

- uri: (str) broadcast uri
- id: (str) id for the broadcast


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
