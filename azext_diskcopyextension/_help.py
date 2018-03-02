from knack.help_files import helps

helps['storage blob copy-to-disk'] = """
    type: command
    short-summary: Copy a Virtual Machine disk
    long-summary: >
        Takes a snapshot of a VHD blob and creates a new disk from it. 
        Supports cross-region copies.
    parameters:
        - name: --source-uri -u
          type: string
          short-summary: Unmanaged disk blob URL
        - name: --disk-name -n
          type: string
          short-summary: Name of the new Managed Disk.  Uses the name of the source blob if not provided.
        - name: --resource-group -g
          type: string
          short-summary: Name of resource group
        - name: --sku
          type: string
          short-summary: short-summary: (Optional) Underlying storage SKU for the new disk. Uses the SKU of the source storage account if not provided.
        - name: --temp-storage-account
          type: string
          short-summary: (Optional) Temporary storage account to be used for cross-region copies. Created dynamically if not provided.
    examples:
        - name: Copy an unmanaged disk to a Managed Disk
          text: >
            az storage blob copy-to-disk -u https://mystorage.blob.core.windows.net/vhds/my-disk.vhd -g my-local-rg
        - name: Copy an unmanaged disk to a Managed Disk across regions with a specified temporary storage account
          text: >
            az storage blob copy-to-disk -u https://mystorage.blob.core.windows.net/vhds/my-disk.vhd -g my-remote-rg --temp-storage diskcopytemp123
"""

helps['disk copy-to-disk'] = """
    type: command
    short-summary: Copy a Virtual Machine disk
    long-summary: >
        Takes a snapshot of a Managed Disk and creates a new disk from it. 
        Supports cross-region copies.
    parameters:
        - name: --source-disk-name -n
          type: string
          short-summary: Name of the source disk
        - name: --source-resource-group -g
          type: string
          short-summary: Name of resource group for the source disk
        - name: --target-resource-group
          type: string
          short-summary: Name of resource group for the new disk
        - name: --target-disk-name
          type: string
          short-summary: Name for the new disk.  Uses the name of the source disk if not provided.
        - name: --sku
          type: string
          short-summary: (Optional) Underlying storage SKU for the new disk. Uses the SKU of the source disk if not provided.
        - name: --temp-storage-account
          type: string
          short-summary: (Optional) Temporary storage account to be used for cross-region copies. Created dynamically if not provided.
    examples:
        - name: Copy a Managed Disk to a Managed Disk
          text: >
            az disk copy-to-disk -n mydisk -g my-source-rg --target-resource-group my-local-rg
        - name: Copy a Nanaged Disk to a Managed Disk across regions with a specified temporary storage account
          text: >
            az disk copy-to-disk -n mydisk -g my-source-rg --target-resource-group my-remote-rg --temp-storage diskcopytemp123
"""