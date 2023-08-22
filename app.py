import logging
import os
import sys
import tarfile
from pathlib import Path

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QPushButton, QWidget, \
    QListView, QTreeView, QAbstractItemView, QSizePolicy, QTextEdit, QMessageBox, QLabel, QCheckBox, QSpinBox, \
    QDoubleSpinBox

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

raw_folders = []


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Set window title and size
        self.setWindowTitle("timsTofExtractorGUI")
        self.resize(500, 400)

        # Set font
        font = QFont()
        font.setPointSize(14)

        # Add padding to the layout
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # Create and style widgets
        self.select_button = QPushButton("Select .D Folders")
        self.select_button.clicked.connect(self.load_file)
        self.select_button.setFont(font)
        self.select_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(self.select_button)

        self.file_display = QTextEdit()
        self.file_display.setReadOnly(True)
        layout.addWidget(self.file_display)

        # Inputs for get_ms2_content
        layout.addWidget(QLabel("Include Spectra:"))
        self.include_spectra_input = QCheckBox()
        self.include_spectra_input.setChecked(True)
        layout.addWidget(self.include_spectra_input)

        layout.addWidget(QLabel("Batch Size:"))
        self.batch_size_input = QSpinBox()
        self.batch_size_input.setMinimum(0)
        self.batch_size_input.setMaximum(10000)
        self.batch_size_input.setValue(1000)
        layout.addWidget(self.batch_size_input)

        layout.addWidget(QLabel("Remove Charge 1 Spectra:"))
        self.remove_charge1_input = QCheckBox()
        self.remove_charge1_input.setChecked(True)
        layout.addWidget(self.remove_charge1_input)

        layout.addWidget(QLabel("Remove Empty Spectra:"))
        self.remove_empty_spectra_input = QCheckBox()
        self.remove_empty_spectra_input.setChecked(True)
        layout.addWidget(self.remove_empty_spectra_input)

        layout.addWidget(QLabel("Min Intensity:"))
        self.min_intensity_input = QDoubleSpinBox()
        self.min_intensity_input.setMinimum(0.0)
        self.min_intensity_input.setMaximum(100000.0)
        self.min_intensity_input.setValue(0.0)
        layout.addWidget(self.min_intensity_input)

        layout.addWidget(QLabel("Isotope Score:"))
        self.isotope_core = QCheckBox()
        self.isotope_core.setChecked(False)
        layout.addWidget(self.isotope_core)

        layout.addWidget(QLabel("Isotope Score (PPM):"))
        self.isotope_ppm = QDoubleSpinBox()
        self.isotope_ppm.setMinimum(0.0)
        self.isotope_ppm.setMaximum(100000.0)
        self.isotope_ppm.setValue(50.0)
        layout.addWidget(self.isotope_ppm)

        layout.addWidget(QLabel("Resolution (PRM & Isotope Scoring):"))
        self.resolution = QDoubleSpinBox()
        self.resolution.setMinimum(1000.0)
        self.resolution.setMaximum(120000.0)
        self.resolution.setValue(10000.0)
        layout.addWidget(self.resolution)

        layout.addWidget(QLabel("Deconvolute Spectra:"))
        self.deconvolute = QCheckBox()
        self.deconvolute.setChecked(False)
        layout.addWidget(self.deconvolute)

        layout.addWidget(QLabel("Deconvolute Score Threshold:"))
        self.deconvolute_score = QDoubleSpinBox()
        self.deconvolute_score.setMinimum(0.0)
        self.deconvolute_score.setMaximum(100.0)
        self.deconvolute_score.setValue(5.0)
        layout.addWidget(self.deconvolute_score)

        layout.addWidget(QLabel("Auto Scan Range (PRM):"))
        self.auto_scan_range = QCheckBox()
        self.auto_scan_range.setChecked(False)
        layout.addWidget(self.auto_scan_range)

        self.ms2_button = QPushButton("Generate Ms2 Files")
        self.ms2_button.clicked.connect(self.generate_ms2)
        self.ms2_button.setEnabled(False)
        self.ms2_button.setFont(font)
        self.ms2_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(self.ms2_button)

        self.compress_button = QPushButton("Tarball D Folders")
        self.compress_button.clicked.connect(self.compress_dfolder)
        self.compress_button.setEnabled(False)
        self.compress_button.setFont(font)
        self.compress_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(self.compress_button)

    def load_file(self):
        dlg = QFileDialog()
        dlg.setOption(QFileDialog.DontUseNativeDialog, True)
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        dlg.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        dlg.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)

        if dlg.exec_():
            global raw_folders
            raw_folders = dlg.selectedFiles()

        if raw_folders:
            logger.info(f'Files Selected: {raw_folders}')
            print(f'Files Selected: {raw_folders}')
            self.file_display.setPlainText('\n'.join(raw_folders))

        self.ms2_button.setEnabled(True)
        self.compress_button.setEnabled(True)

    def generate_ms2(self):
        self.compress_button.setEnabled(False)
        self.ms2_button.setEnabled(False)
        self.select_button.setEnabled(False)

        for i, raw_folder in enumerate(raw_folders):
            logger.info(f'Creating MS2 file for {raw_folder}')
            print(f'Creating MS2 file for {raw_folder}')

            QApplication.processEvents()

            write_ms2_file(analysis_dir=raw_folder,
                           include_spectra=self.include_spectra_input.isChecked(),
                           batch_size=self.batch_size_input.value(),
                           remove_charge1=self.remove_charge1_input.isChecked(),
                           remove_empty_spectra=self.remove_empty_spectra_input.isChecked(),
                           min_intensity=self.min_intensity_input.value(),
                           score_isotope_profile=self.isotope_core.isChecked(),
                           ppm=self.isotope_ppm.value(),
                           resolution=self.resolution.value(),
                           deisotope_spectra=self.deconvolute.isChecked(),
                           minimum_score=self.deconvolute_score.value(),
                           auto_scan_range=self.auto_scan_range.isChecked())

            logger.info(f'Path to MS2: {raw_folder + os.path.sep + Path(raw_folder).stem + ".ms2"}')
            print(f'Path to MS2: {raw_folder + os.path.sep + Path(raw_folder).stem + ".ms2"}')

        self.compress_button.setEnabled(True)
        self.ms2_button.setEnabled(True)
        self.select_button.setEnabled(True)
        QMessageBox.information(self, "Done", "Finished generating MS2 files!")

    def compress_dfolder(self):
        self.compress_button.setEnabled(False)
        self.ms2_button.setEnabled(False)
        self.select_button.setEnabled(False)

        for i, raw_folder in enumerate(raw_folders):
            logger.info(f'Creating tar file for {raw_folder}')
            print(f'Creating tar file for {raw_folder}')

            QApplication.processEvents()
            raw_folder_with_underlines = raw_folder.replace(" ", "_")
            with tarfile.open(raw_folder_with_underlines + '.tar', "w") as tar:
                for root, _, files in os.walk(raw_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        tar.add(file_path, arcname=os.path.relpath(file_path, Path(raw_folder).parent))

            logger.info(f'Path to tar file: {raw_folder_with_underlines + ".tar"}')
            print(f'Path to tar file: {raw_folder_with_underlines + ".tar"}')

        self.compress_button.setEnabled(True)
        self.ms2_button.setEnabled(True)
        self.select_button.setEnabled(True)
        QMessageBox.information(self, "Done", "Finished Creating Tar Files of D Folders!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
