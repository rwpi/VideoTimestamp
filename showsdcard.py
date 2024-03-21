import os
import subprocess
import glob

def show_sd_card():
    # Check the operating system
    if os.name == 'nt':  # Windows
        # Iterate over drive letters
        for drive_letter in range(ord('C'), ord('Z')+1):
            drive = chr(drive_letter)
            # Construct the path
            path = f'{drive}:\\private\\AVCHD\\BDMV\\STREAM\\'
            # Check if the path exists
            if os.path.exists(path):
                # Open the folder in Windows Explorer
                subprocess.run(['explorer', path])
    else:  # macOS
        # Get a list of all mounted volumes
        volumes = glob.glob('/Volumes/*/')
        for volume in volumes:
            # Construct the path
            path = os.path.join(volume, 'private/AVCHD/BDMV/STREAM/')
            # Check if the path exists
            if os.path.exists(path):
                # Open the Finder at the path
                subprocess.run(["open", path])
