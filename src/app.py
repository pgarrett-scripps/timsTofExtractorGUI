import logging
import os
from pathlib import Path
from tkinter import filedialog as fd, messagebox
from tkinter import *
import sys

from PyQt5.QtWidgets import QFileDialog, QListView, QAbstractItemView, QTreeView, QApplication, QDialog
from tdfextractor.ms2_extractor import write_ms2_file

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

        def generate_ms1(raw_folder):
            return 'NotImplemented'

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

        for i, raw_folder in enumerate(self.raw_folders):
            self.dfolder_label['text'] = f'Extracting: {Path(raw_folder).stem}'
            self.percent_done_ms2_text['text'] = f'File {i+1} of {len(self.raw_folders)}'
            self.update()
            write_ms2_file(raw_folder)

        self.percent_done_ms2_text['text'] = str(round(100.00, 2)) + "%"
        self.update()

        messagebox.showinfo('Done!', 'Ms2 Files created!')

        self.button_ms1['state'] = NORMAL
        self.button_ms2['state'] = NORMAL
        self.button['state'] = NORMAL

    def load_file(self):

        class getExistingDirectories(QFileDialog):
            def __init__(self, *args):
                super(getExistingDirectories, self).__init__(*args)
                self.setOption(self.DontUseNativeDialog, True)
                self.setFileMode(self.Directory)
                self.setOption(self.ShowDirsOnly, True)
                self.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)

        q = QApplication(sys.argv)
        dlg = getExistingDirectories()
        if dlg.exec_() == QDialog.Accepted:
            self.raw_folders = dlg.selectedFiles()

        number_files_selected = 0
        if self.raw_folders:
            number_files_selected = len(self.raw_folders)

        self.dfolder_label['text'] = f'Files selected: {number_files_selected}'
        self.button_ms1['state'] = NORMAL
        self.button_ms2['state'] = NORMAL


if __name__ == "__main__":
    RawFileTinker().mainloop()
