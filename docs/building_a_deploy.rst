Building a Deploy
=================

The definitive guide to building a pyinfra deploy:

.. contents::
    :local:


Layout
------

+ ``*.py`` - files that describe deploys
+ ``inventories/*.py`` - files that describe different inventories
+ ``group_data/*.py`` - files that describe data for groups
+ ``templates/*.jn2`` - templates used in the deploys
+ ``files/*`` - files used in the deploys
+ ``roles/*.py`` - files that describe role specific deploys
+ ``config.py`` - optional config and hooks


Inventory
---------

Inventory files contain groups of hosts. Groups are defined as a list or tuple of hosts.
For example, this inventory creates two groups, "app_servers" and "db_servers":

.. code:: python

    # inventories/production.py

    app_servers = [
        'app-1.net',
        'app-2.net'
    ]

    db_servers = [
        'db-1.net',
        'db-2.net',
        'db-3.net'
    ]

**In addition to the groups defined in the inventory, all the hosts are added to two more
groups: "all" and the name of the inventory file, in this case "production"**. Both can be
overriden by defining them in the inventory.


.. _data-ref-label:

Data
----

Data allows you to separate deploy variables from the deploy script. With data per host
and per group, you can easily build deploys that satisfy multiple environments.

Host Data
~~~~~~~~~

Arbitrary data can be assigned in the inventory and used at deploy-time. You just pass a
tuple ``(hostname, data)`` instead of just the hostname:

.. code:: python

    # inventories/production.py

    app_servers = [
        'app-1.net',
        ('app-2.net', {'some_key': True})
    ]

Group Data
~~~~~~~~~~

Group data files can be used to attach data to groups of host. They are placed in
``group_data/<group_name>.py``. This means ``group_data/all.py`` can be used to attach data
to all hosts (unless you override the "all" group).

Data files are just Python, all lowercase attributes not starting in ``_`` will be
included, eg:

.. code:: python

    # group_data/production.py

    app_user = 'myuser'
    app_dir = '/opt/myapp'

Authenticating with Data
~~~~~~~~~~~~~~~~~~~~~~~~

One of the most important use-cases for data is authenticating with the remote host. Instead
of passing ``--key``, ``--user``, etc to the CLI, or running a SSH agent, you can define
these details within host and group data. The attributes available:

.. code:: python

    ssh_port = 22
    ssh_user = 'ubuntu'
    ssh_key = '~/.ssh/some_key'
    ssh_key_password = 'password for key'
    # ssh_password = 'password auth is bad'

Data Hierarchy
~~~~~~~~~~~~~~

The same keys can be defined for host and group data - this means we can set a default in
*all.py* and override it on a group or host basis. When accessing data, the first match in
the following is returned:

+ "Override" data passed in via CLI args
+ Host data as defined in the inventory file
+ Normal group data
+ "all" group data

Debugging data issues:
    pyinfra contains a ``--debug-data`` option which can be used to explore the data output
    per-host for a given inventory/deploy.

Data Example
~~~~~~~~~~~~

Lets say you have an app that you wish to deploy in two environments: staging and
production, with the dev VM as the default. A good layout for this would be:

+ ``deploy.py``
+ ``inventories/production.py`` - production inventory
+ ``inventories/staging.py`` - staging inventory
+ ``group_data/all.py`` - shared data
+ ``group_data/production.py`` - production data
+ ``group_data/staging.py`` - staging data

The "all" group data contains any shared info and defaults:

.. code:: python

    # group_data/all.py

    env = 'dev'
    git_repo = 'https://github.com/Fizzadar/pyinfra'

And the production/staging data describe the differences:

.. code:: python

    # group_data/production.py

    env = 'production'
    git_branch = 'master'

.. code:: python

    # group_data/staging.py

    env = 'staging'
    git_branch = 'develop'


Operations
----------

Now that you've got an inventory of hosts and know how to auth with them, you can start
writing the deploy. This is described in a Python file normally situated in the top level
of the deploy directory.

In this file, eg ``deploy.py``, you import pyinfra **modules**. Each of these contains a
number of **operations**. You call these operations inside the deploy file, with arguments
describing remote state, and pyinfra uses this to run the deploy.

For example, this deploy will ensure that user "pyinfra" exists with home directory
"/home/pyinfra", and that the "/var/log/pyinfra.log" file exists and is owned by that user.

.. code:: python

    # deploy.py

    # Import pyinfra modules, each containing operations to use
    from pyinfra.modules import server, files

    # Ensure the state of a user
    server.user(
        'pyinfra',
        home='/home/pyinfra'
    )

    # Ensure the state of files
    files.file(
        '/var/log/pyinfra.log',
        user='pyinfra',
        group='pyinfra',
        permissions='644',
        sudo=True
    )

Uses the :doc:`server module <./modules/server>` and :doc:`files module <./modules/files>`.
You can see all the modules in :doc:`the modules index <./modules>`.

Naming operations:
    Pass a ``set`` object as the first argument to name the operation, which will appear
    during a deploy. By default the operation module, name and arguments are shown:

.. code:: python

    server.user(
        {'Ensure user pyinfra'},  # the contents of the set will become the op name
        'pyinfra',
        home='/home/pyinfra'
    )


Using Data
~~~~~~~~~~

Adding data to inventories was :ref:`described above <data-ref-label>` - you can access it
within a deploy on ``host.data``:

.. code:: python

    from pyinfra import host
    from pyinfra.modules import server

    # Ensure the state of a user based on host/group data
    server.user(
        host.data.app_user,
        home=host.data.app_dir
    )

String formatting:
    pyinfra supports jinja2 style string arguments, which should be used over Python's
    builtin string formatting where you expect the final string to change per host. This
    is because pyinfra groups operations by their arguments:

.. code:: python

    from pyinfra import host
    from pyinfra.modules import server

    server.user(
        host.data.app_user,
        '/opt/{{ host.data.app_dir }}'  # for multiple values of host.data.app_dir we still
                                        # generate a single operation
    )

Operation Meta
~~~~~~~~~~~~~~

Operation meta can be used during a deploy to change the desired operations:

.. code:: python

    from pyinfra.modules import server

    # Run an operation, collecting its meta output
    meta = server.user(
        'myuser'
    )

    # If we added a user above, do something extra
    if meta.commands:
        server.shell('# add server to sudo, etc...')

Facts
~~~~~

Facts allow you to use information about the target host to change the operations you use.
A good example is switching between apt & yum depending on the Linux distribution. Like data,
facts are accessed on ``host.fact``:

.. code:: python

    from pyinfra import host
    from pyinfra.modules import apt, yum

    if host.fact.linux_distribution == 'CentOS':
        yum.packages(
            'nano',
            sudo=True
        )
    else:
        apt.packages(
            'nano',
            sudo=True
        )

Some facts also take a single argument, for example the ``directory`` or ``file`` facts.
The :doc:`facts index <./facts>` lists the available facts and their arguments.

Includes/Roles
~~~~~~~~~~~~~~

Roles can be used to break out deploy logic into multiple files. They can also be used to
limit the contained operations to a subset of hosts. Roles can be included using
``local.include``.

.. code:: python

    from pyinfra import local, inventory

    # Operations in this file will be added to all hosts
    local.include('roles/my_role.py')

    # Operations in this file will be added to the hosts in group "my_group"
    local.include('roles/limited_role.py', hosts=inventory.my_group)

See more in :doc:`patterns: groups & roles <./patterns/groups_roles>`.


Config
------

There are a number of configuration options for how deploys are managed. These can be
defined at the top of a deploy file, or in a ``config.py`` alongside the deploy file. See
:doc:`the full list of options & defaults <./apidoc/api_config>`.

.. code:: python

    # config.py or top of deploy.py

    # SSH connect timeout
    TIMEOUT = 1

    # Fail the entire deploy after 10% of hosts fail
    FAIL_PERCENT = 10

config.py advantage:
    When added to ``config.py``, these options will take affect when using pyinfra
    ``--fact`` or ``--run``.

Hooks
-----

Deploy hooks are executed by the CLI at various points during the deploy process. Like
config, they can be defined in a ``config.py`` or at the top of the deploy file:

+ ``before_connect``
+ ``before_facts``
+ ``before_deploy``
+ ``after_deploy``

These can be used, for example, to check the right branch before connecting or to build some clientside assets locally before fact gathering. Hooks all take ``data, state`` as
arguments:

.. code:: python

    # config.py or top of deploy.py

    from pyinfra import hook

    @hook.before_connect
    def my_callback(data, state):
        print('Before connect hook!')

To abort a deploy, a hook can raise a ``hook.Error`` which the CLI
will handle.

When executing commands locally inside a hook (ie ``webpack build``), you should always use
the ``pyinfra.local`` module:

.. code:: python

    @hook.before_connect
    def my_callback(data, state):
        # Check something local is correct, etc
        branch = local.shell('git rev-parse --abbrev-ref HEAD')
        app_branch = data.app_branch

        if branch != app_branch:
            # Raise hook.Error for pyinfra to handle
            raise hook.Error('We\'re on the wrong branch (want {0}, got {1})!'.format(
                branch, app_branch
            ))
