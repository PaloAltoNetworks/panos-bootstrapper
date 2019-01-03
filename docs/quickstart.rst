Quickstart
==========


Docker
------

.. _Docker: https://docker.io

The fastest way to start this tool is using Docker_. New container images are built periodically and will always be up
to date.

.. code-block:: bash

    docker build -t panos_bootstrapper:v0.4 .
    docker run -p 5002:5000 -e PYTHONUNBUFFERED=0 nembery/panos_bootstrapper


Standalone
----------

For local development, start the tool directly using these commands:

.. code-block:: bash

    export FLASK_APP=./bootstrapper/bootstrapper.py
    flask run --host=0.0.0.0 --port=5002

This will start the API and listen on all interfaces on port 5002. Browsing to http://localhost:5002 will show the
OpenAPI 2.0 documentation.
