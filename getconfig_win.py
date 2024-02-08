import platform
import subprocess

def get_system_info():
    cpu_info = platform.processor()
    cpu_manufacturer = 'Unknown'
    if 'Intel' in cpu_info:
        cpu_manufacturer = 'Intel'
    elif 'AMD' in cpu_info:
        cpu_manufacturer = 'AMD'
    elif 'ARM' in cpu_info:
        cpu_manufacturer = 'ARM'

    return cpu_manufacturer

def check_nvidia_gpu():
    try:
        gpu_info = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode().strip().split('\n')
        for line in gpu_info:
            if 'NVIDIA' in line:
                return True
        return False
    except Exception:
        return False

def get_config():
    cpu = get_system_info()
    nvidia_gpu_present = check_nvidia_gpu()
    return {"cpu_manufacturer": cpu, "nvidia_gpu_present": nvidia_gpu_present}