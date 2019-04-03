# API Example Usage

This document shows some of the available options using the API



## Generating a base64 encoded tar.gz file for use with Openstack HEAT

This example will post the required data to generate a HEAT template, bootstrap.xml init-cfg.txt, and license 
files. They will be placed in a zip file that can be unzipped and pushed to an openstack cluster using the 'openstack'
CLI tool.

```bash
DFWMACK0AJHTDG:docs nembery$ curl -X POST -d '{
        "hostname": "panos-81",
        "auth_key": "v123",
        "archive_type": "encoded_tgz",
        "management_ip": "192.168.1.100",
        "management_mask": "255.255.255.0",
        "management_gateway": "192.168.1.254",
        "dns_server": "192.168.1.2",
        "outside_ip": "192.168.2.100",
        "inside_ip": "192.168.3.100",
        "ethernet2_1_profile": "PINGSSHTTPS",
        "ethernet1_1_profile": "PINGSSHTTPS",
        "default_next_hop": "10.10.10.10"}' http://localhost:5000/generate_bootstrap_package -o panos-01.tgz.base64

```

## Generating an ISO image for use with KVM / esxi

```bash
DFWMACK0AJHTDG:docs nembery$ curl -X POST -d '{
        "deployment_type": "kvm",
        "archive_type": "iso",
        "hostname": "panos-81",
        "auth_key": "v123",
        "management_ip": "192.168.1.100",
        "management_mask": "255.255.255.0",
        "management_gateway": "192.168.1.254",
        "dns_server": "192.168.1.2",
        "ethernet2_1_profile": "PINGSSHTTPS",
        "ethernet1_1_profile": "PINGSSHTTPS",
        "default_next_hop": "10.10.10.10"
    }'  http://localhost:5000/generate_bootstrap_package -o panos-01.iso
```


## Simple Caching System Debugging
```bash
DFWMACK0AJHTDG:docs nembery$ curl -X POST -d '{"contents": "hi there"}' http://localhost:5000/set 
{
  "key": "bead72e4-5708-48ce-9eda-27d7bc5b72da", 
  "success": true
}
DFWMACK0AJHTDG:docs nembery$ curl -X POST -d '{"key": "bead72e4-5708-48ce-9eda-27d7bc5b72da"}' http://localhost:5000/get_object
{
  "contents": "hi there", 
  "key": "bead72e4-5708-48ce-9eda-27d7bc5b72da"
}
DFWMACK0AJHTDG:docs nembery$ 

```