from knack.help_files import helps

helps['disk copy'] = """
    type: command
    short-summary: Copy a Virtual Machine disk
    long-summary: >
        Takes a snapshot of a VM disk and creates a new disk from it. Supports
        unmanaged disks (VHD blobs in a storage account) and Managed Disks
        as both a source and a target. Also supports copying blobs across
        regions.
    examples:
        - name: Copy an unmanaged disk to a Managed Disk
          text: >
            az disk copy \\
              --source-vhd-uri https://foo.blob.core.windows.net/vhds/myDisk.vhd \\
              --target-resource-group someRG \\
              --target-disk-name someDisk
"""