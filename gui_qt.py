import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QCheckBox, QLabel, QProgressBar, QFileDialog, QHBoxLayout, QListWidget
from PyQt5.QtCore import Qt, QTimer, QSettings, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices
from timestamp import Worker
from datetime import datetime
import sys
import platform

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        self.input_files = []

        self.settings = QSettings('VideoTimestamp', 'VTS')
        self.layout = QVBoxLayout()
        self.copyright_label = QLabel()
        self.copyright_label.setStyleSheet("color: grey; font-size: 10px;")
        self.output_folder_path = ""
    

        self.setWindowTitle("Video Timestamp")

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        splashgraphic_path = os.path.join(base_path, 'splashgraphic.png')
        pixmap = QPixmap(splashgraphic_path)
        self.logo_label.setPixmap(pixmap)
        self.layout.addWidget(self.logo_label)      

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
        
        self.hwaccel_method = self.filter_hwaccel_methods()
       
        self.remove_audio_checkbox = QCheckBox("Remove Audio")
        self.remove_audio_checkbox.setChecked(self.settings.value('remove_audio', True, type=bool))
        self.remove_audio_checkbox.stateChanged.connect(self.save_settings)
        self.layout.addWidget(self.remove_audio_checkbox)

        self.use_hwaccel_checkbox = QCheckBox("Use Hardware Acceleration")
        self.use_hwaccel_checkbox.setChecked(self.settings.value('use_hwaccel', True, type=bool))
        self.use_hwaccel_checkbox.stateChanged.connect(self.save_settings)
        if self.hwaccel_method == 'libx264':
            self.use_hwaccel_checkbox.setEnabled(False)
        self.layout.addWidget(self.use_hwaccel_checkbox)

        self.process_button = QPushButton("Timestamp Videos")
        self.process_button.clicked.connect(self.main)
        self.process_button.setEnabled(False)
        self.layout.addWidget(self.process_button)

        self.progress = QProgressBar()
        self.progress.hide()
        self.layout.addWidget(self.progress)

        self.timer = QTimer()

        self.setLayout(self.layout)

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

        self.setLayout(self.layout)

#    def check_for_updates(self):
#        current_version = "VTS-1.0.2"  # replace with your current version
#        repo_owner = "rwpi"
#        repo_name = "videotimestamp"
#
#        try:
#            response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest")
#            response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
#            data = response.json()
#
#            if data.get("tag_name") and data["tag_name"] > current_version:
#                self.update_label.setText('<a href="{0}">Update Available</a>'.format(data["html_url"]))
#        except requests.exceptions.RequestException:
#            print("Failed to check for updates")
            
#    def open_update_link(self, link):
#        QDesktopServices.openUrl(QUrl(link))


    def update_output_folder_path(self, path):
        self.output_folder_path = path

    def open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_folder_path))

    def choose_output_folder(self):
        self.output_folder_path = QFileDialog.getExistingDirectory(self, 'Select a folder:')
        if self.output_folder_path:
            folder_name = os.path.basename(self.output_folder_path)
            self.output_folder_label.setText(f"Output Folder: {folder_name}")
            self.check_if_ready_to_process()

    def choose_input_files(self):
        new_input_files, _ = QFileDialog.getOpenFileNames(self, 'Select .MTS files', '', 'MTS Files (*.MTS)')
        if new_input_files:
            self.input_files.extend(new_input_files)
            self.input_files_label.setText(f"{len(self.input_files)} Input Files Selected")
            self.input_files_list.clear()
            for file in self.input_files:
                self.input_files_list.addItem(os.path.basename(file)) 
            self.check_if_ready_to_process()
    
    def reset_input_files(self):
        self.input_files = []
        self.input_files_label.setText("0 Input Files Selected")
        self.input_files_list.clear()
        self.check_if_ready_to_process()

    def reset_output_folder(self):
        self.output_folder_path = ""
        self.output_folder_label.setText("Output Folder:")
        self.check_if_ready_to_process()

    def check_if_ready_to_process(self):
        if self.input_files and self.output_folder_path:
            self.process_button.setEnabled(True)
        else:
            self.process_button.setEnabled(False)

    def save_settings(self):
        self.settings.setValue('remove_audio', self.remove_audio_checkbox.isChecked())
        self.settings.setValue('use_hwaccel', self.use_hwaccel_checkbox.isChecked())

    def on_worker_finished(self):
        self.timer.stop()
        self.progress.show()
        self.process_button.setEnabled(True)  # Enable the button when the worker finishes

    def open_folder(self):
        if self.output_folder_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_folder_path))

    def main(self):
        self.progress.show()
        if self.input_files:
            self.timer.start(500)
            hwaccel_method = self.hwaccel_method if self.use_hwaccel_checkbox.isChecked() else 'libx264'
            remove_audio = self.remove_audio_checkbox.isChecked()
            self.worker = Worker(self.input_files, self.output_folder_path, hwaccel_method, remove_audio) 
            self.worker.progressChanged.connect(self.progress.setValue)
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()
            self.process_button.setEnabled(False)  # Disable the button when the worker starts

    def filter_hwaccel_methods(self):
        system = platform.system()
        cpu_info = platform.processor()

        if system == 'Darwin':
            return 'h264_videotoolbox'
        elif system == 'Windows':
            if 'Intel' in cpu_info:
                return 'h264_qsv'
            elif 'AMD' in cpu_info:
                return 'h264_amf'
            elif 'ARM' in cpu_info:
                return 'libx264'
        else:
            return 'libx264'

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()