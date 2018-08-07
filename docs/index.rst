.. PanOS Bootstrapper Utility documentation master file, created by
   sphinx-quickstart on Mon Jul  9 09:56:26 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PanOS Bootstrapper Utility
==========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   bootstrap_aws
   bootstrap_azure
   usage
   testing


.. _here: https://www.paloaltonetworks.com/documentation/71/pan-os/newfeaturesguide/management-features/bootstrapping-firewalls-for-rapid-deployment
.. _GitHub: https://github.com
.. _panos-bootstrapper-ui: https://github.com/PaloAltoNetworks/panos-bootstrapper-ui
.. _PaloAltoNetworks: https://paloaltonetworks.slack.com


About
-----

The PanOS bootstrapper Utility is a tool to simplify the process of building bootstrap packages for
Palo Alto Networks Next-Gen Firewalls.

Complete documentation on the Palo Alto Networks NGFW bootstrapping process can be found here_.

An example web application is hosted on GitHub_ as the panos-bootstrapper-ui_.


Architecture
------------
This utility is provided as a micro-service that provides a simple API. It is expected that another application
will consume this API for presentation to the user.


Contributing
------------
Feel free to contribute templates, bug fixes, examples, documentation updates, etc to the GitHub repository.
For simple contributions, opening an issue on GitHub is the preferred method.
For more complex additions such as bugfixes, fork the project, commit your changes and open a Pull Request.
Questions can be posed to the #automation-bof channel in the PaloAltoNetworks_ slack channel.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`