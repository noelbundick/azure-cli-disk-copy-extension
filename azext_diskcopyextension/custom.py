import random
import re
import time

from knack.log import get_logger
from knack.util import CLIError

from .cli_utils import az_cli

logger = get_logger(__name__)
blob_regex = re.compile('https://(?P<storage_account>.*).blob.core.windows.net/(?P<container>.*)/(?P<blob>.*)')
# TODO: handle blob paths with slashes in the name
file_regex = re.compile(r'(?P<filename>.*)\.(?P<extension>.*)')

def assert_resource_group(resource_group_name):
  logger.info('Retrieving details for resource group %s', resource_group_name)
  resource_group = az_cli(['group', 'show',
                            '-n', resource_group_name])
  if not resource_group:
    raise CLIError('Resource group {0} not found'.format(resource_group_name))
  
  return resource_group

def assert_storage_account(storage_account_name):
  logger.info('Retrieving details for storage account %s', storage_account_name)
  storage_account = az_cli(['storage', 'account', 'list',
                            '--query', "[?name=='{0}'] | [0]".format(storage_account_name)])
  if not storage_account:
    raise CLIError('Storage account {0} not found'.format(storage_account_name))
  
  return storage_account

def get_disk(resource_group_name, disk_name):
  logger.info('Retrieving details for disk %s', disk_name)
  disk = az_cli(['disk', 'show',
                  '-n', disk_name,
                  '-g', resource_group_name])
  return disk

def create_blob_container(storage_account_name, container_name):
  logger.info('Creating container %s in storage account %s', container_name, storage_account_name)
  
  env = {}
  env['AZURE_STORAGE_ACCOUNT'] = storage_account_name
  blob_container = az_cli(['storage', 'container', 'create',
                          '-n', container_name], env=env)
  return blob_container

def create_blob_snapshot(blob_uri):
  logger.info('Creating blob snapshot for %s', blob_uri)
  
  blob_match = blob_regex.match(blob_uri)
  storage_account_name = blob_match.group('storage_account')
  storage_container = blob_match.group('container')
  blob_name = blob_match.group('blob')

  env = {}
  env['AZURE_STORAGE_ACCOUNT'] = storage_account_name
  blob_snapshot = az_cli(['storage', 'blob', 'snapshot',
                          '-c', storage_container,
                          '-n', blob_name], env=env)
  return blob_snapshot

def create_snapshot_from_blob(snapshot_name, resource_group_name, blob_uri):
  logger.info('Creating snapshot for %s', blob_uri)
  snapshot = az_cli(['snapshot', 'create',
                      '-n', snapshot_name,
                      '-g', resource_group_name,
                      '--tags', 'disk-copy-temp',
                      '--source', blob_uri])
  return snapshot

def create_snapshot_from_disk(snapshot_name, resource_group_name, disk_name):
  logger.info('Creating snapshot for %s', disk_name)
  snapshot = az_cli(['snapshot', 'create',
                      '-n', snapshot_name,
                      '-g', resource_group_name,
                      '--tags', 'disk-copy-temp',
                      '--source', disk_name])
  return snapshot

def create_disk_from_snapshot(snapshot_id, resource_group_name, disk_name, disk_sku):
  logger.info('Creating Managed Disk from snapshot %s', snapshot_id)
  disk = az_cli(['disk', 'create',
                  '-n', disk_name,
                  '-g', resource_group_name,
                  '--sku', disk_sku,
                  '--source', snapshot_id])
  return disk

def create_disk_from_blob(blob_uri, resource_group_name, disk_name, disk_sku):
  logger.info('Creating Managed Disk from blob %s', blob_uri)
  disk = az_cli(['disk', 'create',
                  '-n', disk_name,
                  '-g', resource_group_name,
                  '--sku', disk_sku,
                  '--source', blob_uri])
  return disk

def create_or_use_storage_account(storage_account_name, resource_group_name):
  logger.info('Retrieving details for storage account %s', storage_account_name)
  storage_account = az_cli(['storage', 'account', 'list',
                            '--query', "[?name=='{0}'] | [0]".format(storage_account_name)])
  if storage_account:
    return storage_account

  logger.info('Creating storage account %s', storage_account_name)
  storage_account = az_cli(['storage', 'account', 'create',
                            '-n', storage_account_name,
                            '-g', resource_group_name,
                            '--sku', 'Standard_LRS',
                            '--https-only', 'true',
                            '--tags', 'disk-copy-temp',
                            '--encryption-services', 'blob'])
  return storage_account

def start_blob_copy(source_resource_group, source_storage_account_name, source_container, source_blob, source_snapshot, 
                    target_storage_account_name):
  logger.info('Copying %s to %s', source_blob, target_storage_account_name)

  source_storage_account_key = get_storage_account_key(source_resource_group, source_storage_account_name)
  destination_container = source_container
  destination_blob = source_blob

  env = {}
  env['AZURE_STORAGE_ACCOUNT'] = target_storage_account_name
  blob_copy = az_cli(['storage', 'blob', 'copy', 'start',
                        '--source-account-name', source_storage_account_name,
                        '--source-account-key', source_storage_account_key,
                        '--source-container', source_container,
                        '--source-blob', source_blob,
                        '--source-snapshot', source_snapshot,
                        '--destination-container', destination_container,
                        '--destination-blob', destination_blob], env=env)
  return blob_copy

def get_storage_account_key(resource_group, storage_account):
  logger.info('Retrieving storage account key for %s in resource group %s', storage_account, resource_group)
  key = az_cli(['storage', 'account', 'keys', 'list',
                  '-g', resource_group,
                  '-n', storage_account])
  return key[0]['value']

def start_blob_copy_with_sas(snapshot_blob_sas, blob_name, target_storage_account_name, target_storage_account_key, target_storage_container_name):
  logger.info('Copying snapshot to %s in %s', blob_name, target_storage_account_name)
  blob_copy = az_cli(['storage', 'blob', 'copy', 'start',
                        '--source-uri', snapshot_blob_sas,
                        '-b', blob_name,
                        '--account-name', target_storage_account_name,
                        '--account-key', target_storage_account_key,
                        '-c', target_storage_container_name])
  return blob_copy

def get_storage_blob(blob_uri):
  blob_match = blob_regex.match(blob_uri)
  storage_account_name = blob_match.group('storage_account')
  storage_container = blob_match.group('container')
  blob_name = blob_match.group('blob')

  env = {}
  env['AZURE_STORAGE_ACCOUNT'] = storage_account_name
  blob = az_cli(['storage', 'blob', 'show',
                  '-c', storage_container,
                  '-n', blob_name], env=env)
  return blob

def get_sas_for_snapshot(snapshot_id):
  logger.info('Granting access to snapshot %s', snapshot_id)
  sas = az_cli(['snapshot', 'grant-access', '--duration-in-seconds', '86400',
                '--ids', snapshot_id])
  return sas['accessSas']

def revoke_sas_for_snapshot(snapshot_id):
  logger.info('Revoking access to snapshot %s', snapshot_id)
  az_cli(['snapshot', 'revoke-access',
          '--ids', snapshot_id])

def get_matching_disk_sku(source_storage_acct):
  source_storage_acct_tier = source_storage_acct['sku']['tier']
  if source_storage_acct_tier == 'Premium':
    disk_sku = 'Premium_LRS'
  else:
    disk_sku = 'Standard_LRS'
  return disk_sku

def delete_resource(resource_id):
  logger.info('Deleting resource %s', resource_id)
  az_cli(['resource', 'delete',
          '--ids', resource_id])

def delete_blob_snapshot(blob_uri, snapshot):
  logger.info('Deleting blob snapshot %s - %s', blob_uri, snapshot)
  blob_match = blob_regex.match(blob_uri)
  storage_account_name = blob_match.group('storage_account')
  storage_container = blob_match.group('container')
  blob_name = blob_match.group('blob')

  env = {}
  env['AZURE_STORAGE_ACCOUNT'] = storage_account_name
  az_cli(['storage', 'blob', 'delete',
          '-c', storage_container,
          '-n', blob_name,
          '--snapshot', snapshot], env=env)

def sameregion_copy_vhd_to_disk(source_vhd_uri, source_storage_acct, target_resource_group_name, target_disk_name, target_disk_sku):
  logger.info('Copying within the same region (%s)', source_storage_acct['location'])

  # Create a disk from a snapshot
  snapshot_name = 'snapshot_{0}'.format(random.randint(0, 100000))
  snapshot = create_snapshot_from_blob(snapshot_name, source_storage_acct['resourceGroup'], source_vhd_uri)
  disk = create_disk_from_snapshot(snapshot['id'], target_resource_group_name, target_disk_name, target_disk_sku)

  # Clean up snapshot
  delete_resource(snapshot['id'])

  return disk

def crossregion_copy_vhd_to_disk(source_vhd_uri, blob_match, source_storage_acct, 
                                  target_rg, target_disk_name, target_disk_sku,
                                  temp_storage_account_name=None):
  logger.info('Performing a cross-region copy (%s to %s)', source_storage_acct['location'], target_rg['location'])

  # Create a blob snapshot
  blob_snapshot = create_blob_snapshot(source_vhd_uri)

  # Use a temporary storage account to copy the snapshot
  temp_storage_created = False
  if temp_storage_account_name is None:
    # TODO: reuse a temp storage account if one isn't specified & one already exists in the target RG. Use tags
    temp_storage_account_name = 'diskcopytemp{0}'.format(random.randint(0, 100000))
    temp_storage_created = True
  temp_storage_acct = create_or_use_storage_account(temp_storage_account_name, target_rg['name'])
  create_blob_container(temp_storage_account_name, blob_match.group('container'))

  # Copy the blob across regions
  start_blob_copy(source_storage_acct['resourceGroup'], source_storage_acct['name'], blob_match.group('container'), blob_match.group('blob'), blob_snapshot['snapshot'], temp_storage_account_name)
  temp_blob_uri ='https://{0}.blob.core.windows.net/{1}/{2}'.format(temp_storage_account_name, blob_match.group('container'), blob_match.group('blob'))

  # TODO: for very long running copies, it might be better to register a function + event grid listener, but this works to start
  while True:
    temp_blob = get_storage_blob(temp_blob_uri)
    copy_status = temp_blob['properties']['copy']['status']
    copy_progress = temp_blob['properties']['copy']['progress']
    logger.info('%s: Waiting for %s to copy. Current status is %s: %s', time.ctime(), temp_blob['name'], copy_status, copy_progress)
    if copy_status == 'success':
      break
    time.sleep(5)

  # Create a disk from the temporary blob
  disk = create_disk_from_blob(temp_blob_uri, target_rg['name'], target_disk_name, target_disk_sku)

  # Clean up blob snapshot
  delete_blob_snapshot(source_vhd_uri, blob_snapshot['snapshot'])

  # Clean up temp storage account if auto-created
  if temp_storage_created:
    delete_resource(temp_storage_acct['id'])

  return disk

def copy_vhd_to_vhd(source_vhd_uri, target_storage_account_name, target_storage_container_name, target_vhd_name):
  raise NotImplementedError('VHD:VHD copy not implemented yet')
  
def copy_vhd_to_disk(source_vhd_uri, target_resource_group_name, 
                      target_disk_name=None, target_disk_sku=None, temp_storage_account_name=None):
  #TODO: Write map of (blob uri):(managed disk resource id) to output file if specified
  #TODO: move validation to a dedicated validator

  # Ensure source blob uri is valid
  blob_match = blob_regex.match(source_vhd_uri)
  if not blob_match:
    raise CLIError('--source-uri did not match format of a blob URI')

  # Use blob file name if target disk name wasn't specified
  if target_disk_name is None:
    file_match = file_regex.match(blob_match.group('blob'))
    target_disk_name = file_match.group('filename')

  # Ensure target disk does not already exist
  target_disk = get_disk(target_resource_group_name, target_disk_name)
  if target_disk:
    raise CLIError('{0} already exists in resource group {1}. Cannot overwrite an existing disk'.format(target_disk_name, target_resource_group_name))

  # Ensure that the target resource group does exist
  target_rg = assert_resource_group(target_resource_group_name)
  
  # Ensure that the source storage account exists
  source_storage_acct_name = blob_match.group('storage_account')
  source_storage_acct = assert_storage_account(source_storage_acct_name)

  # Use storage acct sku if disk sku wasn't specified
  if target_disk_sku is None:
    target_disk_sku = get_matching_disk_sku(source_storage_acct)
  
  # Ensure that a temp storage account exists if it was specified
  if temp_storage_account_name is not None:
    assert_storage_account(temp_storage_account_name)

  if source_storage_acct['location'].lower() == target_rg['location'].lower():
    disk = sameregion_copy_vhd_to_disk(source_vhd_uri, source_storage_acct, target_resource_group_name, target_disk_name, target_disk_sku)
  else:
    disk = crossregion_copy_vhd_to_disk(source_vhd_uri, blob_match, source_storage_acct, target_rg, target_disk_name, target_disk_sku, temp_storage_account_name)

  return disk

def sameregion_copy_disk_to_disk(source_rg, source_disk_name, target_resource_group_name, target_disk_name, target_disk_sku):
  logger.info('Copying within the same region (%s)', source_rg['location'])
  source_snapshot_name = 'snapshot_{0}'.format(random.randint(0, 100000))
  source_snapshot = create_snapshot_from_disk(source_snapshot_name, source_rg['name'], source_disk_name)
  disk = create_disk_from_snapshot(source_snapshot['id'], target_resource_group_name, target_disk_name, target_disk_sku)
  
  # Clean up snapshot
  delete_resource(source_snapshot['id'])

  return disk

def crossregion_copy_disk_to_disk(source_rg, source_disk_name, 
                                  target_rg, target_disk_name, target_disk_sku, 
                                  temp_storage_account_name=None):
  logger.info('Performing a cross-region copy (%s to %s)', source_rg['location'], target_rg['location'])

  # Create a snapshot
  source_snapshot_name = 'snapshot_{0}'.format(random.randint(0, 100000))
  source_snapshot = create_snapshot_from_disk(source_snapshot_name, source_rg['name'], source_disk_name)

  # Use a temporary storage account to copy the snapshot
  temp_storage_created = False
  if temp_storage_account_name is None:
    # TODO: reuse a temp storage account if one isn't specified & one already exists in the target RG. Use tags
    temp_storage_account_name = 'diskcopytemp{0}'.format(random.randint(0, 100000))
    temp_storage_created = True
  temp_storage_acct = create_or_use_storage_account(temp_storage_account_name, target_rg['name'])
  temp_blob_container_name = 'disks'
  create_blob_container(temp_storage_account_name, temp_blob_container_name)

  # Generate a limited-time SAS url to access the source snapshot
  sas_url = get_sas_for_snapshot(source_snapshot['id'])
  
  # Copy the blob across regions
  temp_storage_acct_key = get_storage_account_key(target_rg['name'], temp_storage_account_name)
  temp_blob_name = '{0}.vhd'.format(source_disk_name)
  start_blob_copy_with_sas(sas_url, temp_blob_name, temp_storage_account_name, temp_storage_acct_key, temp_blob_container_name)
  temp_blob_uri ='https://{0}.blob.core.windows.net/{1}/{2}'.format(temp_storage_account_name, temp_blob_container_name, temp_blob_name)

  # TODO: for very long running copies, it might be better to register a function + event grid listener, but this works to start
  while True:
    temp_blob = get_storage_blob(temp_blob_uri)
    copy_status = temp_blob['properties']['copy']['status']
    copy_progress = temp_blob['properties']['copy']['progress']
    logger.info('%s: Waiting for %s to copy. Current status is %s: %s', time.ctime(), temp_blob['name'], copy_status, copy_progress)
    if copy_status == 'success':
      break
    time.sleep(5)

  # Create a disk from the temporary blob
  disk = create_disk_from_blob(temp_blob_uri, target_rg['name'], target_disk_name, target_disk_sku)

  # Revoke SAS after copy
  revoke_sas_for_snapshot(source_snapshot['id'])

  # Clean up snapshot
  delete_resource(source_snapshot['id'])

  # Clean up temp storage account if auto-created
  if temp_storage_created:
    delete_resource(temp_storage_acct['id'])

  return disk

def copy_disk_to_vhd(source_resource_group_name, source_disk_name, target_storage_account_name, target_storage_container_name, target_vhd_name):
  raise NotImplementedError('Managed Disk:VHD copy not implemented yet')

def copy_disk_to_disk(source_resource_group_name, source_disk_name, target_resource_group_name, 
                      target_disk_name=None, target_disk_sku=None, temp_storage_account_name=None):
  #TODO: Write map of (source managed disk resource id):(target managed disk resource id) to output file if specified
  #TODO: move validation to a dedicated validator

  # Check that source and destination resource groups exist
  target_rg = assert_resource_group(target_resource_group_name)
  source_rg = assert_resource_group(source_resource_group_name)

  # Ensure source disk exists
  source_disk = get_disk(source_resource_group_name, source_disk_name)
  if not source_disk:
    raise CLIError('{0} does not exist in resource group {1}.'.format(source_disk_name, source_resource_group_name))

  # Use source disk name if target disk name wasn't specified
  if target_disk_name is None:
    target_disk_name = source_disk_name

  # Ensure target disk does not already exist
  target_disk = get_disk(target_resource_group_name, target_disk_name)
  if target_disk:
    raise CLIError('{0} already exists in resource group {1}. Cannot overwrite an existing disk'.format(target_disk_name, target_resource_group_name))

  # Use source disk sku if target disk sku wasn't specified
  if target_disk_sku is None:
    target_disk_sku = source_disk['sku']['name']

  # Ensure that a temp storage account exists if it was specified
  if temp_storage_account_name is not None:
    assert_storage_account(temp_storage_account_name)
    
  if source_rg['location'].lower() == target_rg['location'].lower():
    disk = sameregion_copy_disk_to_disk(source_rg, source_disk_name, target_resource_group_name, target_disk_name, target_disk_sku)
  else:
    disk = crossregion_copy_disk_to_disk(source_rg, source_disk_name, target_rg, target_disk_name, target_disk_sku, temp_storage_account_name)

  return disk

