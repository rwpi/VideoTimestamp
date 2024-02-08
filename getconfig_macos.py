import subprocess

def check_nvidia_gpu():
    try:
        gpu_info = subprocess.check_output("system_profiler SPDisplaysDataType", shell=True).decode().strip().split('\n')
        for line in gpu_info:
            if 'NVIDIA' in line:
                return True
        return False
    except Exception:
        return False

def check_amd_gpu():
    try:
        gpu_info = subprocess.check_output("system_profiler SPDisplaysDataType", shell=True).decode().strip().split('\n')
        for line in gpu_info:
            if 'AMD' in line:
                return True
        return False
    except Exception:
        return False

def get_config():
    nvidia_gpu_present = check_nvidia_gpu()
    amd_gpu_present = check_amd_gpu()
    return {"nvidia_gpu_present": nvidia_gpu_present, "amd_gpu_present": amd_gpu_present}