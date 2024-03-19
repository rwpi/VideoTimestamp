import os
import subprocess
import sys
import stat
import datetime
import re
from PyQt5.QtCore import QThread

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

def get_metadata(file_path):
    '''Extracts the CreateDate and Duration from the file's metadata.'''
    exiftool_path = get_resource_path('exiftool')

    create_date_command = [exiftool_path, '-CreateDate', '-s', '-s', '-s', file_path]
    duration_command = [exiftool_path, '-Duration', '-s', '-s', '-s', file_path]

    create_date_result = subprocess.run(create_date_command, capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0))
    
    duration_result = subprocess.run(duration_command, capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0))

    if create_date_result.returncode != 0 or duration_result.returncode != 0:
        print(f"Error reading metadata for {file_path}")
        return None, None

    return create_date_result.stdout.strip(), duration_result.stdout.strip()

def calculate_new_timestamp(create_date, duration):
    '''Calculates a new timestamp by subtracting the duration from the create date.'''
    create_date_dt = datetime.datetime.strptime(create_date, "%Y:%m:%d %H:%M:%S")

    # Check if duration is in the format of decimal seconds
    if " s" in duration:
        duration_seconds = float(duration.replace(" s", ""))
    else:
        # Assuming the duration is in the format "H:MM:SS"
        hours, minutes, seconds = map(int, duration.split(":"))
        duration_seconds = hours * 3600 + minutes * 60 + seconds

    duration_td = datetime.timedelta(seconds=duration_seconds)
    new_timestamp = create_date_dt - duration_td
    return new_timestamp.strftime("%m-%d-%Y_%H-%M-%S")

def get_video_duration(file_path):
    ffmpeg_path = get_resource_path("ffmpeg")
    if sys.platform == "win32":
        command = f'{ffmpeg_path} -i "{file_path}" 2>&1 | find "Duration"'
    else:
        command = f'{ffmpeg_path} -i "{file_path}" 2>&1 | grep "Duration"'
    #result = subprocess.run(command, shell=True, capture_output=True, text=True)
    result = subprocess.run(command, shell=True, capture_output=True, text=True, creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0))
    start = result.stdout.index("Duration: ")
    duration = result.stdout[start+10:start+21]
    h, m, s = duration.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def cliporder_rename(directory):
    # Regex pattern to match date and time in filename
    pattern = re.compile(r"(\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2})")

    # List to store tuples of (datetime, filename)
    files = []

    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if match:
            dt = datetime.datetime.strptime(match.group(1), "%m-%d-%Y_%H-%M-%S")
            files.append((dt, filename))

    # Sort files by datetime
    files.sort()

    # Rename files
    for i, (_, filename) in enumerate(files, start=1):
        base, ext = os.path.splitext(filename)
        new_filename = f"CLIP{i}_{base}{ext}"
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))

class MagicRenamerThread(QThread):
    def __init__(self, output_folder_path, parent=None):
        super().__init__(parent)
        self.directory = output_folder_path
    def run(self):
        process_files(self.directory)

def process_files(directory):
    '''Renames .MOV files based on their CreateDate minus Duration, marks short .mp4 files and long .mp4 files, and then reorders all files.'''
    
    if not directory:
        return

    # List to store tuples of (new_name, old_name)
    files = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.lower().endswith(".mov"):
            create_date, duration = get_metadata(file_path)
            if create_date and duration:
                new_name = calculate_new_timestamp(create_date, duration) + '_COVERT.MOV'
                files.append((new_name, filename))
        elif filename.lower().endswith(".mp4"):
            duration = get_video_duration(file_path)
            base, ext = os.path.splitext(filename)  # Get the filename without extension
            # Remove existing clip number and tags from base name
            base = re.sub(r'^CLIP\d+_', '', base)
            base = re.sub(r'_INTEGRITY$', '', base)
            base = re.sub(r'_CLAIMANT$', '', base)
            if duration < 20:
                new_name = base + "_INTEGRITY" + ext
                files.append((new_name, filename))
            elif duration >= 20:
                new_name = base + "_CLAIMANT" + ext
                files.append((new_name, filename))

    # Sort files by new name
    files.sort()

    # Rename files
    for new_name, old_name in files:
        os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))

    # Add clip order to file name
    cliporder_rename(directory)