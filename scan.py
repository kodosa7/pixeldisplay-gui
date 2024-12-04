from bleak import BleakScanner


class BLEScanner:
    def __init__(self):
        self.scanner = BleakScanner()

    async def discover_devices(self):
        """
        Discover nearby BLE devices asynchronously.

        Returns:
            List of discovered BLE devices.
        """
        devices = await self.scanner.discover()
        return devices
