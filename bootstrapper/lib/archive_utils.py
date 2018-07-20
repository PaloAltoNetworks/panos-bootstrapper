import logging
import os
import shutil

import boto3
from botocore.exceptions import ClientError
import uuid

from . import cache_utils

_archive_dir = '/tmp/bootstrapper/archives'
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
    for package_type in ['appthreat', 'antivirus', 'wildfire']:
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


def create_s3_bucket(files, bucket_name, location, access_key, secret_key):
    client = boto3.client('s3',
                          region_name=location,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)

    # aws enforces some rules on bucket names
    bucket_name = bucket_name.lower() + "-" + str(uuid.uuid4())

    print('Checking for existing buckets with name: {}'.format(bucket_name))
    found = False
    buckets = client.list_buckets()
    print(buckets)
    for bucket in buckets['Buckets']:
        if bucket['Name'] == bucket_name:
            found = True
            print('Found existing bucket!')
            break

    if not found:
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
        except ClientError as ce:
            print('Error creating bucket!')
            print(ce)
            return str(ce)

    print('creating config')
    response = client.put_object(Bucket=bucket_name, Body='', Key='config/')
    print(response)
    print('creating content')
    response = client.put_object(Bucket=bucket_name, Body='', Key='content/')
    print(response)
    print('creating software')
    response = client.put_object( Bucket=bucket_name, Body='', Key='software/')
    print(response)
    print('creating license')
    response = client.put_object( Bucket=bucket_name, Body='', Key='license/')
    print(response)

    for f in files:
        contents = cache_utils.get(files[f]['key'])
        key = files[f]['archive_path'] + '/' + f
        response = client.put_object( Bucket=bucket_name, Body=contents, Key=key)
        print(response)

    print('all done')
    return 'S3 bucket {} created successfully'.format(bucket_name)


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
