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
          long-summary: A URL that specifies the location of an unmanaged disk blob.
    examples:
        - name: Copy an unmanaged disk to a Managed Disk
          text: >
            az storage blob copy-to-disk ...
        - name: Copy an unmanaged disk to a Managed Disk across regions with a specified temporary storage account
          text: >
            az storage blob copy-to-disk ...
"""