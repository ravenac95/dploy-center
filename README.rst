dployment-center - The build server for dploy
=============================================

This is the main controller for dploy. It builds dploy "cargo" files that are
used throughout dploy. Cargo contains all of the components needed to deploy
an application on dploy. It is essentially a squashfs of an overlay directory
for an LXC container plus meta data.

How it works (will work)
------------------------

1. The dployment-center receives notifications via a zeromq request socket from
   a git server. We are currently building a custom version of gitosis which
   will also be released.
2. Once a notification has been received the dployment-center returns a random
   key. This key is used by the custom gitosis application to monitor the
   output from the dployment-center on the status of the build.
3. A ``CargoBuilder`` process is spawned. This process is in charge of creating
   the ``.cargo`` file.
4. The cargo file is distributed to any dployment zones (application servers
   mostly).

Architecture Overview
---------------------

The dployment-center consists of two different servers:
- **Build Control Server**- This server receives notifications from gitosis
  processes. Anything from outside of the dployment-center comes through here
  first.
- **Broadcast Server** - This server publishes output from the CargoBuilders.
  The output is subscribed by any gitosis processes.

Configuring the server
----------------------

The configuration for dployment-center is loaded from a file name
``dployment-center.conf`` current directory unless otherwise specified. The
configuration file is very simple at this time. It contains one section that
specifies the sockets it binds to. Here's an example::
    
    [dployment-center]
    broadcast_socket = ipc:///var/lib/dploy/center-broadcast.sock
    request_socket = ipc:///var/lib/dploy/center-control.sock

Possible Usage
--------------

Running the server::
    
    $ dployment-center

Run the server as a daemon::
    
    $ dployment-center --daemon
