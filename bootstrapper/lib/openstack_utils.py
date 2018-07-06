
# these keys are required to be present in the POSTed JSON
openstack_required_keys = {'management_ip', 'outside_ip', 'inside_ip'}

# these keys are optional, they can override the defaults if desired
openstack_keys = {'hostname', 'image_name', 'image_flavor',
                  'management_network', 'management_subnet',
                  'outside_network', 'outside_subnet',
                  'inside_network', 'inside_subnet'}


def verify_data(posted_json):
    # verify we have the required keys first
    if not openstack_required_keys.issubset(posted_json):
        return False

    return True


def generate_config(defaults, posted_json):
    """
    Generates a simple configuration object that contains the default values unless overridden in the
    data passed from the user
    :param defaults: object containing all default values
    :param posted_json: JSON payload from the user
    :return: dict
    """
    # create the openstack config object that will be used to populate the HEAT template
    openstack_config = {}

    # populate with defaults if they exist
    if 'openstack' in defaults:
        openstack_config.update(defaults['openstack'])

    # push all the required keys - should have already been validated
    for k in openstack_required_keys:
        openstack_config[k] = posted_json.get(k, None)

    # push all the optional keys if they exist
    for k in openstack_keys:
        if k in posted_json:
            openstack_config[k] = posted_json[k]

    return openstack_config


