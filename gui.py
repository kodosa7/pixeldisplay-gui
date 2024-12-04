import os
import sys
import tkinter
from tkinter import Label, filedialog, messagebox
import asyncio
import re
import logging

logging.basicConfig(level=logging.INFO)

# import send   # Original script by R0ger and Aki - Refactored into idm.pixeldisplay library
from idm.pixeldisplay import BLEScanner, BLEImageUploader

ble_scanner = BLEScanner()


# setup
tk = tkinter.Tk(className=" DotMatrix Display GUI Uploader")
tk.geometry("500x400")
tk.resizable(False, False)

# labels
label = Label(tk, text="MAC address of your device:")
mac_label = Label(tk, text="<None selected>", font=("Calibri", 30))
author = Label(tk, text="Engine by R0ger, GUI by Aki © 2024\nScanner + GUI modifications by Noctis")
file_label = Label(tk, text="Selected File: <not selected>")
upload_label = Label(tk, text="Status: idle")
lbl_select_device = Label(tk, text="Select Device")
# listbox
lst_devices = tkinter.Listbox(tk, width=100)

# checkbox
fix_colors = tkinter.IntVar(value=1)
chk_fixcolors = tkinter.Checkbutton(tk, text="Fix colors", variable=fix_colors)


# get path (for python 3.8+) to be able to compile as one file using PyInstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# define callbacks
def selectFileCallback():
    """ Select File button handler """
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("BMP Images", "*.bmp"), ("GIF Animations", "*.gif"), ("All files", "*.*")]
    )
    if file_path:
        file_label.config(text=f"Selected File: {file_path}")


def uploadCallback():
    """ Upload button handler """
    file_path = file_label.cget("text")
    mac_addr = mac_label.cget("text")

    # Validate device selection
    if mac_addr == "<None selected>":
        tkinter.messagebox.showwarning("Warning", "Please select your device")
        return

    # Validate file selection
    if file_path == "Selected File: <not selected>":
        tkinter.messagebox.showwarning("Warning", "No file selected")
        return

    # Proceed with upload
    try:
        upload_label.config(text="Status: Uploading, please wait!")
        tk.update()  # Update GUI before the upload starts

        # Extract the file path
        filename = file_path.split(": ", 1)[1]

        # Execute the external script
        # subprocess.run(["python", "send.py", "mac", mac_addr, filename], check=True)
        _uploader = BLEImageUploader(mac_addr, bool(fix_colors.get()))
        asyncio.run(_uploader.send_image(filename))

        upload_label.config(text="Status: Upload complete")
        logging.info("All done! :-)")
    except Exception as e:
        upload_label.config(text=f"Status: Upload failed {e}")
        logging.error(f"ERROR: {e}")
        tkinter.messagebox.showerror("Error", "Upload failed. Please try again.")


def scan_callback():
    lst_devices.delete(0, tkinter.END)  # Clear listbox
    btn_scan.config(state=tkinter.DISABLED, text="Scanning...")  # Disable button and change text
    tk.update()
    asyncio.run(scan_and_update())


async def scan_and_update():
    """
    Scan for BLE devices and update list
    """
    devices = await ble_scanner.discover_devices()
    for device in devices:
        lst_devices.insert(tkinter.END, f"{device.name}({device.address})")
    btn_scan.config(state=tkinter.NORMAL, text="Scan for devices")  # Disable button and change text


def select_device_callback(event):
    listbox = event.widget
    sel_index = listbox.curselection()
    if sel_index:
        # RegEx to extract MAC address - This allows us to show the name in the listbox.
        # Yay, userfriendlyness! :)
        selected_device = lst_devices.get(sel_index)
        match = re.search(r"\(([^)]+)\)", selected_device)
        mac_label.config(text=match.group(1))
    else:
        mac_label.config(text="-")


# show text
label.place(x=230, y=5)
mac_label.place(x=152, y=25)
author.place(x=160, y=335)
file_label.place(x=128, y=180)
upload_label.place(x=128, y=200)
lbl_select_device.place(x=5, y=5)

# configure buttons
btn_sel_file = tkinter.Button(tk, text="Select File", command=selectFileCallback)
btn_upload = tkinter.Button(tk, text="Upload to device", command=uploadCallback)
btn_scan = tkinter.Button(tk, text="Scan for devices", command=scan_callback)

# show buttons
btn_sel_file.place(x=200, y=90, height=50, width=120)
btn_upload.place(x=320, y=90, height=50, width=120)
btn_scan.place(x=5, y=330, height=50, width=120)
lst_devices.place(x=5, y=30, height=300, width=120)
chk_fixcolors.place(x=125, y=160, height=20)

# bind callback to listbox
lst_devices.bind("<<ListboxSelect>>", select_device_callback)

if __name__ == "__main__":
    tk.mainloop()
