# PANOS Bootstrapper

Panos bootstrapper is a tool to quickly build all required files to boostrap
a panos device. This usually requires a customized bootstrap.xml, init-cfg.txt, and 
a license file. However, other scenarios may require more files like Openstack or ONAP.

This tool follows a micro-services design philosophy where it does only one thing, but tries
to do it well. For example, there is no GUI for this tool. It is expected that another 
single purpose tool will consume the this API to produce a suitable UI

## Getting started

Edit the `bootstrapper/conf/defaults.yaml` file to reflect your envinonment. Then refer
to the `api_examples` documents in the docs folder. 

## Customization

Each template can be fully customized using the jinja2 templating language. All 
template amd input validation is done dynamically to make creating and using customized
templates as easy as possible. 
