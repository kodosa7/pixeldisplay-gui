import tkinter, sys, os
from tkinter import Label, filedialog
import send


# setup
tk = tkinter.Tk(className=" DotMatrix Display GUI Uploader")
tk.geometry("400x200")
label = Label(tk, text="MAC address of your device:")
maclabel = Label(tk, text=send.address.upper(), font=("Calibri", 30))
author = Label(tk, text="© Aki 2024")
filelabel = Label(tk, text="Selected File: <not selected>")

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
    global file_path
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("BMP Images", "*.bmp"), ("GIF Animations", "*.gif"), ("All files", "*.*")]
    )
    if file_path:
        filelabel.config(text=f"Selected File: {file_path}")

def uploadCallback():
    if file_path:
        filename = file_path
        print("file_path: ", file_path)
        os.system(f'python send.py {filename}')
        print("all done! :-)")
    
def enterMacAddressCallback():
    pass

# show text
label.place(x=5, y=5)
maclabel.place(x=41, y=25)
author.place(x=335, y=180)
filelabel.place(x=5, y=160)


# configure buttons
button1 = tkinter.Button(tk, text="Select File", command=selectFileCallback)
button2 = tkinter.Button(tk, text="Upload to device", command=uploadCallback)
button3 = tkinter.Button(tk, text="Enter MAC address", command=enterMacAddressCallback)

# show buttons
button1.place(x=30, y=90, height=50, width=100)
button2.place(x=150, y=90, height=50, width=100)
button3.place(x=270, y=90, height=50, width=100)



if __name__ == "__main__":
    tk.mainloop()