from azure.cli.core import AzCommandsLoader

from ._help import helps

from ._validators import validate_copy_vhd_to_disk

class DiskCopyCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        diskcopy_custom = CliCommandType(operations_tmpl='azext_diskcopyextension.custom#{}')
        super(DiskCopyCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                     custom_command_type=diskcopy_custom)

    def load_command_table(self, args):
        with self.command_group('storage blob') as g:
            g.custom_command('copy-to-vhd', 'copy_vhd_to_vhd')
            g.custom_command('copy-to-disk', 'copy_vhd_to_disk', validator=validate_copy_vhd_to_disk)
        with self.command_group('disk') as g:
            g.custom_command('copy-to-vhd', 'copy_disk_to_vhd')
            g.custom_command('copy-to-disk', 'copy_disk_to_disk')
        return self.command_table

    def load_arguments(self, command):
        with self.argument_context('storage blob copy-to-vhd') as c:
            c.argument('source_vhd_uri', options_list=['--source-uri', '-u'])
        with self.argument_context('storage blob copy-to-vhd', arg_group='Destination VHD') as c:
            c.argument('target_storage_account_name', options_list=['--account-name'])
            c.argument('target_storage_container_name', options_list=['--destination-container', '-c'])
            c.argument('target_vhd_name', options_list=['--destination-blob', '-b'])
        
        with self.argument_context('storage blob copy-to-disk') as c:
            c.argument('source_vhd_uri', options_list=['--source-uri', '-u'])
        with self.argument_context('storage blob copy-to-disk', arg_group='Destination Disk') as c:
            c.argument('target_resource_group_name', options_list=['--resource-group', '-g'])
            c.argument('target_disk_name', options_list=['--disk-name', '-n'])

        with self.argument_context('disk copy-to-vhd') as c:
            c.argument('source_resource_group_name', options_list=['--source-resource-group'])
            c.argument('source_disk_name', options_list=['--source-disk-name'])
        with self.argument_context('disk copy-to-vhd', arg_group='Destination VHD') as c:
            c.argument('target_storage_account_name', options_list=['--account-name'])
            c.argument('target_storage_container_name', options_list=['--destination-container', '-c'])
            c.argument('target_vhd_name', options_list=['--destination-blob', '-b'])

        with self.argument_context('disk copy-to-disk') as c:
            c.argument('source_resource_group_name', options_list=['--source-resource-group'])
            c.argument('source_disk_name', options_list=['--source-disk-name'])
        with self.argument_context('disk copy-to-disk', arg_group='Destination Disk') as c:
            c.argument('target_resource_group_name', options_list=['--resource-group', '-g'])
            c.argument('target_disk_name', options_list=['--disk-name', '-n'])


COMMAND_LOADER_CLS = DiskCopyCommandsLoader
