# Copyright (c) 2018, Palo Alto Networks
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Author: Nathan Embery nembery@paloaltonetworks.com

"""
Palo Alto Networks panos- bootstrapper

panos-bootstrapper is a tool to build bootstrap packages for Pan-OS devices.

This tool provides an API that can be consumed by other automation tools such as Ansible or Salt.

Please see http://panos-bootstrapper.readthedocs.io for more information

This software is provided without support, warranty, or guarantee.
Use at your own risk.
"""

import logging
import sys
import urllib3
from urllib.parse import unquote

from flask import Flask
from flask import Response
from flask import abort
from flask import jsonify
from flask import render_template
from flask import request
from flask import send_file
from werkzeug.exceptions import BadRequest

from bootstrapper.lib import archive_utils
from bootstrapper.lib import bootstrapper_utils
from bootstrapper.lib import cache_utils
from bootstrapper.lib.db import db_session
from bootstrapper.lib.db import init_db
from bootstrapper.lib.exceptions import RequiredParametersError
from bootstrapper.lib.exceptions import TemplateNotFoundError
from .lib import jinja2_filters

app = Flask(__name__)
defaults = bootstrapper_utils.load_defaults()
config = bootstrapper_utils.load_config()

# disable HTTPS warnings
urllib3.disable_warnings()


@app.route('/')
def index():
    """
    Default route, return simple HTML page
    :return:  index.html template
    """
    return render_template('index.html', title='PanOS Bootstrap Utility')


@app.route('/bootstrapper.swagger.json')
def api():
    """
    Simple api to return the swagger json
    :return: json file
    """
    return send_file('templates/bootstrapper.swagger.json')


@app.route('/get/<key>', methods=['GET'])
def get_object_contents(key):
    """
    Get object from cache, useful to 'chain' together actions
    :return: json encoded string with dict containing with key and contents keys
    """
    if key is None or key == "":
        r = jsonify(message="Not all required params are present", success=False, status_code=400)
        r.status_code = 400
        return r

    contents = cache_utils.get(key)
    return Response(contents)


@app.route('/set', methods=['POST'])
def set_object():
    """
    Adds an serializable object to the cache
    :return: json encoded string with dict containing key and success keys
    """
    input_params = request.get_json() or request.form.to_dict()
    contents = input_params.get('contents', None)
    if contents is None:
        r = jsonify(message="Not all required keys are present", success=False, status_code=400)
        r.status_code = 400
        return r

    key = cache_utils.set(contents)
    return jsonify(key=key, success=True)


@app.route('/bootstrap_openstack', methods=['POST'])
def bootstrap_openstack():
    try:
        input_params = request.get_json() or request.form.to_dict()
        base_config = bootstrapper_utils.build_base_configs(input_params)
        base_config = bootstrapper_utils.build_openstack_heat(base_config, input_params, archive=True)

        archive = archive_utils.create_archive(base_config, input_params['hostname'])
        mime_type = 'application/zip'

        print("archive path is: %s" % archive)
        if archive is None:
            abort(500, 'Could not create archive! Check bootstrapper logs for more information')

        return send_file(archive, mimetype=mime_type, as_attachment=True)

    except (BadRequest, RequiredParametersError):
        abort(400, 'Invalid input parameters')
    except TemplateNotFoundError:
        print('Could not load templates!')
        abort(500, 'Could not load template!')


@app.route('/bootstrap_kvm', methods=['POST'])
def bootstrap_kvm():
    try:
        input_params = request.get_json() or request.form.to_dict()
        base_config = bootstrapper_utils.build_base_configs(input_params)

        archive = archive_utils.create_iso(base_config, input_params['hostname'])
        mime_type = 'application/iso-image'

        print("archive path is: %s" % archive)
        if archive is None:
            abort(500, 'Could not create archive! Check bootstrapper logs for more information')

        return send_file(archive, mimetype=mime_type, as_attachment=True)

    except (BadRequest, RequiredParametersError):
        abort(400, 'Invalid input parameters')
    except TemplateNotFoundError:
        print('Could not load templates!')
        abort(500, 'Could not load template!')


@app.route('/bootstrap_kvm', methods=['POST'])
def bootstrap_openstack_tgz():
    try:
        input_params = request.get_json() or request.form.to_dict()
        base_config = bootstrapper_utils.build_base_configs(input_params)

        archive = archive_utils.create_tgz(base_config, input_params['hostname'])
        mime_type = 'application/gzip'

        print("archive path is: %s" % archive)
        if archive is None:
            abort(500, 'Could not create tgz archive! Check bootstrapper logs for more information')

        return send_file(archive, mimetype=mime_type, as_attachment=True)

    except (BadRequest, RequiredParametersError):
        abort(400, 'Invalid input parameters')
    except TemplateNotFoundError:
        print('Could not load templates!')
        abort(500, 'Could not load template!')


@app.route('/bootstrap_aws', methods=['POST'])
def bootstrap_aws():
    try:
        input_params = request.get_json() or request.form.to_dict()
        base_config = bootstrapper_utils.build_base_configs(input_params)

        response = archive_utils.create_s3_bucket(base_config, input_params['hostname'], input_params['aws_location'],
                                                  input_params['aws_key'], input_params['aws_secret']
                                                  )
        return jsonify(response=response)

    except KeyError as ke:
        print(ke)
        abort(400, 'Invalid input parameters! Not all required parameters are present')
    except (BadRequest, RequiredParametersError):
        abort(400, 'Invalid input parameters for basic configuration!')
    except TemplateNotFoundError:
        print('Could not load templates!')
        abort(500, 'Could not load template!')


@app.route('/bootstrap_azure', methods=['POST'])
def bootstrap_azure():
    try:
        input_params = request.get_json() or request.form.to_dict()
        base_config = bootstrapper_utils.build_base_configs(input_params)

        response = archive_utils.create_azure_fileshare(base_config, input_params['hostname'],
                                                        input_params['azure_account_name'],
                                                        input_params['azure_account_key']
                                                        )
        return jsonify(response=response)

    except KeyError as ke:
        print(ke)
        abort(400, 'Invalid input parameters! Not all required parameters are present')
    except (BadRequest, RequiredParametersError):
        abort(400, 'Invalid input parameters for basic configuration!')
    except TemplateNotFoundError:
        print('Could not load templates!')
        abort(500, 'Could not load template!')


@app.route('/bootstrap_gcp', methods=['POST'])
def bootstrap_gcp():
    try:
        input_params = bootstrapper_utils.normalize_input_params(request)
        base_config = bootstrapper_utils.build_base_configs(input_params)

        response = archive_utils.create_gcp_bucket(base_config, input_params['hostname'],
                                                   input_params['gcp_project_id'],
                                                   input_params["gcp_access_token"]
                                                   )
        return jsonify(response=response)

    except KeyError as ke:
        print(ke)
        abort(400, 'Invalid input parameters! Not all required parameters are present')
    except (BadRequest, RequiredParametersError):
        abort(400, 'Invalid input parameters for basic configuration!')
    except TemplateNotFoundError:
        print('Could not load templates!')
        abort(500, 'Could not load template!')


@app.route('/generate_bootstrap_package', methods=['POST'])
def generate_bootstrap_package():
    """
    Main function to build a bootstrap archive. You must post the following params:
    hostname: we cannot build an archive without at least a hostname
    deployment_type: openstack, kvm, vmware, etc.
    archive_type: zip, iso

    You must also supply all the variables required from included templates

    :return: binary package containing variable interpolated templates
    """
    input_params = dict()
    try:
        # input_params = request.get_json() or request.form.to_dict()
        input_params = bootstrapper_utils.normalize_input_params(request)
        base_config = bootstrapper_utils.build_base_configs(input_params)

    except (BadRequest, RequiredParametersError):
        err_string = '\nRequired variables: hostname'
        err_string += '\nOptional variables: '
        vs = bootstrapper_utils.get_bootstrap_variables(input_params)
        for v in vs:
            err_string += '%s ' % v
        print('aborting due to bad request, invalid params')
        abort(400, 'Invalid input parameters %s' % err_string)
    except TemplateNotFoundError:
        print('aborting, Could not load templates!')
        abort(500, 'Could not load template!')

    # if desired deployment type is openstack, then add the heat templates and whatnot
    if 'deployment_type' in input_params and input_params['deployment_type'] == 'openstack':
        print('Including openstack')
        try:
            base_config = bootstrapper_utils.build_openstack_heat(base_config, input_params, archive=True)
        except RequiredParametersError:
            abort(400, 'Could not parse JSON data')

    if 'hostname' not in input_params:
        abort(400, 'No hostname found in posted data')

    # if the user supplies an 'archive_type' parameter we can return either a ZIP or ISO
    archive_type = input_params.get('archive_type', 'zip')

    # user has specified they want an ISO built
    if archive_type == 'iso':
        archive = archive_utils.create_iso(base_config, input_params['hostname'])
        mime_type = 'application/iso-image'

    elif archive_type == 'tgz':
        archive = archive_utils.create_tgz(base_config, input_params['hostname'])
        mime_type = 'application/gzip'

    elif archive_type == 's3':
        response = archive_utils.create_s3_bucket(base_config, input_params['hostname'], input_params['aws_location'],
                                                  input_params['aws_key'], input_params['aws_secret']
                                                  )
        return jsonify(response=response)

    elif archive_type == 'azure':
        response = archive_utils.create_azure_fileshare(base_config, input_params['hostname'],
                                                        input_params['azure_account_name'],
                                                        input_params['azure_account_key']
                                                        )
        return jsonify(response=response)

    elif archive_type == 'gcp':
        response = archive_utils.create_gcp_bucket(base_config, input_params['hostname'],
                                                   input_params['project_id'],
                                                   input_params["access_token"]
                                                   )
        return jsonify(response=response)

    else:
        # no ISO required, just make a zip
        archive = archive_utils.create_archive(base_config, input_params['hostname'])
        mime_type = 'application/zip'

    print("archive path is: %s" % archive)
    if archive is None:
        print('Aborting with no archive created')
        abort(500, 'Could not create archive! Check bootstrapper logs for more information')

    return send_file(archive, mimetype=mime_type, as_attachment=True)


@app.route('/get_bootstrap_variables', methods=['POST'])
def get_bootstrap_variables():
    print('Compiling variables required in payload to generate a valid bootstrap archive')
    input_params = bootstrapper_utils.normalize_input_params(request)
    vs = bootstrapper_utils.get_bootstrap_variables(input_params)
    payload = dict()

    payload['archive_type'] = "tgz"
    payload['auth_code'] = "VALID-PAN-AUTH-CODE"

    if 'bootstrap_template' in input_params and input_params['bootstrap_template'] is not None:
        print('Using bootstrap %s' % input_params['bootstrap_template'])
        payload['bootstrap_template'] = input_params['bootstrap_template']
    else:
        print('No bootstrap file requested')

    if 'init_cfg_template' in input_params and input_params['init_cfg_template'] is not None:
        print('Setting init_cfg_name')
        payload['init_cfg_template'] = input_params['init_cfg_template']
    else:
        print('No init_cfg file requested')

    if 'format' in input_params and input_params['format'] == 'aframe':
        for v in vs:
            payload[v] = "{{ %s }}" % v
    else:
        for v in vs:
            payload[v] = ""

    return jsonify(success=True, payload=payload, status_code=200)


@app.route('/import_template', methods=['POST'])
def import_template():
    """
    Adds a template to the db
    required keys are [name, template, description, type]
    template must be properly quoted for example using urllib3.quote
    see: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.quote
    :return: json with 'success', 'message' and 'status' keys
    """
    input_params = bootstrapper_utils.normalize_input_params(request)
    try:
        name = input_params['name']
        encoded_template = input_params['template']
        description = input_params.get('description', 'Imported Template')
        template_type = input_params.get('type', 'bootstrap')
        template = unquote(encoded_template)

    except KeyError:
        print("Not all required keys are present!")
        r = jsonify(message="Not all required keys for add template are present", success=False, status_code=400)
        r.status_code = 400
        return r
    print('Importing template with name: %s' % name)
    print('Importing template with description: %s' % description)
    print(template)
    if bootstrapper_utils.import_template(template, name, description, template_type):
        return jsonify(success=True, message='Imported Template Successfully', status_code=200)
    else:
        r = jsonify(success=False, message='Could not import template repository to the configuration',
                    status_code=500)
        r.status_code = 500
        return r


@app.route('/update_template', methods=['POST'])
def update_template():
    """
    Updates a template
    :return: json with 'success', 'message' and 'status' keys
    """
    input_params = bootstrapper_utils.normalize_input_params(request)
    try:
        name = input_params['name']
        encoded_template = input_params['template']
        description = input_params.get('description', 'Imported Template')
        template_type = input_params.get('type', 'bootstrap')
        template = unquote(encoded_template)

    except KeyError:
        print("Not all required keys are present!")
        r = jsonify(message="Not all required keys for add template are present", success=False, status_code=400)
        r.status_code = 400
        return r
    print('Updating template with name: %s' % name)
    if bootstrapper_utils.edit_template(template, name, description, template_type):
        return jsonify(success=True, message='Updated Template Successfully', status_code=200)
    else:
        r = jsonify(success=False, message='Could not import template repository to the configuration',
                    status_code=500)
        r.status_code = 500
        return r


@app.route('/delete_template', methods=['POST'])
def delete_template():
    """
    Deletes a template from the db
    :return: json with 'success', 'message' and 'status' keys
    """
    input_params = bootstrapper_utils.normalize_input_params(request)
    try:
        name = input_params['template_name']
    except KeyError:
        print("Not all required keys are present!")
        r = jsonify(message="Not all required keys for add template are present", success=False, status_code=400)
        r.status_code = 400
        return r

    if bootstrapper_utils.delete_template(name):
        return jsonify(success=True, message='Deleted Template Successfully', status_code=200)
    else:
        r = jsonify(success=False, message='Could not delete template', status_code=500)
        r.status_code = 500
        return r


@app.route('/list_templates', methods=['GET'])
def list_templates():
    """
    Lists all templates, returns a list of dicts with the following keys:
    name, type, description
    :return:
    """
    ts = bootstrapper_utils.list_bootstrap_templates()
    return jsonify(success=True, templates=ts, status_code=200)


@app.route('/get_template', methods=['POST'])
def get_template():
    input_params = bootstrapper_utils.normalize_input_params(request)
    try:
        name = input_params['template_name']
    except KeyError:
        print("Not all required keys are present!")
        r = jsonify(message="Not all required keys for add template are present", success=False, status_code=400)
        r.status_code = 400
        return r

    ts = bootstrapper_utils.get_template(name)
    return Response(ts, mimetype='text/plain')


@app.route('/list_init_cfg_templates', methods=['GET'])
def list_init_cfg_templates():
    ts = bootstrapper_utils.list_init_cfg_templates()
    return jsonify(success=True, templates=ts, status_code=200)


@app.route('/render_template', methods=['POST'])
def render_db_template():
    """
    Renders a template with the posted variables
    :return: json with 'success', 'message' and 'status' keys
    """
    try:
        input_params = bootstrapper_utils.normalize_input_params(request)
        return bootstrapper_utils.compile_template(input_params)
    except RequiredParametersError as rpe:
        print(rpe)
        abort(400, 'Not all required parameters are present in payload')
    except TemplateNotFoundError as tne:
        print(tne)
        abort(500, 'Could not load desired template')


@app.route('/get_template_variables', methods=['POST'])
def get_template_variables():
    print('Getting variables from a single template')
    input_params = bootstrapper_utils.normalize_input_params(request)

    if 'template_name' not in input_params:
        abort(400, 'Not all required keys for bootstrap.xml are present')

    template_name = input_params['template_name']
    required = bootstrapper_utils.get_required_vars_from_template(template_name)

    payload = dict()
    payload['template_name'] = template_name
    if 'format' in input_params and input_params['format'] == 'aframe':
        for v in required:
            payload[v] = "{{ %s }}" % v
    else:
        for v in required:
            payload[v] = ""

    return jsonify(success=True, payload=payload, status_code=200)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.before_first_request
def init_application():
    # set up logging
    handler = logging.StreamHandler(sys.stdout)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    print('Init App')

    import os
    if not os.path.exists('/var/tmp/.bootstrap_complete'):
        init_db()
        print('Importing templates')
        bootstrapper_utils.import_templates()
        with open('/var/tmp/.bootstrap_complete', 'w+') as init_complete:
            init_complete.write('done')

    for f in jinja2_filters.defined_filters:
        app.jinja_env.filters[f] = getattr(jinja2_filters, f)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
