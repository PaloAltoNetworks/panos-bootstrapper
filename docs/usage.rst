Using the API
=============

API documentation is included in OpenAPI (currently swagger 2.0) format. A simple swagger API viewer is included
in the root directory by browsing to http://bootstrapper_host:5000/, where bootstrapper_host is the host where
the bootstrapper service is running.

Some examples are given below:

List available templates
------------------------

.. code-block:: bash

    local:~ operator$ curl  http://localhost:5000/list_templates | python -m json.tool
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100   458  100   458    0     0  39031      0 --:--:-- --:--:-- --:--:-- 41636
    {
        "status_code": 200,
        "success": true,
        "templates": [
            {
                "description": "No Bootstrap.xml Required",
                "name": "None",
                "type": "bootstrap"
            },
            {
                "description": "Default Bootstrap template",
                "name": "Default Bootstrap.xml",
                "type": "bootstrap"
            },
            {
                "description": "Imported Template",
                "name": "GKE_Bootstrap",
                "type": "bootstrap"
            },
            {
                "description": "Imported Template",
                "name": "VMWare_Bootstrap",
                "type": "bootstrap"
            },
            {
                "description": "Imported Template",
                "name": "AWS_Bootstrap",
                "type": "bootstrap"
            }
        ]
    }

List Init-Cfg Templates
-----------------------

.. code-block:: bash

    local:~ operator$ curl  http://localhost:5000/list_init_cfg_templates | python -m json.tool
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100   413  100   413    0     0  30134      0 --:--:-- --:--:-- --:--:-- 31769
    {
        "status_code": 200,
        "success": true,
        "templates": [
            {
                "description": "Init-Cfg with static management IP addresses",
                "name": "init-cfg-static.txt",
                "type": "init-cfg"
            },
            {
                "description": "Init-Cfg with DHCP Assigned IP addresses",
                "name": "Default Init-Cfg DHCP",
                "type": "init-cfg"
            },
            {
                "description": "",
                "name": "init-cfg-hostname",
                "type": "init-cfg"
            },
            {
                "description": "",
                "name": "working-init-cfg-hostname-only-dhcp",
                "type": "init-cfg"
            }
        ]
    }

Show the contents of a template
-------------------------------
.. code-block:: bash

    local:~ operator$ curl -X POST -d '{"template_name": "init-cfg-hostname"}'  http://localhost:5000/get_template
    type=dhcp
    ip-address=
    default-gateway=
    netmask=
    hostname={{ hostname }}
    dns-primary=
    panorama-server=
    dgname=
    tplname=

This template only defines one variable. In this case `hostname` is declared as a variable. To use this template in a
bootstrap package, you must supply a `hostname` variable to the `generate_bootstrap_package` API.

To show required variables in a set of templates
------------------------------------------------

.. code-block:: bash

    local:~ operator$ curl -X POST -d '{"init_cfg_template": "init-cfg-hostname"}'  http://localhost:5000/get_bootstrap_variables | python -m json.tool
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100   188  100   146  100    42  11718   3371 --:--:-- --:--:-- --:--:-- 12166
    {
        "payload": {
            "archive_type": "iso",
            "deployment_type": "kvm",
            "hostname": "",
            "init_cfg_template": "init-cfg-hostname"
        },
        "status_code": 200,
        "success": true
    }

This example uses the `get_bootstrap_variables` API to return the required payload for the desired templates. In this
case, the keys listed in the payload dictionary will be required to build a bootstrap package using only the `init-cfg-hostname`
template.

Building a bootstrap package
----------------------------

.. code-block:: bash

    curl -X POST -d '{ "archive_type": "iso", "deployment_type": "kvm", "hostname": "NGFW-001", "init_cfg_template": "init-cfg-hostname"}'  http://localhost:5000/generate_bootstrap_package -o NGFW.iso
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100  380k  100  380k  100   116  10.6M   3319 --:--:-- --:--:-- --:--:-- 10.9M
    local:~ operator$ hdiutil mount NGFW.iso
    /dev/disk7          	                               	/Volumes/bootstrap 5
    local:~ operator$ cd /Volumes/bootstrap\ 5/
    local:bootstrap 5 operator$ ls
    config		content		license		software
    local:bootstrap 5 operator$ cd config/
    local:config operator$ ls
    init-cfg.txt
    local:config operator$ cat init-cfg.txt
    type=dhcp
    ip-address=
    default-gateway=
    netmask=
    hostname=NGFW-001
    dns-primary=
    panorama-server=
    dgname=
    tplname=
    vm-auth-key=

In this example, we took the output of the `get_bootstrap_variables` API call, entered our desired `hostname`
(NGFW-001 in this case) and POSTed that information to the `generate_bootstrap_package` API. This returned an ISO image
with the desired init-cfg template compiled with our variables. Attaching this ISO to a factory default PanOS firewall
will result in the firewall booting up with the NGFW-001 hostname configured at boot. f


Building a Bootstrap Package with a custom bootstrap.xml
--------------------------------------------------------

In the previous example, we only built a package that included the init-cfg.txt file. However, you can also include
a complete firewall configuration using a `bootstrap.xml` file.


Once again, let's get all required variables for our selected templates:
*note that we've included a `bootstrap_template` parameters with the value of a bootstrap template name.

.. code-block:: bash

    local:curl -X POST -d '{"init_cfg_template": "Default Init-Cfg DHCP", "bootstrap_template": "Default Bootstrap.xml"}'  http://localhost:5000/get_bootstrap_variables | python -m json.tool
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100   438  100   345  100    93  19049   5135 --:--:-- --:--:-- --:--:-- 19166
    {
        "payload": {
            "archive_type": "iso",
            "bootstrap_template": "Default Bootstrap.xml",
            "default_next_hop": "",
            "deployment_type": "kvm",
            "ethernet1_1_profile": "",
            "ethernet2_1_profile": "",
            "hostname": "",
            "init_cfg_template": "Default Init-Cfg DHCP",
            "management_gateway": "",
            "management_ip": "",
            "management_mask": "",
            "timezone": ""
        },
        "status_code": 200,
        "success": true
    }

This output now includes the variables required for both the init-cfg template as well as the bootstrap template.

.. code-block:: bash

    local:~ operator$ curl -X POST -d '{ "archive_type": "iso", "bootstrap_template": "Default Bootstrap.xml", "default_next_hop": "10.0.1.1", "deployment_type": "kvm", "ethernet1_1_profile": "PING", "ethernet2_1_profile": "PING", "hostname": "NGFW-003", "init_cfg_template": "Default Init-Cfg DHCP", "management_gateway": "10.0.1.1", "management_ip": "10.0.1.129", "management_mask": "255.255.255.0", "timezone": "NewYork"}' http://localhost:5000/generate_bootstrap_package -o NGFW-003.iso
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100  394k  100  394k  100   385  7857k   7678 --:--:-- --:--:-- --:--:-- 7880k
    local:~ operator$ hdiutil mount NGFW-003.iso
    /dev/disk2          	                               	/Volumes/bootstrap
    local:~ operator$ cat /Volumes/bootstrap/config/init-cfg.txt
    type=dhcp
    hostname=NGFW-003
    dns-primary=
    panorama-server=
    dgname=
    tplname=
    vm-auth-key=
    local:~ operator$ cat /Volumes/bootstrap/config/bootstrap.xml | grep hostname
              <hostname>NGFW-003</hostname>



Using the bootstrapper-cli 
==========================

If you do not want to have the bootstrapper service always available via a REST interface, you can use the 
bootstrapper-cli interface.

.. code-block:: bash

    cat /tmp/bootstrapper_cli_example.yaml
    ---
    dhcp_or_static: dhcp-client
    ip_address:
    default_gateway:
    netmask:
    ipv6_address:
    ipv6_default_gateway:
    hostname: my-example-hostname
    panorama_server:
    panorama_server_2:
    tpl_name:
    dg_name:
    dns_primary:
    dns_secondary:
    op_command_modes:
    dhcp_send_hostname:
    dhcp_send_client_id:
    dhcp_accept_server_hostname:
    dhcp_accept_server_domain:
    vm_auth_key:
    auth_code: VALID_AUTHCODE_HERE

and launch with:

.. code-block:: bash

    docker run -it --rm -v "$(pwd):/var/tmp" -w /var/tmp nembery/panos_bootstrapper  bootstrap.sh build_bootstrap_iso bootstrapper_cli_example.yaml


You can also use this interface to build bootstrap archives in all the various public clouds. For AWS for example:

.. code-block/;: bash

    docker run -it --rm -v "$(pwd):/var/tmp" -w /var/tmp -e AWS_LOCATION=$(echo $AWS_LOCATION) -e AWS_ACCESS_KEY=$(echo $AWS_ACCESS_KEY) -e AWS_SECRET_KEY=$(echo $AWS_SECRET_KEY) nembery/panos_bootstrapper  bootstrap.sh build_bootstrap_aws bootstrapper_cli_example.yaml


Azure is similar. Set the appropriate environment variables then run the build_bootstrap_azure command:

.. code-block:: bash

    docker run -it --rm -v "$(pwd):/var/tmp" -w /var/tmp -e AZURE_STORAGE_ACCESS_KEY=$(echo $AZURE_STORAGE_ACCESS_KEY) -e AZURE_STORAGE_ACCOUNT=$(echo $AZURE_STORAGE_ACCOUNT) nembery/panos_bootstrapper  bootstrap.sh build_bootstrap_azure bootstrapper_cli_example.yaml

