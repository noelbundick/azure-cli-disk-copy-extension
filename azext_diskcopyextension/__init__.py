from azure.cli.core import AzCommandsLoader

from ._help import helps

class DiskCopyCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        diskcopy_custom = CliCommandType(operations_tmpl='azext_diskcopyextension.custom#{}')
        super(DiskCopyCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                     custom_command_type=diskcopy_custom)

    def load_command_table(self, args):
        with self.command_group('disk') as g:
            from ._validators import validate_disk_copy
            g.custom_command('copy', 'disk_copy', validator=validate_disk_copy)
        return self.command_table

    def load_arguments(self, command):
        with self.argument_context('disk copy') as c:
            c.ignore('source_type')
            c.ignore('target_type')

COMMAND_LOADER_CLS = DiskCopyCommandsLoader
