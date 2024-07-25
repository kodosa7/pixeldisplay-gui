import asyncio
from bleak import BleakClient
import zlib
import os
import sys
from PIL import Image


# R0ger
# address = "2a:d8:16:d0:23:ca"
# own 
# address = "b4:fb:a8:bc:c5:70"
# steve
address = "34:49:39:B1:59:17"

filename = ""

def Usage():
	print("usage: send [mac aa:bb:cc:dd:ee:ff] [nofix] filename")
	print("nofix = do not fix colours")

async def main(address, filename):

	argl = len(sys.argv);
	
	fix = 1
	
	if argl > 1:
		for i in range(1, argl):
			cmd=sys.argv[i]
			
			if 	cmd.lower() == "mac":
				i = i + 1
				if i < argl:
					address = sys.argv[i]
				else:
					return Usage()
					
			elif cmd.lower() == "nofix":
				fix = 0
			
			else:
				filename = sys.argv[i]
					
	if address == "" or filename == "":
		return Usage()


	async with BleakClient(address) as client:

		name, ext = os.path.splitext(filename)

		if ext.lower() == ".bmp":

			im = Image.open(filename, "r")
			w, h = im.size
			pix = im.load()

			bl = []

			rf = 255
			gf = 255
			bf = 150

			gamma = 1 / 0.5

			for y in range(h):
				for x in range(w):
					p = pix[x, y]

					if fix > 0:
						r = int(pow(p[0] / 255, gamma) * rf)
						g = int(pow(p[1] / 255, gamma) * gf)
						b = int(pow(p[2] / 255, gamma) * bf)
						bl.extend([r, g, b])
					else:
						bl.extend(p)

			data = bytes(bl)

			crc = zlib.crc32(data).to_bytes(4, "little")
			header1 = bytes.fromhex("020000")
			header2 = bytes.fromhex("05000d")
			
			data_len = w * h * 3
			cmd_size = data_len + 16

			print ("Sending " + str(cmd_size) + " bytes")
			
			await client.write_gatt_char("0000fa02-0000-1000-8000-00805F9B34FB", cmd_size.to_bytes(2, "little") + header1 + data_len.to_bytes(4, "little") + crc + header2 + data)

			print ("Done.")				


		if ext.lower() == ".gif":

			stats = os.stat(filename)

			f = open(filename, "rb")
			data = f.read()
			f.close()
			
			data_len = stats.st_size
			remaining = data_len
			offset = 0
			
			crc = zlib.crc32(data).to_bytes(4, "little")
			header1 = bytes.fromhex("010000")
			header2 = bytes.fromhex("05000d")

			while remaining > 0:
			
				if remaining > 4096:
					cmd_data = 4096
				else:
					cmd_data = remaining

				cmd_size = cmd_data + 16
				
				print ("Sending " + str(cmd_size) + " bytes at offset " + str(offset))
			
				await client.write_gatt_char("0000fa02-0000-1000-8000-00805F9B34FB", cmd_size.to_bytes(2,"little") + header1 + data_len.to_bytes(4, "little") + crc + header2 + data[offset:offset + cmd_data])
				
				if offset == 0 and cmd_data == 4096:
					header1 = bytes.fromhex("010002")

				remaining = remaining - cmd_data
				offset = offset + cmd_data
				
			print ("Done.")
			
			
if __name__ == "__main__":
	asyncio.run(main(address,filename))
