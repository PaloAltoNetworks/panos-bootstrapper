Bootstrap on Microsoft Azure
============================

Bootstrapper can build File Shares on Azure using custom bootstrap.xml and init-cfg templates. In order to
create files and folders, Bootstrapper needs your Storage Account Name and Storage Access Key. This information is never stored on
disk.

Finding your Access Key
-----------------------

To find your access key for Azure:

Use your Azure account email address and password to sign in to the `Azure Portal <https://portal.azure.com/>`_.

Choose a valid storage account from the Dashboard in the **resources** section

In the **settings** section, chose the **Access Keys** option.

Take note of the **Storage Account Name**

Copy either **key1** or **key2**.

.. Warning::
    An access key grants full programmatic access to your resources, meaning that it should be guarded as carefully as the root sign-in credentials for your account.


Next Steps
----------

Refer to the official documentation here: `Bootstrap the VM-Series Firewall in Azure <https://www.paloaltonetworks.com/documentation/80/virtualization/virtualization/bootstrap-the-vm-series-firewall/bootstrap-the-vm-series-firewall-in-azure.html>`_


.. Note::
    You may need to open a new browser window to follow links to external sites when viewing these docs in an embedded environment like Bootstrapper-UI