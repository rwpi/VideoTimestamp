from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from magicrenamer import MagicRenamerThread
import os 

class MagicRenamerDialog(QDialog):
    def __init__(self, output_folder_path, parent=None):
        super().__init__(parent)
        self.output_folder_path = output_folder_path
        self.magic_renamer_thread = None

        self.setWindowTitle("Renamer")
        self.layout = QVBoxLayout(self)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.select_folder_button = QPushButton("Select Target Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_folder_button)

        self.folder_label = QLabel('')  # initialize with empty string
        self.folder_label.setStyleSheet("color: grey; font-size: 10px;")
        self.folder_label.setOpenExternalLinks(True)  # allow the label to open external links
        self.layout.addWidget(self.folder_label)

        self.start_button = QPushButton("Rename Files")
        self.start_button.clicked.connect(self.start_magic_renamer)
        self.start_button.setEnabled(bool(self.output_folder_path))  # disable the button if no output folder path is set
        self.layout.addWidget(self.start_button)

        self.done_label = QLabel("")  # add a label for the "Done!" message
        self.done_label.setStyleSheet("color: green; font-size: 20px;")
        self.done_label.setAlignment(Qt.AlignCenter)  # center the text
        self.layout.addWidget(self.done_label)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Target Folder", self.output_folder_path)
        if folder:
            self.output_folder_path = folder
            self.folder_label.setText(f'Target Folder: <a href="file:///{self.output_folder_path}">{os.path.basename(self.output_folder_path)}</a>')  # make the folder name a link
            self.start_button.setEnabled(True)  # enable the button when a folder is selected

    def start_magic_renamer(self):
        if self.output_folder_path:
            self.magic_renamer_thread = MagicRenamerThread(self.output_folder_path)
            self.magic_renamer_thread.finished.connect(self.on_renamer_finished)  # connect to the finished signal
            self.magic_renamer_thread.start()
        else:
            QMessageBox.warning(self, "No Target Folder", "Please choose a target folder before starting the magic renamer.")

    def on_renamer_finished(self):  # new method
        self.done_label.setText('DONE!')