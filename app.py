import logging
import os
from pathlib import Path
from tkinter import filedialog as fd, messagebox
from tkinter import *
import sys
import tarfile

from PyQt5.QtWidgets import QFileDialog, QListView, QAbstractItemView, QTreeView, QApplication, QDialog
from tdfextractor.ms2_extractor import write_ms2_file

exe_dir = os.path.dirname(sys.executable)
log_file_path = os.path.join(exe_dir, "timsTofExtractorGUI.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename=log_file_path,
    filemode='a'
)

logger = logging.getLogger('timsTofExtractorGUI')

logger.info('Start timsTofExtractorGUI')
print('Start timsTofExtractorGUI')
logger.info(f'log_file_path: {log_file_path}')
print(f'log_file_path: {log_file_path}')


class RawFileTinker(Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.raw_folder = None
        self.generating_file = False

        self._frame_width = 80

        self.master.title("timsTofExtractorGUI")
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W + E + N + S)

        self.create_widgets()

        self.raw_folders = []

    def create_widgets(self):
        self.button = Button(self, text="Select D folder", command=self.load_file, width=self._frame_width)
        self.button.pack(expand=True)

        self.dfolder_label = Label(self, text="no file selected", width=self._frame_width, height=2)
        self.dfolder_label.pack(expand=True)

        self.ms2_frame = Frame(self)
        self.ms2_frame.pack(expand=True)

        self.button_ms2 = Button(self.ms2_frame, text="Generate Ms2 Files", command=self.generate_ms2,
                                 width=int(self._frame_width / 2), state=DISABLED)
        self.button_ms2.pack(side=LEFT, expand=True)

        self.percent_done_ms2_text = Label(self.ms2_frame, text="", width=int(self._frame_width / 2), height=2)
        self.percent_done_ms2_text.pack(side=RIGHT, expand=True)

        self.compress_frame = Frame(self)
        self.compress_frame.pack(expand=True)

        self.button_compress = Button(self.compress_frame, text="Tarball D Folders", command=self.compress_dfolder,
                                      width=int(self._frame_width / 2), state=DISABLED)
        self.button_compress.pack(side=LEFT, expand=True)

        self.percent_done_compress_text = Label(self.compress_frame, text="", width=int(self._frame_width / 2),
                                                height=2)
        self.percent_done_compress_text.pack(side=RIGHT, expand=True)

    def generate_ms2(self):

        self.button_compress['state'] = DISABLED
        self.button_ms2['state'] = DISABLED
        self.button['state'] = DISABLED

        for i, raw_folder in enumerate(self.raw_folders):

            logger.info(f'Generating MS2: {raw_folder}')
            print(f'Generating MS2: {raw_folder}')

            self.dfolder_label['text'] = f'Generating MS2: {Path(raw_folder).stem}'
            self.percent_done_ms2_text['text'] = f'File {i + 1} of {len(self.raw_folders)}'
            self.update()

            write_ms2_file(raw_folder)

            logger.info(f'Done. Path to MS2: {raw_folder + os.path.sep + Path(raw_folder).stem + ".ms2"}')
            print(f'Done. Path to MS2: {raw_folder + os.path.sep + Path(raw_folder).stem + ".ms2"}')

        self.update()

        messagebox.showinfo('Done!', f'Generated {len(self.raw_folders)} MS2 Files')

        self.button_compress['state'] = NORMAL
        self.button_ms2['state'] = NORMAL
        self.button['state'] = NORMAL

        self.dfolder_label['text'] = f'Files selected: {len(self.raw_folders)}'


    def compress_dfolder(self):

        self.button_compress['state'] = DISABLED
        self.button_ms2['state'] = DISABLED
        self.button['state'] = DISABLED

        for i, raw_folder in enumerate(self.raw_folders):
            logger.info(f'Tarballing: {raw_folder}')
            print(f'Tarballing: {raw_folder}')

            self.dfolder_label['text'] = f'Tarballing: {Path(raw_folder).stem}'
            self.percent_done_compress_text['text'] = f'File {i + 1} of {len(self.raw_folders)}'
            with tarfile.open(raw_folder + '.tar', "w") as tar:
                for root, _, files in os.walk(raw_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        tar.add(file_path, arcname=os.path.relpath(file_path, raw_folder))

            logger.info(f'Done. Path to tarball: {raw_folder + ".tar"}')
            print(f'Done. Path to tarball: {raw_folder + ".tar"}')

            self.update()

        self.update()

        messagebox.showinfo('Done!', f'Tarballed {len(self.raw_folders)} files')

        self.button_compress['state'] = NORMAL
        self.button_ms2['state'] = NORMAL
        self.button['state'] = NORMAL

        self.dfolder_label['text'] = f'Files selected: {len(self.raw_folders)}'


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
            logger.info(f'Files Selected: {self.raw_folders}')
            print(f'Files Selected: {self.raw_folders}')

        self.dfolder_label['text'] = f'Files selected: {number_files_selected}'
        self.button_ms2['state'] = NORMAL
        self.button_compress['state'] = NORMAL


if __name__ == "__main__":
    RawFileTinker().mainloop()
