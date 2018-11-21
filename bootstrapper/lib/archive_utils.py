import logging
import os
import shutil
import tarfile
import uuid

import boto3
from azure.storage.file import FileService

from azure.common import AzureException, AzureHttpError

from botocore.exceptions import ClientError
from google.auth.exceptions import GoogleAuthError
from google.cloud import storage
from google.oauth2.credentials import Credentials

from google.api_core.exceptions import BadRequest

from . import cache_utils

_archive_dir = '/var/tmp/bootstrapper'
_content_update_dir = '/var/tmp/content_updates/'

log = logging.getLogger(__name__)


def _create_archive_directory(files, archive_name):
    """
    Creates a directory structure from the given files dict
    :param files: A dict of files with the following structure:
        files = {
                    "FILENAME":
                    {
                        "archive_path": "RELATIVE_PATH"
                        "key": "CACHE_KEY_TO_CONTENTS"
                    }
                }
    Each key of the dict is a filename that will be created. The contents of the file will be retrieved from the cache
    system using the cache_utils library. The file will be placed in the relative path given by the 'archive_path'
    :param archive_name: the name of the archive to create
    :return: path to the newly created directory or None on error
    """
    log.info('_create_archive_directory with name %s' % archive_name)
    archive_file_path = os.path.join(_archive_dir, archive_name)

    try:
        if not os.path.exists(archive_file_path):
            os.makedirs(archive_file_path)
    except OSError:
        log.error('Could not create the initial archive directory')
        return None

    # create skeleton structure for PanOS devices
    # if we ever need to build packages that are not destined for panos devices, then this should be
    # refactored and the skeleton dirs should be done in the build_base_config function
    config_dir = os.path.join(_archive_dir, archive_name, 'config')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    content_dir = os.path.join(_archive_dir, archive_name, 'content')
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)

    # iterate through the content updates that is needed for licensed features
    for package_type in ['appthreat', 'antivirus', 'wildfire', 'wildfire2', 'app']:
        # grab the latest version in the update cache dir (populated manually or via another container volume mount)
        latest_update = check_latest_update(package_type)
        # we have an update
        if latest_update is not None:
            # craft the absolute path to where we want to copy the file
            destination_file = os.path.join(content_dir, os.path.basename(latest_update))
            # copy the file from the content cache dir into the archive dir
            shutil.copyfile(latest_update, destination_file)

    software_dir = os.path.join(_archive_dir, archive_name, 'software')
    if not os.path.exists(software_dir):
        os.makedirs(software_dir)

    license_dir = os.path.join(_archive_dir, archive_name, 'license')
    if not os.path.exists(license_dir):
        os.makedirs(license_dir)

    for f in files:
        archive_file_dir = os.path.join(_archive_dir, archive_name, files[f]['archive_path'])
        archive_file = os.path.abspath(os.path.join(archive_file_dir, f))

        try:
            if not os.path.exists(archive_file_dir):
                os.makedirs(archive_file_dir)
        except OSError:
            log.error('Could not create archive subdirectory')
            return None
        try:
            with open(os.path.abspath(archive_file), 'w') as tmp_file:
                contents = cache_utils.get(files[f]['key'])
                tmp_file.write(contents)
        except OSError:
            log.error('Could not write archive file into directory')
            return None

    return archive_file_path


def create_archive(files, archive_name):
    """
    Creates a zip file of the desired files with the desired structure.
    :param files: A dict of files with the following structure:
        files = {
                    "FILENAME":
                    {
                        "archive_path": "RELATIVE_PATH"
                        "key": "CACHE_KEY_TO_CONTENTS"
                    }
                }
    Each key of the dict is a filename that will be created. The contents of the file will be retrieved from the cache
    system using the cache_utils library. The file will be placed in the relative path given by the 'archive_path'
    :param archive_name: the name of the archive to create
    :return: path to the newly created archive or None on error
    """

    archive_file_path = _create_archive_directory(files, archive_name)
    if archive_file_path is None:
        log.error('Could not create archive directory structure')
        return None

    try:
        zip_file = shutil.make_archive(archive_file_path, 'zip', root_dir=archive_file_path)
    except [ValueError, OSError]:
        log.error('Could not make zip archive')
        return None

    log.info('Created %s successfully' % zip_file)
    return zip_file


def create_iso(files, archive_name):
    """
    Creates an ISO image of the desired files with the desired structure.
    :param files: A dict of files with the following structure:
        files = {
                    "FILENAME":
                    {
                        "archive_path": "RELATIVE_PATH"
                        "key": "CACHE_KEY_TO_CONTENTS"
                    }
                }
    Each key of the dict is a filename that will be created. The contents of the file will be retrieved from the cache
    system using the cache_utils library. The file will be placed in the relative path given by the 'archive_path'
    :param archive_name: the name of the archive to create
    :return: path to the newly created ISO image or None on error
    """

    archive_file_path = _create_archive_directory(files, archive_name)
    if archive_file_path is None:
        log.error('Could not create archive directory structure')
        return None

    iso_image = archive_file_path + '.iso'
    try:
        rv = os.system(
            'mkisofs -J -R -v -V bootstrap -A bootstrap -ldots -l '
            '-allow-lowercase -allow-multidot -o %s %s' % (iso_image, archive_file_path)
        )
        if rv != 0:
            print("Cold not make ISO Image!")
            return None

    except [ValueError, OSError]:
        print("Could not make ISO Image")
        log.error('Could not make ISO image')
        return None

    log.info('Created %s successfully' % iso_image)
    return iso_image


def create_tgz(files, archive_name):
    """
    Creates an gzipped tarball of the desired files with the desired structure.
    :param files: A dict of files with the following structure:
        files = {
                    "FILENAME":
                    {
                        "archive_path": "RELATIVE_PATH"
                        "key": "CACHE_KEY_TO_CONTENTS"
                    }
                }
    Each key of the dict is a filename that will be created. The contents of the file will be retrieved from the cache
    system using the cache_utils library. The file will be placed in the relative path given by the 'archive_path'
    :param archive_name: the name of the archive to create
    :return: path to the newly created tgz archive or None on error
    """

    archive_file_path = _create_archive_directory(files, archive_name)
    if archive_file_path is None:
        log.error('Could not create archive directory structure')
        return None

    tar_file = archive_file_path + '.tgz'
    try:
        rv = os.system(
            f'tar -C {archive_file_path} -czvf {tar_file} .'
        )
        if rv != 0:
            print("Cold not make ISO Image!")
            return None

    except [ValueError, OSError]:
        print("Could not make ISO Image")
        log.error('Could not make ISO image')
        return None

    # tar_file = archive_file_path + '.tgz'
    # tar = tarfile.open(tar_file, "w:gz", compresslevel=1)
    # tar.add(archive_file_path, arcname='./')

    log.info('Created %s successfully' % tar_file)
    return tar_file


def create_s3_bucket(files, bucket_prefix, location, access_key, secret_key):

    archive_file_path = _create_archive_directory(files, bucket_prefix)

    bucket_name = bucket_prefix.lower() + "-" + str(uuid.uuid4())

    try:
        client = boto3.client('s3',
                              region_name=location,
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)

    except ClientError as ce:
        print('Error: authenticating to AWS')
        return str(ce)

    try:
        print('creating bucket {}'.format(bucket_name))
        response = client.create_bucket(
            ACL='private',
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': location
            },
        )
        print(response)

        for d in ['config', 'content', 'software', 'license']:
            print('creating directory of type: {}'.format(d))
            top_level_dir = '{}/'.format(d)
            response = client.put_object(Bucket=bucket_name, Body='', Key=top_level_dir)
            print(response)

            d_dir = os.path.join(archive_file_path, d)
            for filename in os.listdir(d_dir):
                print('creating file: {0}'.format(filename))
                key = '{}/{}'.format(d, filename)
                file_path = os.path.join(d_dir, filename)
                with open(file_path, 'rb') as file_object:
                    contents = file_object.read()
                    print('{} {} {}'.format(file_path, bucket_name, key))
                    response = client.put_object(Bucket=bucket_name, Body=contents, Key=key)
                    print(response)

    except IOError as ioe:
        print(ioe)
        return 'Error: Could not read local files for upload'

    except ClientError as ce:
        print('Error creating bucket!')
        print(ce)
        return str(ce)

    print('all done')
    return 'S3 bucket {} created successfully'.format(bucket_name)


def create_azure_fileshare(files, share_prefix, account_name, account_key):
    # generate a unique share name to avoid overlaps in shared infra
    share_name = "{0}-{1}".format(share_prefix.lower(), str(uuid.uuid4()))
    print('using share_name of: {}'.format(share_name))

    archive_file_path = _create_archive_directory(files, share_prefix)

    try:
        file_service = FileService(account_name=account_name, account_key=account_key)

        # print(file_service)
        if not file_service.exists(share_name):
            file_service.create_share(share_name)

        for d in ['config', 'content', 'software', 'license']:
            print('creating directory of type: {}'.format(d))
            if not file_service.exists(share_name, directory_name=d):
                file_service.create_directory(share_name, d)

            d_dir = os.path.join(archive_file_path, d)
            for filename in os.listdir(d_dir):
                print('creating file: {0}'.format(filename))
                file_service.create_file_from_path(share_name, d, filename, os.path.join(d_dir, filename))

    except AttributeError as ae:
        # this can be returned on bad auth information
        print(ae)
        return "Authentication or other error creating bootstrap file_share in Azure"

    except AzureException as ahe:
        print(ahe)
        return str(ahe)
    except ValueError as ve:
        print(ve)
        return str(ve)

    print('all done')
    return 'Azure file-share {} created successfully'.format(share_name)


def create_gcp_bucket(files, bucket_prefix, project_id, access_token):

    archive_file_path = _create_archive_directory(files, bucket_prefix)

    try:
        credentials = Credentials(access_token)
        client = storage.Client(project_id, credentials)

        bucket_name = '{0}-{1}'.format(bucket_prefix, uuid.uuid4())
        bucket = client.create_bucket(bucket_name)

    except GoogleAuthError as gae:
        print(gae)
        return 'Could not authenticate to GCP!'

    except BadRequest as br:
        print(br)
        return str(br)

    except ValueError as ve:
        print(ve)
        return str(ve)

    for d in ['config', 'content', 'software', 'license']:
        print('creating directory of type: {}'.format(d))
        d_dir_blob = bucket.blob('{}/'.format(d))
        d_dir_blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')
        d_dir = os.path.join(archive_file_path, d)
        for filename in os.listdir(d_dir):
            print('creating file: {0}'.format(filename))
            d_dir_file = bucket.blob('{0}/{1}'.format(d, filename))
            d_dir_file.upload_from_filename(os.path.join(d_dir, filename))

    print('all done')
    return 'GCP Bucket {} created successfully'.format(bucket_name)


def check_latest_update(package_type):
    """
    Checks the content update directory for the specified package type (appthread, contents, etc)
    If files are found, it will return a path to the file with the highest sequence number
    :param package_type: appthreat, contents, wildfire, etc
    :return: absolute path to the file with the highest sequence number or None if no updates are available
    """
    package_dir = os.path.join(_content_update_dir, package_type)
    if not os.path.exists(package_dir):
        # there's nothing here to see, move along
        return None

    all_files = os.listdir(package_dir)
    if len(all_files) > 0:
        all_files.sort()
        latest = all_files[-1]
        # return the full path here
        return os.path.join(package_dir, latest)
    else:
        return None
