import random
import time

import re
blob_regex = re.compile('https://(?P<storage_account>.*).blob.core.windows.net/(?P<container>.*)/(?P<blob>.*)')

from .cli_utils import az_cli

from knack.util import CLIError
from knack.log import get_logger
logger = get_logger(__name__)

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
  #TODO: make sure to clean up snapshot
  blob_snapshot = az_cli(['storage', 'blob', 'snapshot',
                          '-c', storage_container,
                          '-n', blob_name], env=env)
  return blob_snapshot

def create_snapshot_from_blob(snapshot_name, resource_group_name, blob_uri):
  logger.info('Creating snapshot for %s', blob_uri)
  #TODO: tag snapshot as transient
  snapshot = az_cli(['snapshot', 'create',
                      '-n', snapshot_name,
                      '-g', resource_group_name,
                      '--source', blob_uri])
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
  # DESTINATION_MANAGED_DISK=${SOURCE_BLOB%.vhd}     # Name the managed disk the same as the source blob
  # DESTINATION_MANAGED_DISK_ID=$(az disk create -n $DESTINATION_MANAGED_DISK -g $DESTINATION_RESOURCEGROUP --source $DESTINATION_MANAGED_DISK_SOURCE --query 'id' -o tsv)

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
                            '--encryption-services', 'blob'])
  return storage_account

def start_blob_copy(source_resource_group, source_storage_account_name, source_container, source_blob, source_snapshot, 
                    target_storage_account_name):
  logger.info('Copying %s to %s', source_blob, target_storage_account_name)
  
  source_storage_account_keys = az_cli(['storage', 'account', 'keys', 'list',
                                        '-n', source_storage_account_name,
                                        '-g', source_resource_group])
  source_storage_account_key = source_storage_account_keys[0]['value']
  
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

def get_storage_blob(blob_uri):
  # BLOB_COPY_STATUS=$(az storage blob show --account-name $DESTINATION_STORAGEACCOUNT --account-key $DESTINATION_STORAGEACCOUNT_KEY -c $DESTINATION_STORAGEACCOUNT_CONTAINER -n $SOURCE_BLOB --query 'properties.copy.status' -o tsv)

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

def copy_vhd_to_vhd(source_vhd_uri, target_storage_account_name, target_storage_container_name, target_vhd_name):
  raise NotImplementedError('VHD:VHD copy not implemented yet')
  
def copy_vhd_to_disk(source_vhd_uri, target_resource_group_name, target_disk_name):
  #TODO: allow optional standard/premium
  #TODO: allow optional temp storage acct in target region

  #TODO: move these to a validator
  blob_match = blob_regex.match(source_vhd_uri)
  if not blob_match:
    raise CLIError('--source-uri did not match format of a blob URL')

  target_disk = get_disk(target_resource_group_name, target_disk_name)
  if target_disk:
    raise CLIError('{0} already exists in resource group {1}. Cannot overwrite an existing disk'.format(target_disk_name, target_resource_group_name))

  target_rg = assert_resource_group(target_resource_group_name)
  
  source_storage_acct_name = blob_match.group('storage_account')
  source_storage_acct = assert_storage_account(source_storage_acct_name)

  # Create disk with same tier as storage account
  source_storage_acct_tier = source_storage_acct['sku']['tier']
  if source_storage_acct_tier == 'Premium':
    target_disk_sku = 'Premium_LRS'
  else:
    target_disk_sku = 'Standard_LRS'

  if source_storage_acct['location'].lower() == target_rg['location'].lower():
    logger.info('Copying within the same region (%s)', source_storage_acct['location'])

    # Create a disk from a snapshot
    snapshot_name = 'snapshot_{0}'.format(random.randint(0, 100000))
    snapshot = create_snapshot_from_blob(snapshot_name, source_storage_acct['resourceGroup'], source_vhd_uri)
    disk = create_disk_from_snapshot(snapshot['id'], target_resource_group_name, target_disk_name, target_disk_sku)
    return disk
  else:
    logger.info('Performing a cross-region copy (%s to %s)', source_storage_acct['location'], target_rg['location'])

    # Create a blob snapshot
    blob_snapshot = create_blob_snapshot(source_vhd_uri)

    # Copy the blob snapshot to a temporary storage account
    # TODO: reuse a temp storage account if one isn't specified & one already exists in the target RG. Use tags
    temp_storage_account_name = 'diskcopytemp{0}'.format(random.randint(0, 100000))
    temp_storage_account = create_or_use_storage_account(temp_storage_account_name, target_resource_group_name)
    create_blob_container(temp_storage_account_name, blob_match.group('container'))
    start_blob_copy(source_storage_acct['resourceGroup'], source_storage_acct_name, blob_match.group('container'), blob_match.group('blob'), blob_snapshot['snapshot'], temp_storage_account_name)
    temp_blob_uri ='https://{0}.blob.core.windows.net/{1}/{2}'.format(temp_storage_account_name, blob_match.group('container'), blob_match.group('blob'))
    # TODO: for very long running copies, it might be better to register a function + event grid listener, but this works to start
    while True:
      temp_blob = get_storage_blob(temp_blob_uri)
      copy_status = temp_blob['properties']['copy']['status']
      logger.info('%s: Waiting for %s to copy. Current status is %s', time.ctime(), temp_blob['name'], copy_status)
      if copy_status == 'success':
        break
      time.sleep(5)

    # Create a disk from the temporary blob
    disk = create_disk_from_blob(temp_blob_uri, target_resource_group_name, target_disk_name, target_disk_sku)
    return disk

  # # Write map of VHD->managed disk to OUTPUT_FILE_PATH
  # echo "$VHD:$DESTINATION_MANAGED_DISK_ID" >> $OUTPUT_FILE_PATH
  #logger.error('VHD:Managed Disk copy not implemented yet')

def copy_disk_to_vhd(source_resource_group_name, source_disk_name, target_storage_account_name, target_storage_container_name, target_vhd_name):
  raise NotImplementedError('Managed Disk:VHD copy not implemented yet')

def copy_disk_to_disk(source_resource_group_name, source_disk_name, target_resource_group_name, target_disk_name):
  #TODO: Ensure target disk does not already exist
  #!/bin/bash

  # #TODO: create named args
  # SOURCE_DISK_PATHS=$1
  # DESTINATION_RESOURCEGROUP=$2
  # OUTPUT_FILE_PATH=$3

  # echo "SOURCE_DISK_PATHS: $SOURCE_DISK_PATHS"
  # echo "DESTINATION_RESOURCEGROUP: $DESTINATION_RESOURCEGROUP"
  # echo "OUTPUT_FILE_PATH: $OUTPUT_FILE_PATH"

  # # Check that 'az' is configured
  # SUBSCRIPTION_NAME=`az account show --query name`
  # if [ $? == "0" ]; then
  #   echo "Running in $SUBSCRIPTION_NAME"
  # else
  #   echo "'az' does not have a subscription set. Do you need to run 'az login'?"
  #   exit 1 
  # fi

  # # Check that destination RG exists
  # DESTINATION_RESOURCEGROUP_REGION=`az group show -n $DESTINATION_RESOURCEGROUP --query location -o tsv`
  # if [ ! $DESTINATION_RESOURCEGROUP_REGION ]; then
  #   echo "Destination resource group ($DESTINATION_RESOURCEGROUP) not found"
  #   exit 1
  # fi

  # DISKS=($SOURCE_DISK_PATHS)
  # DISKCOUNT=${#DISKS[@]}
  # echo "There are $DISKCOUNT disks to migrate"

  # for (( i=0; i<$DISKCOUNT; i++))
  # do
  #   DISK=${DISKS[$i]}

  #   # Make sure user gets a snapshot warning & wants to proceed
  #   echo -e "\nWARNING!\nThis script will take a snapshot of your disk. All writes received after the snapshot is taken will remain in the source disk but will not be present in the target disk. We recommend stopping writes, or if not possible, syncing data from the source disk to the destination disk after it has been mounted (via sftp, rsync, etc)\n"
  #   echo -e "\nWARNING!\nIf your source disk is in a different region than your destination resource group, this script will copy them across a regions. This operation will incur outbound data charges\n"
  #   read -r -p "Do you want to migrate $DISK? [y/N] " response
  #   if ! [[ $response =~ ^[yY]$ ]]; then
  #     echo "Skipping $DISK"
  #     continue
  #   fi

  #   SOURCE_DISK_NAME=$(az disk show --ids $DISK --query name -o tsv)
  #   SOURCE_DISK_REGION=$(az disk show --ids $DISK --query location -o tsv)
  #   SOURCE_DISK_GROUP=$(az disk show --ids $DISK --query resourceGroup -o tsv)
  #   SOURCE_SNAPSHOT_NAME="snapshot-$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-z0-9' | fold -w 10 | head -n 1)"
  #   echo "Creating snapshot for disk $DISK"
  #   az snapshot create -n $SOURCE_SNAPSHOT_NAME -g $SOURCE_DISK_GROUP --source $DISK -o tsv
  #   SOURCE_SNAPSHOT_ID=$(az snapshot show -n $SOURCE_SNAPSHOT_NAME -g $SOURCE_DISK_GROUP --query 'id' -o tsv)

  #   # Detect region move (based on disk and target RG name)
  #   if [[ $SOURCE_DISK_REGION != $DESTINATION_RESOURCEGROUP_REGION ]]; then 
  #     MIGRATE_REGIONS=true
  #   fi

  #   # When moving between regions, we need to copy the snapshot to a storage account in the destination region
  #   if [ "$MIGRATE_REGIONS" = true ]; then
  #     echo "Migrating from $SOURCE_DISK_REGION to $DESTINATION_RESOURCEGROUP_REGION"
      
  #     if [ "$DESTINATION_STORAGE_ACCOUNT_CREATED" = true ]; then
  #       echo "Destination storage account $DESTINATION_STORAGEACCOUNT already created"
  #     else
  #       # Create dynamically named storage account to copy blob
  #       #TODO: allow specifying temp storage acct
  #       echo "Creating storage account $DESTINATION_STORAGEACCOUNT"
  #       DESTINATION_STORAGEACCOUNT="diskmigration$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-z0-9' | fold -w 10 | head -n 1)"
  #       az storage account create -n $DESTINATION_STORAGEACCOUNT -g $DESTINATION_RESOURCEGROUP -l $DESTINATION_RESOURCEGROUP_REGION --sku Standard_LRS
  #       DESTINATION_STORAGE_ACCOUNT_CREATED=true
  #       DESTINATION_STORAGEACCOUNT_KEY=$(az storage account keys list -g $DESTINATION_RESOURCEGROUP -n $DESTINATION_STORAGEACCOUNT --query '[0].value' -o tsv)

  #       DESTINATION_STORAGEACCOUNT_CONTAINER=temp
  #       az storage container create --name $DESTINATION_STORAGEACCOUNT_CONTAINER --account-key $DESTINATION_STORAGEACCOUNT_KEY --account-name $DESTINATION_STORAGEACCOUNT
  #     fi

  #     # Copy snapshot to new blob (if moving regions)
  #     echo "Copying disk snapshot $SOURCE_SNAPSHOT_ID"

  #     #TODO: revoke access after copying
  #     SOURCE_SNAPSHOT_BLOB_SAS=$(az snapshot grant-access --duration-in-seconds 86400 --ids $SOURCE_SNAPSHOT_ID --query accessSas -o tsv)
  #     TEMP_BLOB_NAME="$SOURCE_DISK_NAME.vhd"

  #     az storage blob copy start \
  #       --source-uri $SOURCE_SNAPSHOT_BLOB_SAS \
  #       -b $TEMP_BLOB_NAME \
  #       --account-name $DESTINATION_STORAGEACCOUNT \
  #       --account-key $DESTINATION_STORAGEACCOUNT_KEY \
  #       -c $DESTINATION_STORAGEACCOUNT_CONTAINER
      
  #     DESTINATION_MANAGED_DISK_SOURCE="https://$DESTINATION_STORAGEACCOUNT.blob.core.windows.net/$DESTINATION_STORAGEACCOUNT_CONTAINER/$TEMP_BLOB_NAME"

  #     # Wait for blob copy to finish
  #     BLOB_COPY_STATUS=$(az storage blob show --account-name $DESTINATION_STORAGEACCOUNT --account-key $DESTINATION_STORAGEACCOUNT_KEY -c $DESTINATION_STORAGEACCOUNT_CONTAINER -n $TEMP_BLOB_NAME --query 'properties.copy.status' -o tsv)
  #     while [ "$BLOB_COPY_STATUS" != "success" ]; do
  #       echo "$(date +"%F %T%z") Waiting for $TEMP_BLOB_NAME to copy. Current status is $BLOB_COPY_STATUS"
  #       sleep 5
  #       BLOB_COPY_STATUS=$(az storage blob show --account-name $DESTINATION_STORAGEACCOUNT --account-key $DESTINATION_STORAGEACCOUNT_KEY -c $DESTINATION_STORAGEACCOUNT_CONTAINER -n $TEMP_BLOB_NAME --query 'properties.copy.status' -o tsv)
  #     done
  #   else
  #     DESTINATION_MANAGED_DISK_SOURCE=$SOURCE_SNAPSHOT_ID
  #   fi

  #   echo "Creating Managed Disk from $SOURCE_DISK_NAME"
  #   DESTINATION_MANAGED_DISK=${SOURCE_DISK_NAME}     # Name the new managed disk the same as the source
  #   DESTINATION_MANAGED_DISK_ID=$(az disk create -n $DESTINATION_MANAGED_DISK -g $DESTINATION_RESOURCEGROUP --source $DESTINATION_MANAGED_DISK_SOURCE --query 'id' -o tsv)

  #   # Write map of managed disk->managed disk to OUTPUT_FILE_PATH
  #   echo "$DISK:$DESTINATION_MANAGED_DISK_ID" >> $OUTPUT_FILE_PATH
  # done

  # # Cleanup temp files (copied blob if moving regions, remove snapshots)
  # echo -e "ATTENTION!\nFor safety, this script doesn't delete anything. You'll need to do some cleanup to remove the temporary resources that were created. This includes blob snapshots in the source storage account(s) and temporary diskmigration* storage accounts"
  raise NotImplementedError('Managed Disk:Managed Disk copy not implemented yet')
