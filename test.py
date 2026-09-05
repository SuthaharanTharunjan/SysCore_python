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

