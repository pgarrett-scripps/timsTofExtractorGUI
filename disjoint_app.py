import os
from pathlib import Path

from tkinter import messagebox, ttk
from tkinter import *

import sys
from PyQt5.QtWidgets import (QFileDialog, QAbstractItemView, QListView,
                             QTreeView, QApplication, QDialog)

RAW_CONVERTOR_PATH = Path('C:\\Users\\diash\\scripts\\tdf2ms2\\extract_msn_nopd.py')


class getExistingDirectories(QFileDialog):
    def __init__(self, *args):
        super(getExistingDirectories, self).__init__(*args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.Directory)
        self.setOption(self.ShowDirsOnly, True)
        self.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)


class RawFileTinker(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.raw_folders = None
        self.generating_file = False

        self._frame_width = 100

        self.master.title("RawFileExtractor")
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W + E + N + S)

        self.folder_frame = Frame(self)
        self.folder_frame.pack(expand=True)

        self.button = Button(self.folder_frame, text="Select D folders", command=self.load_file, width=int(self._frame_width / 3))
        self.button.pack(side=LEFT, expand=True)

        self.overwrite_flag = StringVar()
        self.overwrite_button = ttk.Checkbutton(self.folder_frame,
                                                text='overwrite ms2 files',
                                                variable=self.overwrite_flag,
                                                onvalue=True,
                                                offvalue=False)
        self.overwrite_button.pack(side=RIGHT, expand=True)

        self.dfolder_label = Label(self, text="no file selected", width=self._frame_width, height=2)
        self.dfolder_label.pack(expand=True)

        self.ms1_frame = Frame(self)
        self.ms1_frame.pack(expand=True)

        self.button_ms1 = Button(self.ms1_frame, text="Generate Ms1 Files", command=self.generate_ms1,
                                 width=int(self._frame_width / 3), state=DISABLED)
        self.button_ms1.pack(side=LEFT, expand=True)

        self.percent_done_ms1_text = Label(self.ms1_frame, text="0%", width=int(self._frame_width / 3 * 2), height=2)
        self.percent_done_ms1_text.pack(side=RIGHT, expand=True)

        self.ms2_frame = Frame(self)
        self.ms2_frame.pack(expand=True)

        self.button_ms2 = Button(self.ms2_frame, text="Generate Ms2 Files", command=self.generate_ms2s,
                                 width=int(self._frame_width / 3), state=DISABLED)
        self.button_ms2.pack(side=LEFT, expand=True)

        self.percent_done_ms2_text = Label(self.ms2_frame, text="0%", width=int(self._frame_width / 3 * 2), height=2)
        self.percent_done_ms2_text.pack(side=RIGHT, expand=True)

        directions = "Directions\n" \
                     " 1) Use shift/ctrl click to highlight multiple folders.\n" \
                     " 2) Press either ms1 or ms2 button.\n" \
                     " 3) Wait :) \n" \
                     " 4) ms1/ms2 files will be generated in the D folder with the same name as the folder.\n" \
                     " \n" \
                     "Note: Ms1 files are very large for timsTof experiments ~50 GB\n" \
                     " - Made by Patrick Garrett 8/6/2021"
        messagebox.showinfo("Version 1.0", directions)

    def generate_ms1(self):

        self.button_ms1['state'] = DISABLED
        self.button_ms2['state'] = DISABLED
        self.button['state'] = DISABLED

        for i, folder in enumerate(self.raw_folders):

            percent_done = round((i + 1) / len(self.raw_folders) * 100)
            self.percent_done_ms2_text['text'] = f'processing: {os.path.basename(folder)}'
            self.master.title(f"RawFileExtractor {percent_done}%")
            self.update()

            ms1_file_path = os.path.join(folder, os.path.basename(folder) + ".ms1")
            contains_file = os.path.exists(ms1_file_path)
            if contains_file and not self.overwrite_flag.get():
                print(f"Ms1 file exists: {ms1_file_path} skipping...")
            else:
                os.system(f'python {RAW_CONVERTOR_PATH} {folder}')

        self.button_ms1['state'] = NORMAL
        self.button_ms2['state'] = NORMAL
        self.button['state'] = NORMAL

    def generate_ms2s(self):

        self.button_ms2['state'] = DISABLED
        self.button_ms1['state'] = DISABLED
        self.button['state'] = DISABLED

        for i, folder in enumerate(self.raw_folders):

            percent_done = round((i + 1)/len(self.raw_folders)*100)
            self.percent_done_ms2_text['text'] = f'processing: {os.path.basename(folder)}'
            self.master.title(f"RawFileExtractor {percent_done}%")
            self.update()

            ms2_file_path = os.path.join(folder, os.path.basename(folder) + ".ms2")
            contains_file = os.path.exists(ms2_file_path)
            if contains_file and not self.overwrite_flag.get():
                print(f"Ms2 file exists: {ms2_file_path} skipping...")
            else:
                os.system(f'python {RAW_CONVERTOR_PATH} {folder}')


        self.button_ms1['state'] = NORMAL
        self.button_ms2['state'] = NORMAL
        self.button['state'] = NORMAL

    def load_file(self):

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
