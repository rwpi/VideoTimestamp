from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QListWidget, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
from hwaccel_filter import filter_hwaccel_methods

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Timestamp")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Progress")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel("Timestamping...")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

def setup_ui(self):
    self.choose_input_files_button = QPushButton("Choose Input Files")
    self.choose_input_files_button.clicked.connect(self.choose_input_files)
    self.layout.addWidget(self.choose_input_files_button)
    self.input_files_label = QLabel("0 Input Files Selected")
    self.input_files_label.setStyleSheet("color: grey; font-size: 10px;")
    self.reset_input_files_label = QLabel('<a href="#">Reset</a>')
    self.reset_input_files_label.setStyleSheet("color: blue; font-size: 10px;")
    self.reset_input_files_label.linkActivated.connect(self.reset_input_files)
    self.input_files_layout = QHBoxLayout()
    self.input_files_layout.addWidget(self.input_files_label)
    self.input_files_layout.addStretch(1)
    self.input_files_layout.addWidget(self.reset_input_files_label)
    self.layout.addLayout(self.input_files_layout)
    self.input_files_list = QListWidget()
    self.input_files_list.setMaximumHeight(100)
    self.layout.addWidget(self.input_files_list)
    self.choose_button = QPushButton("Choose Output Folder")
    self.choose_button.clicked.connect(self.choose_output_folder)
    self.layout.addWidget(self.choose_button)        
    self.output_folder_label = QLabel("Output Folder:")
    self.output_folder_label.setStyleSheet("color: grey; font-size: 10px;")
    self.reset_output_folder_label = QLabel('<a href="#">Reset</a>')
    self.reset_output_folder_label.setStyleSheet("color: blue; font-size: 10px;")
    self.reset_output_folder_label.linkActivated.connect(self.reset_output_folder)

    self.view_output_folder_label = QLabel('<a href="#">View</a>')
    self.view_output_folder_label.setStyleSheet("color: blue; font-size: 10px;")

    self.view_output_folder_label.linkActivated.connect(self.open_folder)

    self.output_folder_layout = QHBoxLayout()
    self.output_folder_layout.addWidget(self.output_folder_label)
    self.output_folder_layout.addStretch(1)

    self.output_folder_layout.addWidget(self.view_output_folder_label)
    self.output_folder_layout.addWidget(self.reset_output_folder_label)

    self.layout.addLayout(self.output_folder_layout)    
    self.hwaccel_method = filter_hwaccel_methods() 

    self.process_button = QPushButton("Timestamp Videos")
    self.process_button.clicked.connect(self.main)
    self.process_button.setEnabled(False)
    self.layout.addWidget(self.process_button)

    self.progress_dialog = ProgressDialog(self)
    self.progress_dialog.hide()

    self.timer = QTimer()

    current_year = datetime.now().year
    self.copyright_label.setText(f"© {current_year} Robert Webber")
    self.layout.addWidget(self.copyright_label)
    self.copyright_label.setAlignment(Qt.AlignCenter)

    self.link_label = QLabel()
    self.link_label.setText('<a href="https://www.videotimestamp.com">www.videotimestamp.com</a>')
    self.link_label.setStyleSheet("color: grey; font-size: 10px;")
    self.link_label.setOpenExternalLinks(True)
    self.layout.addWidget(self.link_label)
    self.link_label.setAlignment(Qt.AlignCenter)
    self.layout.addWidget(self.link_label)

    self.version_label = QLabel()
    self.version_label.setStyleSheet("color: grey; font-size: 10px;")
    self.version_label.setAlignment(Qt.AlignCenter)

    self.layout.addWidget(self.version_label)