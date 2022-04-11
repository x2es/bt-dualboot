class BluetoothDevice:
    """Representation of bluetooth device

    Properties:
        klass (str)
        mac (str)
        name (str)
        pairing_key (str)
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
    ):
        # fmt: off
        self.source         = source
        self.klass          = device_class
        self.mac            = mac
        self.name           = name
        self.pairing_key    = pairing_key
        self.adapter_mac    = adapter_mac
        # fmt: on

    def __repr__(self):
        source = "?"
        if self.source is not None:
            source = self.source[0]
        return f"{self.__class__} {source} [{self.mac}] {self.name}"

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
