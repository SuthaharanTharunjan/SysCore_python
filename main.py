from rich.console import Console, Group
from rich.table import Table
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    ProgressColumn,
)
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
import psutil
import platform
import time
from collections import namedtuple

class FrequencyColumn(ProgressColumn):
    def render(self, task):
        return Text(f"[{task.fields['freq']:.2f} GHz]")


def usage_details(usage, name=None):
    progress = Progress(
        BarColumn(bar_width=10,finished_style="red"),
        TaskProgressColumn()
    )
    if name == "cpu":
        progress.add_task("",total=100, completed=usage)
    else:
        progress.add_task("",total=100, completed=usage)

    return progress


def cpu_table():
    table = Table(show_header=True, box=None)

    cpu_usage = psutil.cpu_percent(interval=None, percpu=False)
    cpu_freq = (psutil.cpu_freq(percpu=False).current) / 1000

    cpu_core_usage = psutil.cpu_percent(interval=None, percpu=True)

    table.add_column()
    table.add_column("Usage")
    table.add_row(f"CPU {cpu_freq:.2f}GHz",usage_details(cpu_usage, "cpu"))
    for i, core_usage in enumerate(cpu_core_usage):
        table.add_row(f"⚙️ Core {i}", usage_details(core_usage, "cpu"))
    return table


def cpu_table_2():
    table=Table(show_header=True, box=None)

    table.add_column(f"Number of CPU Cores ")
    table.add_column()
    table.add_row(f"Physical : {psutil.cpu_count(logical=False)}",f"Logical : {psutil.cpu_count(logical=True)}")
    
    return table


def ram_table():

    table = Table(show_header=True, box=None)

    table.add_column("RAM")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    ram_v_data=psutil.virtual_memory()
    ram_v_usage = ram_v_data.percent
    used1 = f"{ram_v_data.used/(1024**3):.2f}GB"
    free1 = f"{ram_v_data.free/(1024**3):.2f}GB"
    total1 = f"{ram_v_data.total/(1024**3):.2f}GB"

    ram_s_data=psutil.swap_memory()
    ram_s_usage = ram_s_data.percent
    used2 = f"{ram_s_data.used/(1024**3):.2f}GB"
    free2 = f"{ram_s_data.free/(1024**3):.2f}GB"
    total2 = f"{ram_s_data.total/(1024**3):.2f}GB"

    
    table.add_row("📀 Virtual", usage_details(ram_v_usage, "ram"), used1, free1, total1)
    table.add_row("💿 Swap", usage_details(ram_s_usage, "ram"), used2, free2, total2)

    return table


def disk_table_1():
    table = Table(show_header=True, box=None)

    table.add_column("DISK")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    drive_data_list=psutil.disk_partitions(all=False)
    for drive_data in drive_data_list:
        disk_data=psutil.disk_usage(drive_data.mountpoint)
        disk_usage=disk_data.percent
        used=f"{disk_data.used/(1024**3):.2f}GB"
        free=f"{disk_data.free/(1024**3):.2f}GB"
        total=f"{disk_data.total/(1024**3):.2f}GB"
        table.add_row(f"{drive_data.device}")
        table.add_row(f"💾 [{drive_data.fstype}]",usage_details(disk_usage, "disk"),used,free,total)

    return table


def disk_table_2():
    table= Table(show_header=False, box=None)
    table.add_column()
    table.add_column()
    table.add_column()

    d_details=disk_info_calc()
    for disk in d_details:
        table.add_row(f"💽 {disk.drive}",f"read: {disk.read:.2f}MB/s",f"write: {disk.write:.2f}MB/s")
        table.add_row("",f"count: {disk.count_r}",f"count: {disk.count_w}")
    return table

def disk_info_calc():
    data=psutil.disk_io_counters(perdisk=True, nowrap=True)
    d_details=[]
    Info = namedtuple("Info", ["drive", "read", "write", "count_r", "count_w"])
    for drive,details in data.items():
        old_drive_data=psutil.disk_io_counters(perdisk=True, nowrap=True)[drive]
        start=time.monotonic()
        old_r=old_drive_data.read_bytes/(1024**2)
        old_w=old_drive_data.write_bytes/(1024**2)

        time.sleep(0.1)

        new_drive_data=psutil.disk_io_counters(perdisk=True, nowrap=True)[drive]
        end=time.monotonic()
        new_r=new_drive_data.read_bytes/(1024**2)
        new_w=new_drive_data.write_bytes/(1024**2)

        r_count=new_drive_data.read_count
        w_count=new_drive_data.write_count

        read=(new_r-old_r)/(end-start)
        write=(new_w-old_w)/(end-start)
        info= Info(drive,read,write,r_count,w_count)
        d_details.append(info)
    return d_details


def network_table():
    table = Table(show_header=True, box=None)
    table.add_column("NET")
    table.add_column("Upload")
    table.add_column("Download")
    table.add_column("Sent")
    table.add_column("Recieved")

    d_details=net_info_cal()
    for d_detail in d_details:
        if "Wi-Fi" or "wlp" or "wlan" in d_detail.device :
            emoji="🛜"
        elif "Ethernet" or "eth" or "enp" or "en1" in d_detail.device :
            emoji="🔌"
        else:
            emoji="🌐"
        table.add_row(f"{emoji} {d_detail.device}",f"{d_detail.upload:.2f}MB/s",f"{d_detail.download:.2f}MB/s",f"{d_detail.sent:.2f}MB",f"{d_detail.recv:.2f}MB") 

    return table 


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

        old_s=data[device].bytes_sent/(1024**2)
        old_r=data[device].bytes_recv/(1024**2)

        time.sleep(0.1)

        data=psutil.net_io_counters(pernic=True, nowrap=True)
        end=time.monotonic()

        new_s=data[device].bytes_sent/(1024**2)
        new_r=data[device].bytes_recv/(1024**2)

        upload=(new_s-old_s)/(end-start)
        download=(new_r-old_r)/(end-start)

        info= Info(device,upload,download,new_s,new_r)
        d_details.append(info)

    return d_details

def bat_table():
    table = Table(show_header=True, box=None)
    table.add_column("Battery")

    battry_details=psutil.sensors_battery()
    if battry_details :
        b_percent=battry_details.percent
        b_plugged=battry_details.power_plugged
        if b_plugged :
            time_left="--N/A--"
            status= "plugged in"
        else:
            time_left=time_left=battry_details.secsleft/(60*60)
            time_left=round(time_left,2)
            status= "not plugged in"
        battery_info=f"🔋 Percentage : {b_percent}   Status : {status}   Time left : {time_left} hrs"
    else:
        battery_info=f"------"

    table.add_row(battery_info)

    return table


def process_table():
    table=Table(show_header=True, box=None)
    table.add_column("Name")
    table.add_column("PID")
    table.add_column("Status")
    table.add_column("User Name")
    table.add_column("CPU")
    table.add_column("RAM")
    for p in psutil.process_iter(["name","pid","status","username","cpu_percent","memory_percent"]):
        proc=p.info
        table.add_row(f"{proc.get("name")}",f"{proc.get("pid")}",f"{proc.get("status")}",f"{proc.get("username")}",f"{proc.get("cpu_percent"):.2f}",f"{proc.get("memory_percent")}")
    return table


def table_updator():
    with Live(refresh_per_second=10,screen=True) as live:
        while True:
            table1 = cpu_table()
            table2= cpu_table_2()
            table3 = ram_table()
            table4=disk_table_1()
            table5=disk_table_2()
            table6 = network_table()
            table7=bat_table()
            table8=process_table()
            col = Group(Columns([table1, Group(table2,table3,table4,table5,table6,table7)]),table8)
            live.update(col)

            time.sleep(1)


def main():
  
    table_updator()


if __name__ == "__main__":
    main()
