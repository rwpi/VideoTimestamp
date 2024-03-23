import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFileDialog, QMainWindow, QMessageBox, QProgressDialog
from PyQt5.QtCore import Qt, QSettings, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices
from timestamp import Worker
from magicrenamer import MagicRenamerThread
from autodelete import delete_files
from magicrenamergui import MagicRenamerDialog
from importtoday import ImportThread
from check_for_updates import check_for_updates
from menubar import setup_menu_bar
from ui_setup import setup_ui

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        self.input_files = set()

        self.settings = QSettings('VideoTimestamp', 'VTS')
        self.layout = QVBoxLayout()
        self.copyright_label = QLabel()
        self.copyright_label.setStyleSheet("color: grey; font-size: 10px;")
        self.output_folder_path = ""
    
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        setup_menu_bar(self)
  
        self.setWindowTitle("Video Timestamp")
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        splashgraphic_path = os.path.join(base_path, 'splashgraphic.png')
        pixmap = QPixmap(splashgraphic_path)
        self.logo_label.setPixmap(pixmap)
        self.layout.addWidget(self.logo_label)      

        setup_ui(self)

        self.check_for_updates()

    def check_for_updates(self):
        text, style = check_for_updates()
        self.version_label.setText(text)
        self.version_label.setStyleSheet(style)

    def launch_magic_renamer_gui(self):
        self.magic_renamer_gui = MagicRenamerDialog(self.output_folder_path)
        self.magic_renamer_gui.show()

    def start_magic_renamer(self):
        directory = self.output_folder_path
        if directory:
            self.magic_renamer_thread = MagicRenamerThread(directory)
            self.magic_renamer_thread.start()
        else:
            QMessageBox.warning(self, "No Output Folder", "Please choose an output folder before starting the rename tool.")

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
        self.input_files = set()
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
        self.progress_dialog.hide()
        self.process_button.setEnabled(True)
        if self.settings.value('delete_input_files', False, type=bool):
            delete_files(self.input_files)
        if self.settings.value('run_magic_renamer_when_finished', False, type=bool):
            self.start_magic_renamer()

    def open_folder(self):
        if self.output_folder_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_folder_path))

    def main(self):
        self.progress_dialog.show()
        if self.input_files:
            self.timer.start(500)
            hwaccel_method = self.hwaccel_method if self.settings.value('use_hwaccel', True, type=bool) else 'libx264'
            remove_audio = self.settings.value('remove_audio', True, type=bool)
            manually_adjusted_for_dst = self.manually_adjusted_for_dst_action.isChecked()
            add_hour = self.settings.value('add_hour', False, type=bool)
            subtract_hour = self.settings.value('subtract_hour', False, type=bool)
            self.worker = Worker(self.input_files, self.output_folder_path, hwaccel_method, remove_audio, manually_adjusted_for_dst, add_hour, subtract_hour)
            self.worker.progressChanged.connect(self.progress_dialog.progress.setValue)
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()
            self.process_button.setEnabled(False)

    def start_import(self):
        self.import_thread = ImportThread()
        self.import_thread.progress.connect(self.update_progress)
        self.import_thread.finished.connect(self.finish_import)
        self.import_thread.start()
        self.progress_dialog.progress_dialog = QProgressDialog("Importing...", "Cancel", 0, 100, self)
        self.progress_dialog.progress_dialog.setWindowTitle("Importer") 
        self.progress_dialog.progress_dialog.setWindowFlags(self.progress_dialog.progress_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.progress_dialog.progress_dialog.canceled.connect(self.import_thread.terminate)
        self.progress_dialog.progress_dialog.show()
        self.import_thread.finished.connect(self.set_output_folder)
        self.import_thread.finished.connect(self.add_new_files)

    def update_progress(self, value):
        self.progress_dialog.progress_dialog.setValue(value)

    def finish_import(self):
        self.progress_dialog.progress_dialog.close()

    def set_output_folder(self, folder_path):
        self.output_folder_path = folder_path
        folder_name = os.path.basename(self.output_folder_path)
        self.output_folder_label.setText(f"Output Folder: {folder_name}")
        self.check_if_ready_to_process()
        
    def add_new_files(self, folder_path, new_files):
        self.output_folder = folder_path
        self.input_files.update(new_files)
        self.input_files_label.setText(f"{len(self.input_files)} Input Files Selected")
        self.input_files_list.clear()
        for file in self.input_files:
            self.input_files_list.addItem(os.path.basename(file)) 
        self.check_if_ready_to_process()

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()