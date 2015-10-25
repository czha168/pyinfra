pyinfra
=======

pyinfra automates service deployment. It does this by diffing the state of the server with the state defined in the deploy script. Deploys are asyncronous and highly performant. The inventory & deploy are managed with pure Python, allowing for near-infinite extendability.

pyinfra targets POSIX compatability and is currently tested against Ubuntu, Debian, CentOS
& OpenBSD.

.. toctree::
    :maxdepth: 1
    :caption: Using pyinfra

    quick_start
    building_a_deploy
    modules
    facts

.. toctree::
    :maxdepth: 1
    :caption: How pyinfra Works

    operations
    deploy_process
    conventions

.. toctree::
    :maxdepth: 1
    :caption: API Documentation

    api_example
    api_reference

Meta
----

+ :ref:`genindex`
+ :ref:`modindex`

.. toctree::
    :hidden:
    :caption: Elsewhere

    pyinfra's website <http://pyinfra.com>
    pyinfra on GitHub <http://github.com/Fizzadar/pyinfra>