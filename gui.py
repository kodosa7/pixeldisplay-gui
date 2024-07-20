import tkinter, sys, os
from tkinter import Label, filedialog
import send


# setup
global uploadlabel

tk = tkinter.Tk(className=" DotMatrix Display GUI Uploader")
tk.geometry("400x200")
label = Label(tk, text="MAC address of your device:")
maclabel = Label(tk, text=send.address.upper(), font=("Calibri", 30))
author = Label(tk, text="© Aki 2024")
filelabel = Label(tk, text="Selected File: <not selected>")
uploadlabel = Label(tk, text="empty", font=("Calibri", 20))

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
        uploadlabel.config(text="Uploading, please wait!")
        tk.update()  # Ensure the GUI updates the label text before proceeding
        filename = file_path
        print("now it should display the label")
        os.system(f'python send.py {send.address} {filename}')
        uploadlabel.config(text="Upload complete!")
        print("all done! :-)")
    
def enterMacAddressCallback():
    pass

# show text
label.place(x=5, y=5)
maclabel.place(x=41, y=25)
author.place(x=335, y=180)
filelabel.place(x=5, y=160)
uploadlabel.place(x=5, y=5)

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