# Private Investigator Video Timestamp (VTS)

![Screenshot of the application](https://github.com/rwpi/videotimestamp/blob/4d821b04586958bb583926b48f50803fe98709d1/media/Screenshot_1_0_0.png)

## Overview
Private Investigator Video Timestamp (VTS) is a cross-platform Python-based application that adds timestamp overlays to camcorder video files. It leverages the metadata within a file to extract date and time information, which is then overlaid onto the video files.

Currently, VTS supports AVCHD (.MTS) video files from Sony and Panasonic camcorders. If your camera or video file format is not supported, please file an issue on GitHub with the camera make/model and a small sample video file. We are continually expanding our support and your contribution will help us improve.

VTS is currently optimized for MacOS computers with builds for M1 and Intel available. We are actively working on expanding compatibility to include Windows and Linux systems in the near future. An experimental Windows build is now available.

## Installation
To install VTS, download the appropriate installer from the [Latest Release](https://github.com/rwpi/videotimestamp/releases/latest) section.

## Usage
The application provides four options for users to configure before initiating the timestamping process:

1. **Choose Input Files**
    - Select the video files to be timestamped.
    - The selected files will be added to a list.
    - To add more files, simply click the button again.
    - If a mistake is made while creating the list, click 'reset' to start over.

2. **Choose Output Folder**
    - Specify the destination for the new timestamped files.
    - You can select an existing folder or create a new one.
    - Upon completion, the timestamped files will be located in the chosen folder.

3. **Choose Video Encoder**
    - Select the video card used by your computer.
    - By default, the application uses software encoding (libx264), which is much slower than using your video card.
    - For most recent Windows laptops with Intel Processors, "Intel QSV" is the recommended choice.
    - For most recent Windows laptops with AMD Processors, "AMD AMF" is the recommended choice.
    - For most MacOS computers, "MacOS Videotoolbox" is the recommended choice.
    - Options for other graphics cards are available for desktop workstations with dedicated graphics cards.

4. **Remove Audio**
    - If you prefer to have the audio removed from your timestamped video file, ensure this box is checked.

5. **Timestamp Video**
    - After configuring the above options, click the "Timestamp Video" button to start the process.
    - A progress bar will appear and fill up as the video is processed.
    - Once the progress bar is fully filled, your timestamped video is ready for viewing in the specified output folder.
