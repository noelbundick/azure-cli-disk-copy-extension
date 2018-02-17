import random

import re
vhd_regex=re.compile('https://(?P<storage_account>.*).blob.core.windows.net/(?P<container>.*)/(?P<blob>.*)')

from .cli_utils import az_cli

from knack.util import CLIError
from knack.log import get_logger
logger = get_logger(__name__)

def get_resource_group(resource_group_name):
  logger.info('Retrieving details for resource group %s', resource_group_name)
  resource_group = az_cli(['group', 'show',
                            '-n', resource_group_name])
  if not resource_group:
    raise CLIError('Resource group {0} not found'.format(resource_group_name))
  
  return resource_group

def get_storage_account(storage_account_name):
  logger.info('Retrieving details for storage account %s', storage_account_name)
  storage_account = az_cli(['storage', 'account', 'list',
                            '--query', "[?name=='{0}'] | [0]".format(storage_account_name)])
  if not storage_account:
    raise CLIError('Storage account {0} not found'.format(storage_account_name))
  
  return storage_account

def create_snapshot_from_blob(snapshot_name, resource_group_name, blob_uri):
  logger.info('Creating snapshot for %s', blob_uri)
  #TODO: tag snapshot as transient
  snapshot = az_cli(['snapshot', 'create',
                      '-n', snapshot_name,
                      '-g', resource_group_name,
                      '--source', blob_uri])
  return snapshot

def create_disk_from_snapshot(snapshot_id, resource_group_name, disk_name):
  logger.info('Creating Managed Disk from snapshot %s', snapshot_id)
  disk = az_cli(['disk', 'create',
                  '-n', disk_name,
                  '-g', resource_group_name,
                  '--source', snapshot_id])
  return disk

def copy_vhd_to_vhd(source_vhd_uri, target_storage_account_name, target_storage_container_name, target_vhd_name):
  raise NotImplementedError('VHD:VHD copy not implemented yet')
  
def copy_vhd_to_disk(source_vhd_uri, target_resource_group_name, target_disk_name):
  #TODO: move these to a validator
  target_rg = get_resource_group(target_resource_group_name)
  
  vhd_match = vhd_regex.match(source_vhd_uri)
  if not vhd_match:
    raise CLIError('--source-uri did not match format of a blob URL')
  
  #TODO: Ensure target disk does not already exist
  
  source_storage_acct_name = vhd_match.group('storage_account')
  source_storage_acct = get_storage_account(source_storage_acct_name)

  if source_storage_acct['location'].lower() == target_rg['location'].lower():
    logger.info('Copying within the same region (%s)', source_storage_acct['location'])
    snapshot_name = 'snapshot_{0}'.format(random.randint(0, 100000))
    snapshot = create_snapshot_from_blob(snapshot_name, source_storage_acct['resourceGroup'], source_vhd_uri)
    disk = create_disk_from_snapshot(snapshot['id'], target_resource_group_name, target_disk_name)
    return disk
  else:
    logger.info('Performing a cross-region copy (%s to %s)', source_storage_acct['location'], target_rg['location'])
    source_container = vhd_match.group('container')
    source_blob = vhd_match.group('blob')
    logger.error('VHD:Managed Disk copy not implemented yet')

def copy_disk_to_vhd(source_resource_group_name, source_disk_name, target_storage_account_name, target_storage_container_name, target_vhd_name):
  raise NotImplementedError('Managed Disk:VHD copy not implemented yet')

def copy_disk_to_disk(source_resource_group_name, source_disk_name, target_resource_group_name, target_disk_name):
  raise NotImplementedError('Managed Disk:Managed Disk copy not implemented yet')
