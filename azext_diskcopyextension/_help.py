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
          short-summary: Underlying storage SKU
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