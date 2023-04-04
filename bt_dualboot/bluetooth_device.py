from bt_dualboot.bt_windows.convert import mac_to_reg_key, hex_string_to_reg_value, hex_string_to_reg_hex_b
import struct

class BluetoothDevice:
    """Representation of bluetooth device

    Properties:
        klass (str)
        mac (str)
        name (str)
        pairing_key (str)
        ltk (str)
        rand (int)
        edir (int)
        adapter_mac (str)
        source (str): kind of 'Windows', 'Linux'

    """

    def __init__(
        self,
        mac=None,
        name=None,
        pairing_key=None,
        adapter_mac=None,
        device_class=None,
        source=None,
        ltk=None,
        rand=None,
        ediv=None,
    ):
        # fmt: off
        self.source         = source
        self.klass          = device_class
        self.mac            = mac
        self.name           = name
        self.pairing_key    = pairing_key
        self.adapter_mac    = adapter_mac
        # bluetooth 5.1
        self.ltk            = ltk
        self.rand           = rand
        self.ediv           = ediv
        # fmt: on

    def __repr__(self):
        source = "?"
        if self.source is not None:
            source = self.source[0]
        return f"{self.__class__} {source} [{self.mac}] {self.name}"
    
    def _get_reg_adapter_section_key(self):
        if self.pairing_key:
            return (
                r"ControlSet001\Services\BTHPORT\Parameters\Keys" + "\\" + mac_to_reg_key(self.adapter_mac)
            )
        if self.ltk:
            return (
                r"ControlSet001\Services\BTHPORT\Parameters\Keys" + "\\" + mac_to_reg_key(self.adapter_mac) + "\\" + mac_to_reg_key(self.mac)
            )
        raise Exception(f"Missing pairing key or long term key for {self.adapter_mac}/{self.mac}")

    def rand_to_erand(self):
        # hex(b) type -> 64 bit -> 8 byte in little endian
        hex_string = struct.pack("<Q", self.rand).hex().upper()
        return hex_string_to_reg_hex_b(hex_string)

    def ediv_to_dword(self):
        # dword alias hex(4) type -> 32 bit -> 4 byte in little endian
        # Microsoft says it should be little endian: https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-value-types
        # they are liars
        dword_val = struct.pack(">I", self.ediv).hex()
        return f"dword:{dword_val}"

    def for_win_import(self):
        if self.pairing_key:
            device_key = f'"{mac_to_reg_key(self.mac)}"'
            pairing_key = hex_string_to_reg_value(self.pairing_key)
            return self._get_reg_adapter_section_key(), {
                    device_key: pairing_key
                }
        elif self.ltk:
            return self._get_reg_adapter_section_key(), {
                    '"LTK"': hex_string_to_reg_value(self.ltk),
                    '"ERand"': self.rand_to_erand(),
                    '"EDIV"': self.ediv_to_dword()
                }
        raise KeyError(f"Device {self.mac} has neither pairing key, nor long term key")

    def synced(self, other):
        if self.pairing_key:
            return self.pairing_key == other.pairing_key
        if self.ltk and self.rand and self.ediv:
            return (self.ltk == other.ltk and
                    self.rand == other.rand and
                    self.ediv == other.ediv)

    @classmethod
    def source_linux(cls):
        return "Linux"

    @classmethod
    def source_windows(cls):
        return "Windows"

    def is_source_linux(self):
        return self.source == "Linux"

    def is_source_windows(self):
        return self.source == "Windows"
