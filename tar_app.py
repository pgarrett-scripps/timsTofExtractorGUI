import logging
import os
import sys
import tarfile
from pathlib import Path

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QPushButton, QWidget, \
    QListView, QTreeView, QAbstractItemView, QSizePolicy, QTextEdit, QMessageBox, QLabel

exe_dir = os.path.dirname(sys.executable)
log_file_path = os.path.join(exe_dir, "folderTarGUI.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename=log_file_path,
    filemode='a'
)

logger = logging.getLogger('folderTarGUI')

logger.info('Start folderTarGUI')
print('Start folderTarGUI')
logger.info(f'log_file_path: {log_file_path}')
print(f'log_file_path: {log_file_path}')

selected_folders = []
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle("Folder Tar Creator")
        self.resize(700, 500)  # Larger window size

        font = QFont()
        font.setPointSize(12)

        # More padding
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title label
        title_label = QLabel("Folder Tar Creator")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Select button with styling
        self.select_button = QPushButton("📁 Select Folders")
        self.select_button.clicked.connect(self.load_folders)
        button_font = QFont()
        button_font.setPointSize(13)
        self.select_button.setFont(button_font)
        self.select_button.setMinimumHeight(50)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        layout.addWidget(self.select_button)

        # Info label
        info_label = QLabel("Selected folders:")
        info_label.setFont(font)
        info_label.setStyleSheet("color: #34495e; font-weight: bold;")
        layout.addWidget(info_label)

        # File display with styling
        self.file_display = QTextEdit()
        self.file_display.setReadOnly(True)
        self.file_display.setFont(font)
        self.file_display.setStyleSheet("""
            QTextEdit {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                color: #2c3e50;
            }
        """)
        layout.addWidget(self.file_display)

        # Tar button with styling
        self.tar_button = QPushButton("🗜️ Create Tar Files")
        self.tar_button.clicked.connect(self.create_tar_files)
        self.tar_button.setEnabled(False)
        self.tar_button.setFont(button_font)
        self.tar_button.setMinimumHeight(50)
        self.tar_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        layout.addWidget(self.tar_button)

        # Set overall window styling
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)

    def load_folders(self):
        dlg = QFileDialog()
        dlg.setOption(QFileDialog.DontUseNativeDialog, True)
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        dlg.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        dlg.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Make the dialog larger
        dlg.resize(1000, 700)

        if dlg.exec_():
            global selected_folders
            # Filter to only include folders ending in .d
            all_selected = dlg.selectedFiles()
            selected_folders = [f for f in all_selected if f.lower().endswith('.d')]
            
            if len(all_selected) != len(selected_folders):
                QMessageBox.warning(self, "Warning", 
                    f"Only {len(selected_folders)} out of {len(all_selected)} selected folders end in .d\n"
                    "Non-.d folders have been excluded.")

        if selected_folders:
            logger.info(f'Folders Selected: {selected_folders}')
            print(f'Folders Selected: {selected_folders}')
            
            # Display only the folder names (not full paths)
            folder_names = [Path(f).name for f in selected_folders]
            self.file_display.setPlainText('\n'.join(folder_names))

        self.tar_button.setEnabled(bool(selected_folders))

    def create_tar_files(self):
        self.tar_button.setEnabled(False)
        self.select_button.setEnabled(False)

        for folder in selected_folders:
            logger.info(f'Creating tar file for {folder}')
            print(f'Creating tar file for {folder}')

            QApplication.processEvents()
            
            # Get the parent directory where the folder is located
            parent_dir = Path(folder).parent
            folder_name = Path(folder).name.replace(" ", "_")
            
            # Create tar file in the SAME directory as the source folder
            tar_path = parent_dir / f"{folder_name}.tar"
            
            with tarfile.open(tar_path, "w") as tar:
                tar.add(folder, arcname=Path(folder).name)

            logger.info(f'Created tar file: {tar_path}')
            print(f'Created tar file: {tar_path}')

        self.tar_button.setEnabled(True)
        self.select_button.setEnabled(True)
        QMessageBox.information(self, "Done", f"Created {len(selected_folders)} tar file(s)!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())