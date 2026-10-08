import psutil
import time
import os
import subprocess

def get_cpu_temp():

    result = subprocess.run(
        "sensors | grep Package",
        shell=True,
        capture_output=True,
        text=True
    )

def get_cpu_freq():
    cpu_frequency = psutil.cpu_freq()

    current = cpu_frequency.current
    minimum = cpu_frequency.min
    maximum = cpu_frequency.max

    return current, minimum, maximum

def get_cpu_load():
    cpu_load = psutil.cpu_percent()
    return cpu_load

def get_memory_info():
    meminfo = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":")
            meminfo[key.strip()] = int(value.split()[0])  # в KB

    total = meminfo["MemTotal"] // 1024
    available = meminfo["MemAvailable"] // 1024
    used = total - available

    return  total, available, used

def get_disk_info():
    path = '/'
    disk_space = psutil.disk_usage(path)
    bytes_total = disk_space.total
    bytes_available = disk_space.free
    bytes_used = disk_space.used
    disk_percent = disk_space.percent

    gigabytes_total = bytes_total / 1024 / 1024 / 1024
    gigabytes_available = bytes_available / 1024 / 1024 / 1024
    gigabytes_used = bytes_used / 1024 / 1024 / 1024

    #print(gigabytes_total, gigabytes_available, gigabytes_used, disk_percent)

    return gigabytes_available, gigabytes_available, gigabytes_used, disk_percent


def get_device_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])

            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            #uptime_str = f"{days} дн. {hours} ч. {minutes} мин."

            return f"{days} days | {hours} hours | {minutes} minutes"
    except FileNotFoundError:
        return None

def get_process_info():
    process = psutil.Process(os.getpid())
    ram_used = process.memory_info().rss / (1024 * 1024)  # in MB

    return ram_used

def get_tasks_info():
    processes = []

    for task in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            mem = task.info['memory_info'].rss / (1024 * 1024)  # MB
            processes.append((task.info['pid'], task.info['name'], mem))
        except:
            pass

    processes.sort(key=lambda x: x[2], reverse=True)

    return processes[:8]

io_old =  psutil.net_io_counters()
net_upload = 0
net_download = 0

def get_current_network():
    global io_old , net_upload, net_download

    io_new = psutil.net_io_counters()


    net_download = io_new.bytes_recv - io_old .bytes_recv
    net_upload = io_new.bytes_sent - io_old.bytes_sent

    io_old  = io_new

    #print(f"Download: {net_download / 1024:.2f} KB/s")
    #print(f"Upload:   {net_upload / 1024:.2f} KB/s")

    kb_download, kb_upload = net_download / 1024, net_upload / 1024

    return kb_download, kb_upload




#print(get_cpu_freq()) #min
#print(f"CPU Load: {get_cpu_load()}%")
#print(f"Procces memory: {int(get_process_info())} MB"  )
#pid,name,mem = get_tasks_info()
#print(get_tasks_info())
#print(get_memory_info())
