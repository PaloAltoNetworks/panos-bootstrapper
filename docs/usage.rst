Using the API
=============

API documentation is included in OpenAPI (currently swagger 2.0) format. A simple swagger API viewer is included
in the root directory by browsing to http://bootstrapper_host:5000/, where bootstrapper_host is the host where
the bootstrapper service is running.

Some examples are given below:


Generate a minimal Bootstrap Archive
------------------------------------


.. code-block:: bash

    local:~ operator$ curl -J -O  -X POST -d "hostname=PANOS-01"  localhost:5001/generate_bootstrap_package
    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
    100  138M  100  138M  100    22  17.9M      2  0:00:11  0:00:07  0:00:04 30.6M
    curl: Saved to filename 'PANOS-TEST-01.zip'


Controlling the output format
------------------------------


.. code-block:: bash

   local:~ operator$ curl -J -O  -X POST -d "hostname=PANOS-TEST-01" -d "archive_type=iso"  localhost:5001/generate_bootstrap_package
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100  138M  100  138M  100    39  37.5M     10  0:00:03  0:00:03 --:--:-- 37.5M
    curl: Saved to filename 'PANOS-TEST-01.iso'


Using JSON Input
-----------------


.. code-block:: bash

    local:~ operator$ curl -J -O  -X POST -d '{"hostname": "PANOS-TEST-02", "archive_type": "iso"}' -H "Content-Type: application/json" localhost:5001/generate_bootstrap_package
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100  138M  100  138M  100    52  32.9M     12  0:00:04  0:00:04 --:--:-- 34.6M
    curl: Saved to filename 'PANOS-TEST-02.iso'



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
                "description": "PAN-OS Version 8.0 Init-Cfg",
                "name": "Default Init-Cfg",
                "type": "init-cfg"
            }
        ]
    }


Show the contents of a template
-------------------------------


.. code-block:: bash

    local:~ operator$ curl -X POST -d "template_name=Default Init-Cfg"  http://localhost:5001/get_template
    type={{ dhcp_or_static }}
    ip-address={{ ip_address }}
    default-gateway={{ default_gateway }}
    netmask={{ netmask }}
    ipv6-address={{ ipv6_address }}
    ipv6-default-gateway={{ ipv6_default_gateway }}
    hostname={{ hostname }}
    panorama-server={{ panorama_server }}
    panorama-server-2={{ panorama_server_2 }}
    tplname={{ tpl_name }}
    dgname={{ dg_name }}
    dns-primary={{ dns_primary }}
    dns-secondary={{ dns_secondary }}
    op-command-modes={{ op_command_modes }}
    dhcp-send-hostname={{ dhcp_send_hostname }}
    dhcp-send-client-id={{ dhcp_send_client_id }}
    dhcp-accept-server-hostname={{ dhcp_accept_server_hostname }}
    dhcp-accept-server-domain={{ dhcp_accept_server_domain }}
    vm-auth-key={{ vm_auth_key }}

This template only defines one variable. In this case `hostname` is declared as a variable. To use this template in a
bootstrap package, you must supply a `hostname` variable to the `generate_bootstrap_package` API.


To show required variables in a set of templates
------------------------------------------------


.. code-block:: bash

    local:~ operator$ curl -X POST -d '{"init_cfg_template": "init-cfg-hostname"}' -H "Content-Type: application/json" http://localhost:5000/get_bootstrap_variables | python -m json.tool
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

    curl -X POST -d '{ "archive_type": "iso", "deployment_type": "kvm", "hostname": "NGFW-001", "init_cfg_template": "init-cfg-hostname"}' -H "Content-Type: application/json"  http://localhost:5000/generate_bootstrap_package -o NGFW.iso
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
with the desired init-cfg template compiled with our variables. Attaching this ISO to a factory default PAN-OS firewall
will result in the firewall booting up with the NGFW-001 hostname configured at boot.


Building a Bootstrap Package with a custom bootstrap.xml
--------------------------------------------------------

In the previous example, we only built a package that included the init-cfg.txt file. However, you can also include
a complete firewall configuration using a `bootstrap.xml` file.


Once again, let's get all required variables for our selected templates:
*note that we've included a `bootstrap_template` parameters with the value of a bootstrap template name.


.. code-block:: bash

    local:curl -X POST -d '{"init_cfg_template": "Default Init-Cfg", "bootstrap_template": "Default Bootstrap.xml"}' -H "Content-Type: application/json"  http://localhost:5000/get_bootstrap_variables | python -m json.tool
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
            "init_cfg_template": "Default Init-Cfg",
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

    local:~ operator$ curl -X POST -d '{ "archive_type": "iso", "bootstrap_template": "Default Bootstrap.xml", "default_next_hop": "10.0.1.1", "deployment_type": "kvm", "ethernet1_1_profile": "PING", "ethernet2_1_profile": "PING", "hostname": "NGFW-003", "init_cfg_template": "Default Init-Cfg", "management_gateway": "10.0.1.1", "management_ip": "10.0.1.129", "management_mask": "255.255.255.0", "timezone": "NewYork"}' -H "Content-Type: application/json"  http://localhost:5000/generate_bootstrap_package -o NGFW-003.iso
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


.. code-block:: bash

    docker run -it --rm -v "$(pwd):/var/tmp" -w /var/tmp -e AWS_LOCATION=$(echo $AWS_LOCATION) -e AWS_ACCESS_KEY=$(echo $AWS_ACCESS_KEY) -e AWS_SECRET_KEY=$(echo $AWS_SECRET_KEY) nembery/panos_bootstrapper  bootstrap.sh build_bootstrap_aws bootstrapper_cli_example.yaml


Azure is similar. Set the appropriate environment variables then run the build_bootstrap_azure command:


.. code-block:: bash

    docker run -it --rm -v "$(pwd):/var/tmp" -w /var/tmp -e AZURE_STORAGE_ACCESS_KEY=$(echo $AZURE_STORAGE_ACCESS_KEY) -e AZURE_STORAGE_ACCOUNT=$(echo $AZURE_STORAGE_ACCOUNT) nembery/panos_bootstrapper  bootstrap.sh build_bootstrap_azure bootstrapper_cli_example.yaml

