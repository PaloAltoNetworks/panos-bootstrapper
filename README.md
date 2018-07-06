# PANOS Bootstrapper

Panos bootstrapper is a tool to quickly build all required files to bootstrap
a Pala Alto Networks device. This usually requires a customized bootstrap.xml, init-cfg.txt, and 
a license file. The output will be an archive package, either ISO or ZIP, with all required files fully compiled
from the supplied templates and input variables. 

This tool follows a micro-services design philosophy where it does only one thing, but tries
to do it well. As such, there is no GUI for this tool. It is expected that another 
tool will consume this API directly.

An example GUI application that consumes this service can be found
 [here](https://github.com/PaloAltoNetworks/panos-bootstrapper-ui).

## Getting started

A prebuilt docker container can be found here:

```bash

docker search nembery/panos_bootstrapper

```

Most users will want to use the example pre-built
 [Automatio UI](https://github.com/PaloAltoNetworks/panos-bootstrapper-ui)).

To start the service manually, issue the following commands:

```bash
export FLASK_APP=./bootstrapper/bootstrapper.py
flask run --host=0.0.0.0 --port=5002
```

## Examples and documentation

The API is documented using the OpenAPI specification. The 
API documentation can be found by browsing to the IP address and Port specified above. 

Additional examples can be found in the api_examples.md and testing.md documents in the 'docs' folder.


## Customization

Each template can be fully customized using the jinja2 templating language. All 
template amd input validation is done dynamically to make creating and using customized
templates as easy as possible. 
