import os
import sys

import click
import yaml
from flask import Flask
from flask.cli import with_appcontext
from werkzeug.exceptions import BadRequest

from bootstrapper.bootstrapper import init_application
from bootstrapper.lib import archive_utils
from bootstrapper.lib import bootstrapper_utils
from bootstrapper.lib.exceptions import RequiredParametersError
from bootstrapper.lib.exceptions import TemplateNotFoundError

app = Flask(__name__)


@app.cli.command('build_bootstrap_gcp')
@click.argument('input_config', type=click.File('rb'))
@with_appcontext
def build_bootstrap_gcp(input_config):
    init_application()
    try:
        yaml_conf = input_config.read()
        payload = yaml.load(yaml_conf)
        print(payload)
        base_config = bootstrapper_utils.build_base_configs(payload)

        if not set(['GCP_PROJECT_ID', 'GCP_ACCESS_TOKEN']).issubset(set(os.environ)):
            print('GCP bootstrap type requires GCP_PROJECT_ID and GCP_ACCESS_TOKEN')
            sys.exit(1)

        project_id = os.environ['GCP_PROJECT_ID']
        access_token = os.environ['GCP_ACESSS_TOKEN']

        message = archive_utils.create_gcp_bucket(base_config, payload['hostname'], project_id, access_token)

        print(message)

    except IOError as ioe:
        print('Could not read from input')
        print(ioe)
        sys.exit(1)
    except yaml.YAMLError as ye:
        print('Could not load YAML input')
        print(ye)
        sys.exit(2)
    except (BadRequest, RequiredParametersError):
        sys.exit(3)
    except TemplateNotFoundError:
        print('Could not load templates!')
        sys.exit(4)


@app.cli.command('build_bootstrap_azure')
@click.argument('input_config', type=click.File('rb'))
@with_appcontext
def build_bootstrap_azure(input_config):
    init_application()
    try:
        yaml_conf = input_config.read()
        payload = yaml.load(yaml_conf)
        print(payload)
        base_config = bootstrapper_utils.build_base_configs(payload)

        if not set(['AZURE_STORAGE_ACCOUNT', 'AZURE_STORAGE_ACCESS_KEY']).issubset(set(os.environ)):
            print('Azure bootstrap type requires AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_ACCESS_KEY')
            sys.exit(1)

        storage_account_name = os.environ['AZURE_STORAGE_ACCOUNT']
        access_key = os.environ['AZURE_STORAGE_ACCESS_KEY']

        message = archive_utils.create_azure_fileshare(base_config, payload['hostname'],
                                                       storage_account_name, access_key)

        print(message)

    except IOError as ioe:
        print('Could not read from input')
        print(ioe)
        sys.exit(1)
    except yaml.YAMLError as ye:
        print('Could not load YAML input')
        print(ye)
        sys.exit(2)
    except (BadRequest, RequiredParametersError):
        sys.exit(3)
    except TemplateNotFoundError:
        print('Could not load templates!')
        sys.exit(4)


@app.cli.command('build_bootstrap_aws')
@click.argument('input_config', type=click.File('rb'))
@with_appcontext
def build_bootstrap_aws(input_config):
    init_application()
    try:
        yaml_conf = input_config.read()
        payload = yaml.load(yaml_conf)
        # print(payload)
        base_config = bootstrapper_utils.build_base_configs(payload)

        if not set(['AWS_LOCATION', 'AWS_SECRET_KEY', 'AWS_ACCESS_KEY']).issubset(set(os.environ)):
            print('s3 bootstrap type requires AWS_LOCATION, AWS_ACCESS_KEY, and AWS_SECRET_KEY')
            sys.exit(1)

        location = os.environ['AWS_LOCATION']
        access_key = os.environ['AWS_ACCESS_KEY']
        secret_key = os.environ['AWS_SECRET_KEY']

        message = archive_utils.create_s3_bucket(base_config, payload['hostname'],
                                                 location, access_key, secret_key)

        print(message)

    except IOError as ioe:
        print('Could not read from input')
        print(ioe)
        sys.exit(1)
    except yaml.YAMLError as ye:
        print('Could not load YAML input')
        print(ye)
        sys.exit(2)
    except (BadRequest, RequiredParametersError):
        sys.exit(3)
    except TemplateNotFoundError:
        print('Could not load templates!')
        sys.exit(4)


@app.cli.command('build_bootstrap_iso')
@click.argument('input_arg', type=click.File('rb'))
# @click.argument('output_arg', type=click.Path())
@with_appcontext
def build_bootstrap_iso(input_arg):
    init_application()
    try:
        yaml_conf = input_arg.read()
        payload = yaml.load(yaml_conf)
        print(payload)
        base_config = bootstrapper_utils.build_base_configs(payload)
        archive_path = archive_utils.create_iso(base_config, payload['hostname'])

        if archive_path is None:
            print('Could not create archive!')
            sys.exit(1)

        print(archive_path)
        sys.exit(0)

    except IOError as ioe:
        print('Could not read from input')
        print(ioe)
        sys.exit(1)
    except yaml.YAMLError as ye:
        print('Could not load YAML input')
        print(ye)
        sys.exit(2)
    except (BadRequest, RequiredParametersError):
        sys.exit(3)
    except TemplateNotFoundError:
        print('Could not load templates!')
        sys.exit(4)


@app.cli.command('list_templates')
def list_templates():
    init_application()
    all_templates = list()
    all_templates += bootstrapper_utils.list_init_cfg_templates()
    all_templates += bootstrapper_utils.list_bootstrap_templates()
    print(all_templates)
    sys.exit(0)


@click.option('-n', '--name')
@click.option('-d', '--description')
@click.option('-t', '--type', 'template_type', default='bootstrap')
@click.option('-f', '--file', 'template_file', type=click.File('r'))
@app.cli.command('import_template')
def import_template(name, description, template_file, template_type):
    """
    Provides an interface to add / update templates via cli
    :param name: Name of the template to add / update
    :param description:  template description
    :param template_file: full path of the template file to open and read
    :param template_type: type of template 'init-cfg' or 'bootstrap'
    :return: boolean exit values
    """
    init_application()
    template_string = template_file.read()
    print(type(template_string))
    print(template_string)
    if bootstrapper_utils.edit_template(template_string, name, description, template_type):
        return 'Template added successfully'
    else:
        print('Could not add template')
        sys.exit(1)


@click.argument('template_name')
@app.cli.command('get_template')
def get_template(template_name):
    """
    Provides an interface to get the contents of a template
    :param template_name: Name of the template to add / update
    """
    init_application()
    t = bootstrapper_utils.get_template(template_name)
    if t is None:
        sys.exit(1)

    print(t)
    sys.exit(0)


@app.cli.command('init')
def init_cli():
    init_application()


app.cli.add_command(init_cli)
app.cli.add_command(get_template)
app.cli.add_command(import_template)
app.cli.add_command(list_templates)
app.cli.add_command(build_bootstrap_iso)
app.cli.add_command(build_bootstrap_azure)
app.cli.add_command(build_bootstrap_gcp)
app.cli.add_command(build_bootstrap_aws)
