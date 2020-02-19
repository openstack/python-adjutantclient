AdjutantClient is a command-line and python client for Adjutant.

Getting Started
===============

Adjutant Client can be installed from PyPI using pip:

::

    pip install python-openstackclient python-adjutantclient


The command line client is installed as a plugin for the OpenStack client.

Python API
==========

You can use the API with a keystone session:

  >>> from keystoneauth1 import session
  >>> from keystoneauth1.identity import v3
  >>> from adjutantclient.client import Client
  >>> auth = v3.Password(auth_url='http://keystone.host/v3',
                         username='user',
                         password='password',
                         project_name='demo',
                         user_domain_name='default',
                         project_domain_name='default')

  >>> sess = session.Session(auth=auth)
  >>> adjutant = Client('1', session=sess)

If you use a clouds.yaml file os_client_config can also be used:

  >>> import os_client_config
  >>> sess = os_client_config.make_rest_client('admin-logic')
  >>> adjutant = Client('1', session=sess)

A few of the endpoints (users.password_forgot(), token.submit(), signup, token.get()) don't require authentication.
In this case you can instead just pass an endpoint override to the adjutant client constructor.

  >>> from adjutantclient.client import Client
  >>> adjutant = Client('1', endpoint='http://adjutant.host/v1')
