Bootstrap on Amazon Web Services
================================

Bootstrapper can build S3 buckets on Amazon using custom bootstrap.xml and init-cfg templates. In order to
create files and folders, Bootstrapper needs your Access Key and Access Secret. This information is never stored on
disk.

Creating an AWS Access Key
---------------------------

To create an access key for your AWS account root user

Use your AWS account email address and password to sign in to the `AWS Management Console <https://console.aws.amazon.com/>`_ as the AWS account root user.

.. Note::
    If you previously signed in to the console with IAM user credentials, your browser might remember this preference and open your account-specific sign-in page. You cannot use the IAM user sign-in page to sign in with your AWS account root user credentials. If you see the IAM user sign-in page, choose Sign-in using root user credentials near the bottom of the page to return to the main sign-in page. From there, you can type your AWS account email address and password.

In the IAM navigation pane, choose Users.

Choose the name of the preferred user, and then choose the Security credentials tab.

If needed, expand the Access keys section.


Choose Create New Access Key. Then choose Download Key File to save the access key ID and secret access key to a file on your computer. After you close the dialog box, you can't retrieve this secret access key again.

.. Warning::
    A root access key grants full programmatic access to your resources, meaning that it should be guarded as carefully as the root sign-in credentials for your account.


Next Steps
----------

Refer to the official documentation here: |location_link|

.. |location_link| raw:: html
<a href="https://www.paloaltonetworks.com/documentation/80/virtualization/virtualization/bootstrap-the-vm-series-firewall/bootstrap-the-vm-series-firewall-in-aws.html" target="_blank">Bootstrap the VM-Series Firewall on AWS </a>
