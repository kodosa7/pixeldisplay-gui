from bleak import BleakScanner
from bleak import BleakClient
import zlib
import os
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class BLEScanner:
    def __init__(self):
        self.scanner = BleakScanner()

    async def discover_devices(self):
        """
        Discover nearby BLE devices asynchronously.

        Returns:
            List of discovered BLE devices.
        """
        logger.info("Discovering nearby BLE devices...")
        devices = await self.scanner.discover()
        logger.info(f"Discovered {len(devices)} BLE devices:")
        for device in devices:
            logger.info(f"--> {device}")
        return devices


class BLEImageUploader:
    def __init__(self, address, fix_colors=True):
        """
        Initialize the BLEImageUploader.

        :param address: The Bluetooth MAC address of the target device.
        :param fix_colors: Whether to apply color correction to the image.
        """
        self.address = address
        self.fix_colors = fix_colors

    def _apply_color_correction(self, pixel, gamma, rf, gf, bf):
        """
        Apply gamma and color scaling correction to a pixel.

        :param pixel: A tuple representing the pixel (R, G, B).
        :param gamma: The gamma value for correction.
        :param rf, gf, bf: Red, green, and blue scaling factors.
        :return: A corrected (R, G, B) tuple.
        """
        r = int(pow(pixel[0] / 255, gamma) * rf)
        g = int(pow(pixel[1] / 255, gamma) * gf)
        b = int(pow(pixel[2] / 255, gamma) * bf)
        return r, g, b

    async def _send_bmp(self, client, filename):
        im = Image.open(filename, "r")
        w, h = im.size
        pix = im.load()

        data = []
        rf, gf, bf = 255, 255, 150
        gamma = 1 / 0.5

        for y in range(h):
            for x in range(w):
                p = pix[x, y]
                if self.fix_colors:
                    r, g, b = self._apply_color_correction(p, gamma, rf, gf, bf)
                    data.extend([r, g, b])
                else:
                    data.extend(p)

        data_bytes = bytes(data)
        crc = zlib.crc32(data_bytes).to_bytes(4, "little")
        header1 = bytes.fromhex("020000")
        header2 = bytes.fromhex("05000d")
        data_len = len(data_bytes)
        cmd_size = data_len + 16

        logger.info(f"Sending {cmd_size} bytes")
        await client.write_gatt_char(
            "0000fa02-0000-1000-8000-00805F9B34FB",
            cmd_size.to_bytes(2, "little") + header1 +
            data_len.to_bytes(4, "little") + crc + header2 + data_bytes
        )
        logger.info(f"Completed uploading {filename} to device {client}.")

    async def _send_gif(self, client, filename):
        stats = os.stat(filename)
        with open(filename, "rb") as f:
            data = f.read()

        data_len = stats.st_size
        remaining = data_len
        offset = 0
        crc = zlib.crc32(data).to_bytes(4, "little")
        header1 = bytes.fromhex("010000")
        header2 = bytes.fromhex("05000d")

        while remaining > 0:
            cmd_data = min(remaining, 4096)
            cmd_size = cmd_data + 16

            logger.info(f"Sending {cmd_size} bytes at offset {offset}")
            await client.write_gatt_char(
                "0000fa02-0000-1000-8000-00805F9B34FB",
                cmd_size.to_bytes(2, "little") + header1 +
                data_len.to_bytes(4, "little") + crc + header2 +
                data[offset:offset + cmd_data]
            )

            if offset == 0 and cmd_data == 4096:
                header1 = bytes.fromhex("010002")

            remaining -= cmd_data
            offset += cmd_data

        logger.info(f"Completed uploading {filename} to device {client}.")

    async def send_image(self, filename):
        """
        Send an image file (BMP or GIF) to the BLE device.

        :param filename: The path to the image file.
        """
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"File {filename} not found")

            name, ext = os.path.splitext(filename)
            ext = ext.lower()

            async with BleakClient(self.address) as client:
                if ext == ".bmp":
                    await self._send_bmp(client, filename)
                elif ext == ".gif":
                    await self._send_gif(client, filename)
                else:
                    raise ValueError("Unsupported file format. Only BMP and GIF are supported.")
        except FileNotFoundError as e:
            logger.error(f"File error: {e}")
            raise
        except Exception as e:
            logger.exception("An unexpected error occurred while sending the image")
            raise