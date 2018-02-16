def copy_vhd_to_vhd(source_vhd_uri, target_storage_account_name, target_storage_container_name, target_vhd_name):
  raise NotImplementedError('VHD:VHD copy not implemented yet')
  
def copy_vhd_to_disk(source_vhd_uri, target_resource_group_name, target_disk_name):
  raise NotImplementedError('VHD:Managed Disk copy not implemented yet')

def copy_disk_to_vhd(source_resource_group_name, source_disk_name, target_storage_account_name, target_storage_container_name, target_vhd_name):
  raise NotImplementedError('Managed Disk:VHD copy not implemented yet')

def copy_disk_to_disk(source_resource_group_name, source_disk_name, target_resource_group_name, target_disk_name):
  raise NotImplementedError('Managed Disk:Managed Disk copy not implemented yet')

def disk_copy(source_type, target_type,
              source_vhd_uri=None,
              source_resource_group_name=None, source_disk_name=None,
              target_storage_account_name=None, target_storage_container_name=None, target_vhd_name=None,
              target_resource_group_name=None, target_disk_name=None):
    
    if source_type not in ['vhd', 'disk'] and target_type not in ['vhd', 'disk']:
      raise Exception('An invalid combination of source (vhd/disk) and target (vhd/disk) was provided')

    if source_type == 'vhd':
      #TODO: Get source region for VHDs
      source_region = None

      if target_type == 'vhd':
        copy_vhd_to_vhd(source_vhd_uri, target_storage_account_name, target_storage_container_name, target_vhd_name)
      elif target_type == 'disk':
        copy_vhd_to_disk(source_vhd_uri, target_resource_group_name, target_disk_name)
    elif source_type == 'disk':
      #TODO: Get source region for Managed Disks
      source_region = None

      if target_type == 'vhd':
        copy_disk_to_vhd(source_resource_group_name, source_disk_name, target_storage_account_name, target_storage_container_name, target_vhd_name)
      elif target_type == 'vhd':
        copy_disk_to_disk(source_resource_group_name, source_disk_name, target_disk_name)
      