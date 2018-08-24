import logging
import sys
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


@app.route('/')
def index():
    """
    Default route, return simple HTML page
    :return:  index.htnl template
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
    posted_json = request.get_json(force=True)
    contents = posted_json.get('contents', None)
    if contents is None:
        r = jsonify(message="Not all required keys are present", success=False, status_code=400)
        r.status_code = 400
        return r

    key = cache_utils.set(contents)
    return jsonify(key=key, success=True)


@app.route('/bootstrap_openstack', methods=['POST'])
def bootstrap_openstack():
    try:
        posted_json = request.get_json(force=True)
        base_config = bootstrapper_utils.build_base_configs(posted_json)
        base_config = bootstrapper_utils.build_openstack_heat(base_config, posted_json, archive=True)

        archive = archive_utils.create_archive(base_config, posted_json['hostname'])
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
        posted_json = request.get_json(force=True)
        base_config = bootstrapper_utils.build_base_configs(posted_json)

        archive = archive_utils.create_iso(base_config, posted_json['hostname'])
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


@app.route('/bootstrap_aws', methods=['POST'])
def bootstrap_aws():
    try:
        posted_json = request.get_json(force=True)
        base_config = bootstrapper_utils.build_base_configs(posted_json)

        response = archive_utils.create_s3_bucket(base_config, posted_json['hostname'], posted_json['aws_location'],
                                                  posted_json['aws_key'], posted_json['aws_secret']
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
        posted_json = request.get_json(force=True)
        base_config = bootstrapper_utils.build_base_configs(posted_json)

        response = archive_utils.create_azure_fileshare(base_config, posted_json['hostname'],
                                                        posted_json['azure_account_name'],
                                                        posted_json['azure_account_key']
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
        posted_json = request.get_json(force=True)
        base_config = bootstrapper_utils.build_base_configs(posted_json)

        response = archive_utils.create_gcp_bucket(base_config, posted_json['hostname'],
                                                   posted_json['gcp_project_id'],
                                                   posted_json["gcp_access_token"]
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

    try:
        posted_json = request.get_json(force=True)
        base_config = bootstrapper_utils.build_base_configs(posted_json)

    except (BadRequest, RequiredParametersError):
        abort(400, 'Invalid input parameters')
    except TemplateNotFoundError:
        print('Could not load templates!')
        abort(500, 'Could not load template!')

    # if desired deployment type is openstack, then add the heat templates and whatnot
    if 'deployment_type' in posted_json and posted_json['deployment_type'] == 'openstack':
        try:
            base_config = bootstrapper_utils.build_openstack_heat(base_config, posted_json, archive=True)
        except RequiredParametersError:
            abort(400, 'Could not parse JSON data')

    if 'hostname' not in posted_json:
        abort(400, 'No hostname found in posted data')

    # if the user supplies an 'archive_type' parameter we can return either a ZIP or ISO
    archive_type = posted_json.get('archive_type', 'iso')

    # user has specified they want an ISO built
    if archive_type == 'iso':
        archive = archive_utils.create_iso(base_config, posted_json['hostname'])
        mime_type = 'application/iso-image'

    elif archive_type == 's3':
        response = archive_utils.create_s3_bucket(base_config, posted_json['hostname'], posted_json['aws_location'],
                                                  posted_json['aws_key'], posted_json['aws_secret']
                                                  )
        return jsonify(response=response)

    elif archive_type == 'azure':
        response = archive_utils.create_azure_fileshare(base_config, posted_json['hostname'],
                                                        posted_json['azure_account_name'],
                                                        posted_json['azure_account_key']
                                                        )
        return jsonify(response=response)

    elif archive_type == 'gcp':
        response = archive_utils.create_gcp_bucket(base_config, posted_json['hostname'],
                                                   posted_json['project_id'],
                                                   posted_json["access_token"]
                                                   )
        return jsonify(response=response)

    else:
        # no ISO required, just make a zip
        archive = archive_utils.create_archive(base_config, posted_json['hostname'])
        mime_type = 'application/zip'

    print("archive path is: %s" % archive)
    if archive is None:
        abort(500, 'Could not create archive! Check bootstrapper logs for more information')

    return send_file(archive, mimetype=mime_type, as_attachment=True)


@app.route('/get_bootstrap_variables', methods=['POST'])
def get_bootstrap_variables():
    print('Compiling variables required in payload to generate a valid bootstrap archive')
    posted_json = request.get_json(force=True)
    vs = bootstrapper_utils.get_bootstrap_variables(posted_json)
    payload = dict()

    payload['archive_type'] = "iso"
    payload['deployment_type'] = "kvm"

    if 'bootstrap_template' in posted_json and posted_json['bootstrap_template'] is not None:
        print('Using bootstrap %s' % posted_json['bootstrap_template'])
        payload['bootstrap_template'] = posted_json['bootstrap_template']
    else:
        print('No bootstrap file requested')

    if 'init_cfg_template' in posted_json and posted_json['init_cfg_template'] is not None:
        print('Setting init_cfg_name')
        payload['init_cfg_template'] = posted_json['init_cfg_template']
    else:
        print('No init_cfg file requested')

    if 'format' in posted_json and posted_json['format'] == 'aframe':
        for v in vs:
            payload[v] = "{{ %s }}" % v
    else:
        for v in vs:
            payload[v] = ""

    return jsonify(success=True, payload=payload, status_code=200)


@app.route('/import_template', methods=['POST'])
def import_template():
    """
    Adds a template location to the configuration
    :return: json with 'success', 'message' and 'status' keys
    """
    posted_json = request.get_json(force=True)
    try:
        name = posted_json['name']
        encoded_template = posted_json['template']
        description = posted_json.get('description', 'Imported Template')
        template_type = posted_json.get('type', 'bootstrap')
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


@app.route('/delete_template', methods=['POST'])
def delete_template():
    """
    Adds a template location to the configuration
    :return: json with 'success', 'message' and 'status' keys
    """
    posted_json = request.get_json(force=True)
    try:
        name = posted_json['template_name']
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
    ts = bootstrapper_utils.list_bootstrap_templates()
    return jsonify(success=True, templates=ts, status_code=200)


@app.route('/get_template', methods=['POST'])
def get_template():
    posted_json = request.get_json(force=True)
    try:
        name = posted_json['template_name']
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
        posted_json = request.get_json(force=True)
        return bootstrapper_utils.compile_template(posted_json)
    except RequiredParametersError as rpe:
        print(rpe)
        abort(400, 'Not all required parameters are present in payload')
    except TemplateNotFoundError as tne:
        print(tne)
        abort(500, 'Could not load desired template')


@app.route('/get_template_variables', methods=['POST'])
def get_template_variables():
    print('Getting variables from a single template')
    posted_json = request.get_json(force=True)

    if 'template_name' not in posted_json:
        abort(400, 'Not all required keys for bootstrap.xml are present')

    template_name = posted_json['template_name']
    required = bootstrapper_utils.get_required_vars_from_template(template_name)

    payload = dict()
    payload['template_name'] = template_name
    if 'format' in posted_json and posted_json['format'] == 'aframe':
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

    init_db()
    bootstrapper_utils.import_templates()

    for f in jinja2_filters.defined_filters:
        app.jinja_env.filters[f] = getattr(jinja2_filters, f)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
