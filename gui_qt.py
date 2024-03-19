import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QFileDialog, QHBoxLayout, QListWidget, QAction, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QSettings, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices
from timestamp import Worker
from datetime import datetime
import sys
import requests
from magicrenamer import MagicRenamerThread
from hwaccel_filter import filter_hwaccel_methods
from autodelete import delete_files
from magicrenamergui import MagicRenamerDialog

class MainWindow(QMainWindow):
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
    
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Video Timestamp")

        self.menu_bar = self.menuBar()
        self.settings_menu = self.menu_bar.addMenu("Settings")
        self.use_hwaccel_action = QAction("Use Hardware Acceleration", self)
        self.use_hwaccel_action.setCheckable(True)
        self.use_hwaccel_action.setChecked(self.settings.value('use_hwaccel', True, type=bool))
        self.use_hwaccel_action.triggered.connect(self.save_settings)
        self.settings_menu.addAction(self.use_hwaccel_action)
        self.remove_audio_action = QAction("Remove Audio", self)
        self.remove_audio_action.setCheckable(True)
        self.remove_audio_action.setChecked(self.settings.value('remove_audio', True, type=bool))
        self.remove_audio_action.triggered.connect(self.save_settings)
        self.settings_menu.addAction(self.remove_audio_action)
        self.delete_input_files_action = QAction("Delete Input Files When Finished", self)
        self.delete_input_files_action.setCheckable(True)
        self.delete_input_files_action.setChecked(self.settings.value('delete_input_files', False, type=bool))
        self.delete_input_files_action.triggered.connect(self.save_settings)
        self.settings_menu.addAction(self.delete_input_files_action)
        self.run_magic_renamer_when_finished_action = QAction("Run Magic Renamer When Finished", self)
        self.run_magic_renamer_when_finished_action.setCheckable(True)
        self.run_magic_renamer_when_finished_action.setChecked(self.settings.value('run_magic_renamer_when_finished', False, type=bool))
        self.run_magic_renamer_when_finished_action.triggered.connect(self.save_settings)
        self.settings_menu.addAction(self.run_magic_renamer_when_finished_action)

        self.fixes_menu = self.menu_bar.addMenu("Fixes")
        self.manually_adjusted_for_dst_action = QAction("Manually set DST", self)
        self.manually_adjusted_for_dst_action.setCheckable(True)
        self.manually_adjusted_for_dst_action.triggered.connect(self.save_settings)
        self.fixes_menu.addAction(self.manually_adjusted_for_dst_action)
        self.add_hour_action = QAction("Adjust timestamp +1 hour", self)
        self.add_hour_action.setCheckable(True)
        self.add_hour_action.setChecked(self.settings.value('add_hour', False, type=bool))
        self.add_hour_action.triggered.connect(self.save_settings)
        self.fixes_menu.addAction(self.add_hour_action)
        self.subtract_hour_action = QAction("Adjust timestamp -1 hour", self)
        self.subtract_hour_action.setCheckable(True)
        self.subtract_hour_action.setChecked(self.settings.value('subtract_hour', False, type=bool))
        self.subtract_hour_action.triggered.connect(self.save_settings)
        self.fixes_menu.addAction(self.subtract_hour_action)

        self.tools_menu = self.menu_bar.addMenu("Tools")
        self.magic_renamer_action = QAction("Magic Renamer", self)
        self.magic_renamer_action.triggered.connect(self.launch_magic_renamer_gui)
        self.tools_menu.addAction(self.magic_renamer_action)

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
        self.hwaccel_method = filter_hwaccel_methods() 

        self.process_button = QPushButton("Timestamp Videos")
        self.process_button.clicked.connect(self.main)
        self.process_button.setEnabled(False)
        self.layout.addWidget(self.process_button)

        self.progress = QProgressBar()
        self.progress.hide()
        self.layout.addWidget(self.progress)
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

        self.check_for_updates()

    def check_for_updates(self):
        current_version = "1.1.1_BETA4"
        repo_owner = "rwpi"
        repo_name = "videotimestamp"

        try:
            response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest")
            response.raise_for_status() 
            data = response.json()

            if data.get("tag_name") and data["tag_name"] > f"VTS-{current_version}":
                self.version_label.setText(f'Update available! Current version: {current_version}')
                self.version_label.setStyleSheet("color: red; font-size: 10px;")
            else:
                self.version_label.setText(f"Ver. {current_version}")
                self.version_label.setStyleSheet("color: grey; font-size: 10px;")
        except requests.exceptions.RequestException:
            print("Failed to check for updates")
            self.version_label.setText(f"Ver. {current_version}")
            self.version_label.setStyleSheet("color: grey; font-size: 10px;")

    def launch_magic_renamer_gui(self):
        self.magic_renamer_gui = MagicRenamerDialog(self.output_folder_path)
        self.magic_renamer_gui.show()

    def start_magic_renamer(self):
        directory = self.output_folder_path
        if directory:
            self.magic_renamer_thread = MagicRenamerThread(directory)
            self.magic_renamer_thread.start()
        else:
            QMessageBox.warning(self, "No Output Folder", "Please choose an output folder before starting the magic renamer.")

    def open_update_link(self, link):
        QDesktopServices.openUrl(QUrl(link))

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
        self.settings.setValue('remove_audio', self.remove_audio_action.isChecked())
        self.settings.setValue('use_hwaccel', self.use_hwaccel_action.isChecked())
        self.settings.setValue('manually_adjusted_for_dst', self.manually_adjusted_for_dst_action.isChecked())
        self.settings.setValue('add_hour', self.add_hour_action.isChecked())
        self.settings.setValue('subtract_hour', self.subtract_hour_action.isChecked())
        self.settings.setValue('delete_input_files', self.delete_input_files_action.isChecked())
        self.settings.setValue('run_magic_renamer_when_finished', self.run_magic_renamer_when_finished_action.isChecked())

    def on_worker_finished(self):
        self.timer.stop()
        self.progress.show()
        self.process_button.setEnabled(True)
        if self.settings.value('delete_input_files', False, type=bool):
            delete_files(self.input_files)
        if self.settings.value('run_magic_renamer_when_finished', False, type=bool):
            self.start_magic_renamer()

    def open_folder(self):
        if self.output_folder_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_folder_path))

    def main(self):
        self.progress.show()
        if self.input_files:
            self.timer.start(500)
            hwaccel_method = self.hwaccel_method if self.settings.value('use_hwaccel', True, type=bool) else 'libx264'
            remove_audio = self.settings.value('remove_audio', True, type=bool)
            manually_adjusted_for_dst = self.manually_adjusted_for_dst_action.isChecked()
            add_hour = self.settings.value('add_hour', False, type=bool)
            subtract_hour = self.settings.value('subtract_hour', False, type=bool)
            self.worker = Worker(self.input_files, self.output_folder_path, hwaccel_method, remove_audio, manually_adjusted_for_dst, add_hour, subtract_hour)
            self.worker.progressChanged.connect(self.progress.setValue)
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()
            self.process_button.setEnabled(False)

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()