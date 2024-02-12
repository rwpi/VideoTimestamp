import subprocess
import os
import datetime
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import stat

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
        if 'exiftool' in relative_path or 'ffmpeg' in relative_path:
            return os.path.basename(relative_path)

    # Add .exe extension if running on Windows
    if sys.platform == "win32" and ('exiftool' in relative_path or 'ffmpeg' in relative_path):
        relative_path += '.exe'

    # For macOS and Linux, ensure 'exiftool' is in a subdirectory
    elif 'exiftool' in relative_path and sys.platform != "win32":
        relative_path = os.path.join('exiftool', relative_path)

    full_path = os.path.join(base_path, relative_path)

    if 'exiftool' in relative_path:
        st = os.stat(full_path)
        os.chmod(full_path, st.st_mode | stat.S_IEXEC)

    return full_path

class Worker(QThread):
    progressChanged = pyqtSignal(int)
    finished = pyqtSignal()  

    def __init__(self, files, output_folder_path, hwaccel_method, remove_audio): 
        super().__init__()
        self.files = files
        self.output_folder_path = output_folder_path
        self.hwaccel_method = hwaccel_method
        self.remove_audio = remove_audio

    def run(self):
        self.process_videos(self.files, self.set_progress)
        self.finished.emit()

    def get_metadata_timestamp(self, file_path):
        exiftool_path = get_resource_path('exiftool')
        result = subprocess.run([exiftool_path, '-DateTimeOriginal', file_path], capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0))
        if result.stderr:
            print("Error:", result.stderr)
        if result.stdout:
            print("Output:", result.stdout)
        timestamp = result.stdout.strip()
        return timestamp

    def to_unix_timestamp(self, date_str):
        date_str = date_str.split(': ', 1)[-1]  # Remove the 'Date/Time Original              :' part
        dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S%z')
        return int(dt.timestamp())    

    def burn_timestamp(self, file_path, start_time_unix, output_file):
        if os.path.exists(output_file):
            return

        ffmpeg_path = get_resource_path("ffmpeg")
        command = (
            f'{ffmpeg_path} -hide_banner -i "{file_path}" -vf '
            f'"drawtext='
            f'text=\'%{{pts\\:localtime\\:{start_time_unix}\\:%X}}\': x=10: y=h-th-85: fontsize=48: fontcolor=white: shadowcolor=black: shadowx=2: shadowy=2, '
            f'drawtext='
            f'text=\'%{{pts\\:localtime\\:{start_time_unix}\\:%m-%d-%Y}}\': x=10: y=h-th-40: fontsize=48: fontcolor=white: shadowcolor=black: shadowx=2: shadowy=2'
        )
        command += f'" -c:v {self.hwaccel_method} -b:v 5000k'
        if self.remove_audio:
            command += ' -an'
        command += f' "{output_file}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0))
        if result.stderr:
            print("Error:", result.stderr)
        if result.stdout:
            print("Output:", result.stdout)

    def process_videos(self, files, set_progress):
        set_progress(0)

        increment = 100 / len(files) if files else 0

        progress = 0

        for file_path in files:
            creation_date = self.get_metadata_timestamp(file_path)
            if creation_date:
                creation_date = creation_date.split(': ', 1)[-1]  # Remove the 'Date/Time Original              :' part
                start_time_unix = self.to_unix_timestamp(creation_date)
                output_file_name = datetime.datetime.strptime(creation_date.split()[0], '%Y:%m:%d').strftime('%m-%d-%Y') + '_' + creation_date.split()[1].split('-')[0].replace(':', '-') + ".mp4"
                output_file = os.path.join(self.output_folder_path, output_file_name)
                self.burn_timestamp(file_path, start_time_unix, output_file)

            progress += increment
            set_progress(int(progress))

    def set_progress(self, value):
        self.progressChanged.emit(value)