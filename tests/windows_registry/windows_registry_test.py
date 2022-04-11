from pytest import fixture
import os

from .shared_fixtures import *

#
# NOTE: helper `wp()` imported from .shared_fixtures
#

class TestExport():
    sample_reg_filename = 'export_sample_01.reg'
    sample_reg_key      = r'ControlSet001\Control\Bluetooth\Audio\Hfp'

    @fixture
    def export_sample(self, windows_registry_samples_dir):
        with open(os.path.join(windows_registry_samples_dir, self.sample_reg_filename), 'r') as f:
            sample = f.read()
        
        return sample


    def test_export(self, export_sample, windows_registry):
        exported_data = windows_registry.export(self.sample_reg_key)
        assert exported_data == export_sample


    def test_configparser_compatible(self, windows_registry):
        reg_data = windows_registry.export_as_config(self.sample_reg_key)

        key = wp(r'ControlSet001\Control\Bluetooth\Audio\Hfp\HandsFree')
        sample_value = reg_data.get(key, '"ProfileVersion"')
        expected = 'dword:00000107';

        assert sample_value == expected


class TestImport():
    sample_reg_key = r'ControlSet001\Control\Bluetooth\Audio\Hfp'

    def test_import_unsafe(self, windows_registry):
        for_import = {
            wp(r'ControlSet001\Control\Bluetooth\Audio\Hfp\HandsFree'): {
                '"Custom"': 'dword:00000120'
            },

            wp(r'ControlSet001\Control\Bluetooth\Audio\Hfp\HandsFree\Sub'): {
                '"CustomSub"': 'dword:00000121'
            }
        }

        windows_registry.import_dict(for_import, safe=False)

        reg_data = windows_registry.export_as_config(self.sample_reg_key)

        key = wp(r'ControlSet001\Control\Bluetooth\Audio\Hfp\HandsFree')
        assert reg_data.get(key, '"ProfileVersion"') == 'dword:00000107', \
            'existing values remain the same'

        assert reg_data.get(key, '"Custom"') == 'dword:00000120', \
            'new key added'

        key = wp(r'ControlSet001\Control\Bluetooth\Audio\Hfp\HandsFree\Sub')
        assert reg_data.get(key, '"CustomSub"') == 'dword:00000121', \
            'new section added'


    def test_import_safe(self, windows_registry, sample_reg_file_path, registry_file_path):
        new_value = 'dword:00000207'
        for_import = {
            wp(r'ControlSet001\Control\Bluetooth\Audio\Hfp\HandsFree'): {
                '"ProfileVersion"': new_value
            }
        }

        windows_registry.import_dict(for_import, safe=True)
        reg_data = windows_registry.export_as_config(self.sample_reg_key)

        key = wp(r'ControlSet001\Control\Bluetooth\Audio\Hfp\HandsFree')

        assert reg_data.get(key, '"ProfileVersion"') == new_value, \
            'existing values updated'

        assert os.path.getsize(sample_reg_file_path) == os.path.getsize(registry_file_path), \
            'Hive file size remain unchanged'
