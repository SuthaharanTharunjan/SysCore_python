import psutil
import time
from collections import namedtuple
def net_info_cal():
    Info = namedtuple("Info", ["device", "upload", "download", "sent", "recv"])
    data=psutil.net_io_counters(pernic=True, nowrap=True)
    devices=[]
    d_details=[]
    for device,values in data.items():
        sent=values.bytes_sent
        recv=values.bytes_recv
        if not (sent==0 and recv==0):
            devices.append(device)
    for device in devices:
        data=psutil.net_io_counters(pernic=True, nowrap=True)
        start=time.monotonic()
        old_s=data[device].bytes_sent
        old_r=data[device].bytes_recv
        time.sleep(0.1)
        data=psutil.net_io_counters(pernic=True, nowrap=True)
        end=time.monotonic()
        new_s=data[device].bytes_sent
        new_r=data[device].bytes_recv

        upload=(new_s-old_s)/(end-start)
        download=(new_r-old_r)/(end-start)
        info= Info(device,upload,download,new_s,new_r)
        d_details.append(info)
    return d_details

def disk_info_calc():
    data=psutil.disk_io_counters(perdisk=True, nowrap=True)
    d_details=[]
    Info = namedtuple("Info", ["drive", "read", "write", "count_r", "count_w"])
    for drive,details in data.items():
        old_drive_data=psutil.disk_io_counters(perdisk=True, nowrap=True)[drive]
        start=time.monotonic()
        old_r=old_drive_data.read_bytes
        old_w=old_drive_data.write_bytes

        time.sleep(0.1)

        new_drive_data=psutil.disk_io_counters(perdisk=True, nowrap=True)[drive]
        end=time.monotonic()
        new_r=new_drive_data.read_bytes
        new_w=new_drive_data.write_bytes

        r_count=new_drive_data.read_count
        w_count=new_drive_data.write_count

        read=(new_r-old_r)/(end-start)
        write=(new_w-old_w)/(end-start)
        info= Info(drive,read,write,r_count,w_count)
        d_details.append(info)
    return d_details

battry_details=psutil.sensors_battery()
if battry_details :
    b_percent=battry_details.percent
    b_plugged=battry_details.power_plugged
    if b_plugged :
        time_left="-"
        status= "plugged in"
    else:
        time_left=time_left=battry_details.secsleft/(60*60)
        status= "not plugged in"
    battery_info=f"Percentage : {b_percent}   Status : {status}   Time left : {time_left}hrs"
else:
    battery_info=f"------"


#for proc in psutil.process_iter(['pid', 'name', 'username']):
    #print(proc.info)
print(
psutil.POSIX,
psutil.LINUX,
psutil.WINDOWS,
psutil.MACOS,
psutil.FREEBSD,
psutil.NETBSD,
psutil.OPENBSD,
psutil.BSD,
psutil.SUNOS,
psutil.AIX,
)
print(
psutil.STATUS_RUNNING,
psutil.STATUS_SLEEPING,
psutil.STATUS_DISK_SLEEP,
psutil.STATUS_STOPPED,
psutil.STATUS_TRACING_STOP,
psutil.STATUS_ZOMBIE,
psutil.STATUS_DEAD,
#psutil.STATUS_WAKE_KILL,
psutil.STATUS_WAKING,
)