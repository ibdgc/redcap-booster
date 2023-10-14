==============
REDCap Booster
==============

An API framework for developing external services for REDCap.


Installation
============

To run from the project folder::
    
    pip install -r requirements.txt
    uvicorn main:app --app-dir redcap_booster
    python redcap_booster/cli.py

To install and run in development environment::
    
    pip install -r requirements.txt
    pip install -e .
    uvicorn redcap_booster.main:app
    rbutils

To run in production environment::
    
    gunicorn --bind=192.168.0.112:8000 -w 4 -k uvicorn.workers.UvicornWorker --daemon redcap_booster.main:app

See https://www.uvicorn.org/deployment/ for more information on deployment
options.


Configuration
=============

To enable use with a specific REDCap project, the project ID must be listed in
your ``.env`` file, e.g.::

    pids = ["11659"]

Multiple project IDs can be listed, separated by commas. In addition, you need
to add to your ``.secrets`` folder a file named ``token_11659`` containing a
valid REDCap API token and a file named ``key_11659`` containing a
project-specific API key that can be generated in Python with::
    
    import secrets
    secrets.token_urlsafe(24)

Finally, within REDCap, under "Project Setup" click on the "Additional
customizations" button. Check "Data Entry Trigger" and enter the URL where the
API is available, e.g.::

    https://rcg.bsd.uchicago.edu/redcap-booster/?key=<api_key>

where <api_key> refers to the API key generated above.


Built-In Services
=================

ID Assignment
-------------

A service called ``id_gen`` is available for assigning unique IDs. To configure
this service, add the following to your ``.env`` file::

    id_gen = '{"db":"<database_file>"}'
    id_gen_11659 = '{"form_triggers":["<form_name>"], "id_field":"<field_name>"}'

and add a list of IDs to the database with::

    rbutils id-gen load-ids <filename>

This service can be easily reused and customized. For example, suppose you
want to inject a second piece of information into a REDCap project for which
you are already using ``id_gen``. To do this, create a new file named
``myservice.py`` containing the following::
    
    from redcap_booster.services import id_gen
    from redcap_booster.services.id_gen.db import DatabaseAccess
    from functools import partial
    
    service = 'my_service'
    db = DatabaseAccess(service)
    
    cli = id_gen.generate_cli(db, id_gen.commands)
    run = partial(id_gen.run, service=service, db=db)

and place this in a directory listed in the ``plugin_dirs`` setting. You may
then configure the new service as described above, and load the items to be
injected into the database via the ``rbutils`` command. If necessary, you may
even replace the entire ``run()`` function.
