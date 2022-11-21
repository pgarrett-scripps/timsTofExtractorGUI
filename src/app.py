import logging
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

        self.ms2_frame = Frame(self)
        self.ms2_frame.pack(expand=True)

        self.button_ms2 = Button(self.ms2_frame, text="Generate Ms2 File", command=self.generate_ms2,
                                 width=int(self._frame_width / 2), state=DISABLED)
        self.button_ms2.pack(side=LEFT, expand=True)

        self.percent_done_ms2_text = Label(self.ms2_frame, text="0%", width=int(self._frame_width / 2), height=2)
        self.percent_done_ms2_text.pack(side=RIGHT, expand=True)

    def generate_ms2(self):

        self.button_ms2['state'] = DISABLED
        self.button['state'] = DISABLED

        for i, raw_folder in enumerate(self.raw_folders):
            self.dfolder_label['text'] = f'Extracting: {Path(raw_folder).stem}'
            self.percent_done_ms2_text['text'] = f'File {i + 1} of {len(self.raw_folders)}'
            self.update()
            write_ms2_file(raw_folder)

        self.percent_done_ms2_text['text'] = str(round(100.00, 2)) + "%"
        self.update()

        messagebox.showinfo('Done!', 'Ms2 Files created!')

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
        self.button_ms2['state'] = NORMAL


if __name__ == "__main__":
    RawFileTinker().mainloop()
