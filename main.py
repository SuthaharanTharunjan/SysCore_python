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


def table_updator():
    with Live(refresh_per_second=1) as live:
        while True:
            table1 = cpu_table()
            table2 = ram_table()
            table3=disk_table()
            table4 = network_table()
            col = Columns([table1, Group(table2,table3,table4)])
            live.update(col)

            time.sleep(1)


def ram_table():

    table = Table(show_header=True, box=None)

    table.add_column("RAM")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    ram_v_data=psutil.virtual_memory()
    ram_v_usage = ram_v_data.percent
    used1 = f"{ram_v_data.used*1e-9:.2f}GB"
    free1 = f"{ram_v_data.free*1e-9:.2f}GB"
    total1 = f"{ram_v_data.total*1e-9:.2f}GB"

    ram_s_data=psutil.swap_memory()
    ram_s_usage = ram_s_data.percent
    used2 = f"{ram_s_data.used*1e-9:.2f}GB"
    free2 = f"{ram_s_data.free*1e-9:.2f}GB"
    total2 = f"{ram_s_data.total*1e-9:.2f}GB"

    
    table.add_row("📀 Virtual", usage_details(ram_v_usage, "ram"), used1, free1, total1)
    
    table.add_row("💿 Swap", usage_details(ram_s_usage, "ram"), used2, free2, total2)
    return table

def disk_table():
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
        used=f"{disk_data.used*1e-9:.2f}GB"
        free=f"{disk_data.free*1e-9:.2f}GB"
        total=f"{disk_data.total*1e-9:.2f}GB"
        table.add_row(f"{drive_data.device}")
        table.add_row(f"💾 [{drive_data.fstype}]",usage_details(disk_usage, "disk"),used,free,total)

    return table

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
        table.add_row(f"{emoji} {d_detail.device}",f"{d_detail.upload}MB/s",f"{d_detail.download}MB/s",f"{d_detail.sent}MB",f"{d_detail.recv}MB") 

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


def main():
    console = Console()
    table_updator()


if __name__ == "__main__":
    main()
