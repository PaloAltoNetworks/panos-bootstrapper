Bootstrap on Google Compute Platform
====================================

Bootstrapper can build buckets on GCP using custom bootstrap.xml and init-cfg templates. In order to
create files and folders, Bootstrapper needs your OAuth Token and Project Id. This information is never stored on
disk.

Finding your Project Id
-----------------------

To find your project id and Oauth Token:

Use your GCP account email address and password to sign in to the `GCP Cloud Portal <https://console.cloud.google.com/>`_.

From the Cloud Console Home screen, the **Project ID** can be found on the **Project Info** widget.


Granting an OAuth Token API Access
-----------------------------------

In order to access the GCP APIs, Bootstrapper needs a valid OAuth Token. To generate an OAuth token:

Browse to the `OAuth Playground <https://developers.google.com/oauthplayground/>`_.

In Step 1: **Select & authorize APIs** scroll down to the **Cloud Storage JSON API v1**.

Click on the caret to open the **Cloud Storage JSON API v1** and highlight the **https://www.googleapis.com/auth/devstorage.read_write** option.

Click the **Authorize API** button.

This will open a **Choose Account** page. Select an appropriate Google Account.

Click the **Allow** button to grant access to the OAuth Playground.

You will be redirected back to the OAuth Playground with **Step 2** opened. Click the **Exchange authorization code for tokens** button.

Copy the value of the **Access Token** field. This token will only be valid for 1 hour.


.. Note::
    You may need to click on **Step 2** again to find the **Access Token** field. The OAuth playground will occassionally
    hide this option and open **Step 3**. **Step 3** is not needed for this application.


Next Steps
----------

Refer to the official documentation for bootstrapping a VM-Series firewall here: `Bootstrapping Workflow <https://www.paloaltonetworks.com/documentation/80/virtualization/virtualization/bootstrap-the-vm-series-firewall/vm-series-firewall-bootstrap-workflow.html>`_

.. Note::
    You may need to open a new browser window to follow links to external sites when viewing these docs in an embedded environment like Bootstrapper-UI