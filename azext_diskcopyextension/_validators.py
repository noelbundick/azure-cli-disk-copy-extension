from knack.util import CLIError

def validate_disk_copy_source(cmd, namespace):
  if namespace.source_vhd_uri and (namespace.source_resource_group_name or namespace.source_disk_name):
    raise CLIError('Only one source can be specified (VHD blob or Managed Disk)')

  elif namespace.source_vhd_uri:
    namespace.source_type = 'vhd'
  
  elif namespace.source_resource_group_name or namespace.source_disk_name:
    if namespace.source_resource_group_name and namespace.source_disk_name:
      namespace.source_type = 'disk'
    else:
      raise CLIError('You must specify both --source-resource-group and --source-disk-name when using a Managed Disk source')
  
  else:
    raise CLIError('You must specify a source (VHD or Managed Disk) to copy')

def validate_disk_copy_target(cmd, namespace):
  if ((namespace.target_storage_account_name or namespace.target_storage_container_name or namespace.target_vhd_name)
      and (namespace.target_resource_group_name or namespace.target_disk_name)):
    raise CLIError('Only one target can be specified (VHD blob or Managed Disk)')
  
  elif namespace.target_storage_account_name or namespace.target_storage_container_name or namespace.target_vhd_name:
    if namespace.target_storage_account_name and namespace.target_storage_container_name and namespace.target_vhd_name:
      namespace.target_type = 'vhd'
    else:
      raise CLIError('You must specify --target-storage-account-name, --target-storage-container, and --target-vhd-name when using a VHD target')

  elif namespace.target_resource_group_name or namespace.target_disk_name:
    if namespace.target_resource_group_name and namespace.target_disk_name:
      namespace.target_type = 'disk'
    else:
      raise CLIError('You must specify --target-resource-group-name and --target-disk-name when using a Managed Disk target')
  
  else:
    raise CLIError('You must specify a target (VHD or Managed Disk)')

def validate_disk_copy(cmd, namespace):
  validate_disk_copy_source(cmd, namespace)
  validate_disk_copy_target(cmd, namespace)
  