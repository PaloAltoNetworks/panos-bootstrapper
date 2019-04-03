Managing Custom Bootstrap files
===============================


Creating a custom bootstrap.xml template
----------------------------------------

The panos-bootstrapper tool is designed to allow the use of custom bootstrap.xml and init-cfg.txt
templates. These should then be managed using a version control system like Git.

To create a bootstrap.xml template, configure a PAN-OS device to have the desired set of
features enabled, then export the configuration as an XML file.

Open the exported configuration in a text editor.

Find any items that should be customized during deployment and replace the value with a
jinja2 variable declaration. For example, to allow the hostname to be customized change the
hostname value in the XML file:

.. code-block:: bash

    <hostname>originalHostNameValue</hostname>


.. code-block:: bash

    <hostname>{{ hostname }}</hostname>


You will now have a single variable called 'hostname' that an operator can customize. Make a note
of all the variables created in this way.

You can use the bootstrapper API to save this template into the bootstrapper service directly, or you may
use another tool to compile this template and POST it to the service as a base64 encoded string. The presence
of the 'bootstrap_str' key in the payload indicates a fully compiled and encoded ootstrap.xml template.


Using the Panos-Bootstrapper-UI tool
------------------------------------

.. _here: https://github.com/PaloAltoNetworks/panos-bootstrapper-ui

You may also use the Bootstrapper UI tool provided here_. This tool allows you to store
custom bootstrap and init-cfg templates in a Git repository. Once you're templates are created,
you make them available to the bootstrapper-ui tool by creating a special configuration file
called a `.meta-cnc.yaml` file. This file instructs the UI tool which variables are available
to customize, the default values to use, and of what type they are.


Creating a .meta-cnc.yaml file
-------------------------------

.. _IronSkillet: https://github.com/PaloAltoNetworks/iron-skillet/blob/panos_v8.0/templates/panos/full/.meta-cnc.yaml

In this example, we will create a very simple configuration file for our template. We will only
include a single variable to brevity.

.. code-block:: yaml

    name: custom_bootstrap_xml
    label: Custom Bootstrap Template
    description: Sets the hostname only
    type: template

    labels:
      template_category: panos_full

    variables:
      - name: hostname
        description: Hostname
        default: panos-01
        type_hint: text

    snippets:
      - name: bootstrap.xml
        file: bootstrap.xml


A more complete example can be found in the IronSkillet_ repository.

This file can be saved anywhere in your git repository. Once this repository has been imported into the UI tool
it will immediately become available for use in bootstrap archives.


