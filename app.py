import logging
import os
import tkinter as tk
from tkinter import filedialog as fd, messagebox
from tkinter import *

from timstof_utils import generate_ms1, generate_ms2
from logger_writer import LoggerWriter

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename='out.log',
    filemode='a'
)

# redirect stdout and stderr to log file
log = logging.getLogger('app')


# sys.stdout = LoggerWriter(log.debug)
# sys.stderr = LoggerWriter(log.warning)

class RawFileTinker(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.raw_folder = None
        self.generating_file = False

        self._frame_width = 80

        self.master.title("RawFileExtractor")
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W + E + N + S)

        self.button = Button(self, text="Select D folder", command=self.load_file, width=self._frame_width)
        self.button.pack(expand=True)

        self.dfolder_label = Label(self, text="no file selected", width=self._frame_width, height=2)
        self.dfolder_label.pack(expand=True)

        self.ms1_frame = Frame(self)
        self.ms1_frame.pack(expand=True)

        self.button_ms1 = Button(self.ms1_frame, text="Generate Ms1 File", command=self.generate_ms1,
                                 width=int(self._frame_width / 2), state=DISABLED)
        self.button_ms1.pack(side=LEFT, expand=True)

        self.percent_done_ms1_text = Label(self.ms1_frame, text="0%", width=int(self._frame_width / 2), height=2)
        self.percent_done_ms1_text.pack(side=RIGHT, expand=True)

        self.ms2_frame = Frame(self)
        self.ms2_frame.pack(expand=True)

        self.button_ms2 = Button(self.ms2_frame, text="Generate Ms2 File", command=self.generate_ms2,
                                 width=int(self._frame_width / 2), state=DISABLED)
        self.button_ms2.pack(side=LEFT, expand=True)

        self.percent_done_ms2_text = Label(self.ms2_frame, text="0%", width=int(self._frame_width / 2), height=2)
        self.percent_done_ms2_text.pack(side=RIGHT, expand=True)

        directions = "Directions\n" \
                     " 1) Select D folder (don't double click).\n" \
                     " 2) Press either ms1 or ms2 button.\n" \
                     " 3) Wait :) \n" \
                     " 4) ms1/ms2 file will be generated in the D folder with the same name as the folder.\n" \
                     " \n" \
                     "Note: Ms1 files are very large for timsTof experiments ~50 GB\n" \
                     " - Made by Patrick Garrett 8/6/2021"
        messagebox.showinfo("Version 1.0", directions)

    def generate_ms1(self):

        self.button_ms1['state'] = DISABLED
        self.button_ms2['state'] = DISABLED
        self.button['state'] = DISABLED

        file_path = os.path.basename(self.raw_folder).split('.')[0] + '.ms1'
        file_path = os.path.join(self.raw_folder, file_path)

        contains_file = os.path.exists(file_path)
        if contains_file:
            MsgBox = messagebox.askquestion('File Exists',
                                            'Ms1 File already exists... Click yes to overwrite. No to abort. ',
                                            icon='warning')
            if MsgBox == 'yes':
                pass
            else:
                self.button_ms1['state'] = NORMAL
                self.button_ms2['state'] = NORMAL
                self.button['state'] = NORMAL
                return

        gen = generate_ms1(self.raw_folder)

        for percent_done in gen:
            print(percent_done)
            self.percent_done_ms1_text['text'] = str(round(percent_done, 2)) + "%"
            self.update()

        file_path = os.path.basename(self.raw_folder).split('.')[0] + '.ms1'
        file_path = os.path.join(self.raw_folder, file_path)
        messagebox.showinfo("Done!", "File Path:\n" + file_path)

        self.button_ms1['state'] = NORMAL
        self.button_ms2['state'] = NORMAL
        self.button['state'] = NORMAL

    def generate_ms2(self):

        self.button_ms2['state'] = DISABLED
        self.button_ms1['state'] = DISABLED
        self.button['state'] = DISABLED

        file_path = os.path.basename(self.raw_folder).split('.')[0] + '.ms2'
        file_path = os.path.join(self.raw_folder, file_path)

        contains_file = os.path.exists(file_path)
        if contains_file:
            MsgBox = messagebox.askquestion('File Exists', 'Ms2 File already exists... Click yes to overwrite. No to abort. ',
                                               icon='warning')
            if MsgBox == 'yes':
                pass
            else:
                self.button_ms1['state'] = NORMAL
                self.button_ms2['state'] = NORMAL
                self.button['state'] = NORMAL
                return

        gen = generate_ms2(self.raw_folder)

        for percent_done in gen:
            print(percent_done)
            self.percent_done_ms2_text['text'] = str(round(percent_done, 2)) + "%"
            self.update()

        messagebox.showinfo("Done!", "File Path:\n" + file_path)

        self.button_ms1['state'] = NORMAL
        self.button_ms2['state'] = NORMAL
        self.button['state'] = NORMAL

    def load_file(self):
        self.raw_folder = fd.askdirectory(
            title='Open a file',
            initialdir='/')

        if not os.path.isdir(self.raw_folder) or self.raw_folder == "":
            messagebox.showinfo("Hmmmm", "Selected Path is not a Directory")
            return

        if ".d" not in self.raw_folder:
            messagebox.showinfo("Hmmmm", "Selected Path is not a timsTof .d folder")
            return

        self.dfolder_label['text'] = os.path.basename(self.raw_folder)
        self.button_ms1['state'] = NORMAL
        self.button_ms2['state'] = NORMAL


if __name__ == "__main__":
    RawFileTinker().mainloop()
