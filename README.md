# Azure CLI Disk Copy Extension

## Commands

```bash
# Copy VHD to VHD (same or cross-region)
# * Snapshot https://foo.blob.core.windows.net/vhds/myDisk.vhd
# * Start blob copy from snapshot to https://bar.blob.core.windows.net/vhdcopies/someDisk.vhd
# * Delete snapshot
az disk copy \
  --source-vhd-uri https://foo.blob.core.windows.net/vhds/myDisk.vhd \
  --target-storage-account bar \
  --target-storage-container vhdcopies \
  --target-disk-name someDisk

# Copy and convert VHD to Managed Disk (same region)
# * Snapshot https://foo.blob.core.windows.net/vhds/myDisk.vhd (az snapshot create)
# * Create /subscriptions/XXXX/resourceGroups/someRG/providers/Microsoft.Compute/disks/someDisk from snapshot
# * Delete snapshot
az disk copy \
  --source-vhd-uri https://foo.blob.core.windows.net/vhds/myDisk.vhd \
  --target-resource-group someRG \
  --target-disk-name someDisk \
  --target-region eastus              # optional - use target-resource-group region if not specified

# Copy and convert VHD to Managed Disk (cross-region)
# * Snapshot https://foo.blob.core.windows.net/vhds/myDisk.vhd (az storage blob snapshot)
# * Create storage account tempstorage123 if needed
# * Create container tempvhds if needed
# * Start blob copy from snapshot to https://tempstorage123.blob.core.windows.net/tempvhds/{GUID}.vhd
# * Wait for blob copy to finish
# * Create /subscriptions/XXXX/resourceGroups/someRG/providers/Microsoft.Compute/disks/someDisk from https://tempstorage123.blob.core.windows.net/tempvhds/{GUID}.vhd
# * Delete snapshot
# * Delete https://tempstorage123.blob.core.windows.net/tempvhds/{GUID}.vhd
az disk copy \
  --source-vhd-uri https://foo.blob.core.windows.net/vhds/myDisk.vhd \
  --temp-storage-account tempstorage123 \   # optional - auto-create if not specified
  --temp-storage-container tempvhds \       # optional - use "temp-disk-copy" if not specified
  --target-resource-group someRG \
  --target-disk-name someDisk \
  --target-region westus                    # optional - use target-resource-group region if not specified

# Copy Managed Disk (same region)
# * Snapshot /subscriptions/XXXX/resourceGroups/myRG/providers/Microsoft.Compute/disks/myDisk (az snapshot create)
# * Create /subscriptions/XXXX/resourceGroups/someRG/providers/Microsoft.Compute/disks/someDisk from snapshot
# * Delete snapshot
az disk copy \
  --source-resource-group myRG \
  --source-disk-name myDisk \
  --target-resource-group someRG \
  --target-disk-name someDisk \
  --target-region eastus                    # optional - use target-resource-group region if not specified

# Copy Managed Disk (cross-region)
# * Snapshot /subscriptions/XXXX/resourceGroups/myRG/providers/Microsoft.Compute/disks/myDisk (az snapshot create)
# * Create storage account tempstorage123 if needed
# * Create container tempvhds if needed
# * Get SAS url for snapshot
# * Start blob copy from snapshot (using SAS url) to https://tempstorage123.blob.core.windows.net/tempvhds/{GUID}.vhd
# * Wait for blob copy to finish
# * Create /subscriptions/XXXX/resourceGroups/someRG/providers/Microsoft.Compute/disks/someDisk from https://tempstorage123.blob.core.windows.net/tempvhds/{GUID}.vhd
# * Delete snapshot
# * Delete https://tempstorage123.blob.core.windows.net/tempvhds/{GUID}.vhd
az disk copy \
  --source-resource-group myRG \
  --source-disk-name myDisk \
  --temp-storage-account tempstorage123 \   # optional - auto-create if not specified
  --temp-storage-container tempvhds \       # optional - use "temp-disk-copy" if not specified
  --target-resource-group someRG \
  --target-disk-name someDisk \
  --target-region westus                    # optional - use target-resource-group region if not specified

# Copy Managed Disk to VHD (same or cross-region)
# * Snapshot /subscriptions/XXXX/resourceGroups/myRG/providers/Microsoft.Compute/disks/myDisk (az snapshot create)
# * Get SAS url for snapshot
# * Start blob copy from snapshot (using SAS url) to https://bar.blob.core.windows.net/vhdcopies/someDisk.vhd
# * Delete snapshot
az disk copy \
  --source-resource-group myRG \
  --source-disk-name myDisk \
  --target-storage-account bar \
  --target-storage-container vhdcopies \
  --target-disk-name someDisk
```

## Development

```bash
export AZURE_EXTENSION_DIR=~/.azure/devcliextensions

pip install --upgrade --target ~/.azure/devcliextensions/disk-copy-extension ~/code/azure-cli-disk-copy-extension
```