from rich.console import Console, Group
from rich.table import Table
from rich.progress import (
    Progress,
    BarColumn,
    TaskProgressColumn,
)
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich import box
import psutil
import time
from collections import namedtuple
from pynput import keyboard
import sys
from usage_bar import usage_details


def cpu_table_1():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)

    cpu_usage = psutil.cpu_percent(interval=None, percpu=False)
    cpu_freq = (psutil.cpu_freq(percpu=False).current) / 1000

    cpu_temp = "-N/A-"
    cpu_core_temp = {}
    if psutil.LINUX:
        temps = psutil.sensors_temperatures(fahrenheit=False)
        if "coretemp" in temps:
            if "Physical id 0" in temps["coretemp"][0].label:
                cpu_temp = f"{entry.current}°C"

                for entry in temps["coretemp"][1:]:
                    if "Core" in entry.label:
                        core_no = entry.label.replace("Core", "")
                        cpu_core_temp[core_no] = entry.current

    cpu_core_usage = psutil.cpu_percent(interval=None, percpu=True)

    table.add_column("CPU")
    table.add_column("Usage")
    table.add_column("Temp")

    table.add_row(
        f"Main {cpu_freq:.2f}GHz", usage_details(cpu_usage, "cpu"), f"{cpu_temp}"
    )
    for i, core_usage in enumerate(cpu_core_usage):
        try:
            cpu_core_temp_n = f"{cpu_core_temp[i]}°C"
        except KeyError:
            cpu_core_temp_n = "-N/A-"
        table.add_row(
            f"⚙️ Core {i}", usage_details(core_usage, "cpu"), f"{cpu_core_temp_n}"
        )

    return table


def cpu_table_2():
    table = Table(show_header=True, box=None, padding=(0, 1))

    table.add_column(f"Core count")
    table.add_column()
    table.add_row(
        f"Physical : {psutil.cpu_count(logical=False)}",
        f"Logical : {psutil.cpu_count(logical=True)}",
    )
    return table


def ram_table():

    table = Table(show_header=True, box=None, padding=(0, 1),expand=True)

    table.add_column("RAM")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    ram_v_data = psutil.virtual_memory()
    ram_v_usage = ram_v_data.percent
    used1 = f"{ram_v_data.used/(1024**3):.2f}GB"
    free1 = f"{ram_v_data.free/(1024**3):.2f}GB"
    total1 = f"{ram_v_data.total/(1024**3):.2f}GB"

    ram_s_data = psutil.swap_memory()
    ram_s_usage = ram_s_data.percent
    used2 = f"{ram_s_data.used/(1024**3):.2f}GB"
    free2 = f"{ram_s_data.free/(1024**3):.2f}GB"
    total2 = f"{ram_s_data.total/(1024**3):.2f}GB"

    table.add_row("📀 Virtual", usage_details(ram_v_usage, "ram"), used1, free1, total1)
    table.add_row("💿 Swap", usage_details(ram_s_usage, "ram"), used2, free2, total2)
    return table


def disk_table_1():
    table = Table(show_header=True, box=None, padding=(0, 1),expand=True)

    table.add_column("DISK")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    drive_data_list = psutil.disk_partitions(all=False)
    for drive_data in drive_data_list:
        disk_data = psutil.disk_usage(drive_data.mountpoint)
        disk_usage = disk_data.percent
        used = f"{disk_data.used/(1024**3):.2f}GB"
        free = f"{disk_data.free/(1024**3):.2f}GB"
        total = f"{disk_data.total/(1024**3):.2f}GB"
        table.add_row(f"{drive_data.device}")
        table.add_row(
            f"💾 [{drive_data.fstype}]",
            usage_details(disk_usage, "disk"),
            used,
            free,
            total,
        )

    return table


def disk_table_2():
    table = Table(show_header=False, box=None, padding=(0, 1),expand=True)
    table.add_column()
    table.add_column()
    table.add_column()

    d_details = disk_info_cal()
    for disk in d_details:
        table.add_row(
            f"💽 {disk.drive}",
            f"read: {disk.read:.2f}MB/s",
            f"write: {disk.write:.2f}MB/s",
        )
        table.add_row("", f"count: {disk.count_r}", f"count: {disk.count_w}")

    return table


def disk_info_cal():
    data = psutil.disk_io_counters(perdisk=True, nowrap=True)
    d_details = []
    Info = namedtuple("Info", ["drive", "read", "write", "count_r", "count_w"])
    for drive, details in data.items():
        old_drive_data = psutil.disk_io_counters(perdisk=True, nowrap=True)[drive]
        start = time.monotonic()
        old_r = old_drive_data.read_bytes / (1024**2)
        old_w = old_drive_data.write_bytes / (1024**2)

        time.sleep(0.1)

        new_drive_data = psutil.disk_io_counters(perdisk=True, nowrap=True)[drive]
        end = time.monotonic()
        new_r = new_drive_data.read_bytes / (1024**2)
        new_w = new_drive_data.write_bytes / (1024**2)

        r_count = new_drive_data.read_count
        w_count = new_drive_data.write_count

        read = (new_r - old_r) / (end - start)
        write = (new_w - old_w) / (end - start)
        info = Info(drive, read, write, r_count, w_count)
        d_details.append(info)

    return d_details


def network_table():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)
    table.add_column("NET")
    table.add_column("Upload")
    table.add_column("Download")
    table.add_column("Sent")
    table.add_column("Recieved")

    d_details = net_info_cal()
    for d_detail in d_details:
        if "Wi-Fi" or "wlp" or "wlan" in d_detail.device:
            emoji = "🛜"
        elif "Ethernet" or "eth" or "enp" or "en1" in d_detail.device:
            emoji = "🔌"
        else:
            emoji = "🌐"
        table.add_row(
            f"{emoji} {d_detail.device}",
            f"{d_detail.upload:.2f}MB/s",
            f"{d_detail.download:.2f}MB/s",
            f"{d_detail.sent:.2f}MB",
            f"{d_detail.recv:.2f}MB",
        )

    return table


def net_info_cal():
    Info = namedtuple("Info", ["device", "upload", "download", "sent", "recv"])
    data = psutil.net_io_counters(pernic=True, nowrap=True)

    devices = []
    d_details = []

    for device, values in data.items():
        sent = values.bytes_sent
        recv = values.bytes_recv
        if not (sent == 0 and recv == 0):
            devices.append(device)

    for device in devices:
        data = psutil.net_io_counters(pernic=True, nowrap=True)
        start = time.monotonic()

        old_s = data[device].bytes_sent / (1024**2)
        old_r = data[device].bytes_recv / (1024**2)

        time.sleep(0.1)

        data = psutil.net_io_counters(pernic=True, nowrap=True)
        end = time.monotonic()

        new_s = data[device].bytes_sent / (1024**2)
        new_r = data[device].bytes_recv / (1024**2)

        upload = (new_s - old_s) / (end - start)
        download = (new_r - old_r) / (end - start)

        info = Info(device, upload, download, new_s, new_r)
        d_details.append(info)

    return d_details


def bat_table():
    table = Table(show_header=True, box=None, padding=(0, 1),expand=True)
    table.add_column("Battery")

    battry_details = psutil.sensors_battery()
    if battry_details:
        b_percent = battry_details.percent
        b_plugged = battry_details.power_plugged
        if b_plugged:
            time_left = "--N/A--"
            status = "plugged in"
        else:
            time_left = battry_details.secsleft
            hrs = time_left // (60 * 60)
            miniut = (time_left % (60 * 60)) // 60
            time_left = f"{hrs}h {miniut}m"
            status = "not plugged in"
        battery_info = f"🔋 Percentage : {b_percent}%   Status : {status}   Time left : {time_left}"
    else:
        battery_info = f"🔋 -------------N/A-------------"

    table.add_row(battery_info)
    return table


def fan_table():
    table = Table(show_header=True, box=None, padding=(0, 1),expand=True)
    table.add_column("Manufacturer")
    table.add_column("Type")
    table.add_column("Speed")

    if psutil.LINUX:
        fan_data = psutil.sensors_fans()
        for mf, fan_d in fan_data.items():
            table.add_row(f"❄️ {mf}", f"{fan_d.label}", f"{fan_d.current}RPM")
    else:
        table.add_row("❄️ -N/A-", "-N/A-", "-N/A-")

    return table


def process_table_1():
    table = Table(
        show_header=True,
        box=box.MARKDOWN,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Name")
    table.add_column("PID")
    table.add_column("PPID")
    table.add_column("Status")
    table.add_column("User Name")
    table.add_column("CPU")
    table.add_column("RAM")
    table.add_column("Location")
    for p in psutil.process_iter(
        [
            "name",
            "pid",
            "ppid",
            "status",
            "username",
            "cpu_percent",
            "memory_percent",
            "exe",
        ]
    ):
        proc = p.info
        if proc.get("exe"):
            exe_text = proc.get("exe")
        else:
            exe_text = Text("-N/A-")

        table.add_row(
            f"{proc.get("name")}",
            f"{proc.get("pid")}",
            f"{proc.get("ppid")}",
            f"{proc.get("status")}",
            f"{proc.get("username")}",
            f"{proc.get("cpu_percent"):.2f}",
            f"{proc.get("memory_percent"):.2f}",
            f"{exe_text}",
        )
    table.add_row()

    return table


def process_table_2():
    table = Table(show_header=True, box=box.MARKDOWN, padding=(0, 1), expand=True)
    table.add_column("No.")
    table.add_column("Name")
    table.add_column("PID")
    table.add_column("PPID")
    table.add_column("Status")
    table.add_column("User Name")
    table.add_column("CPU")
    table.add_column("RAM")
    for data in get_process_data():
        table.add_row(*data)
    return table


def get_process_data():
    no = 1
    for i, p in enumerate(
        psutil.process_iter(
            [
                "name",
                "pid",
                "ppid",
                "status",
                "username",
                "cpu_percent",
                "memory_percent",
                #"exe",
            ]
        )
    ):
        proc = p.info
        if proc["username"] != None:
            data = (
                f"{no}",
                f"{proc["name"]}",
                f"{proc["pid"]}",
                f"{proc["ppid"]}",
                f"{proc["status"]}",
                f"{proc["username"]}",
                f"{proc["cpu_percent"]:.2f}",
                f"{proc["memory_percent"]:.2f}",
                #f"{proc.get("exe")}",
            )
            no += 1
        yield data


def program_name():
    ascii_art = r"""
 .oooooo..o                        .oooooo.                                
d8P'    `Y8                       d8P'  `Y8b                               
Y88bo.      oooo    ooo  .oooo.o 888           .ooooo.  oooo d8b  .ooooo.  
 `"Y8888o.   `88.  .8'  d88(  "8 888          d88' `88b `888""8P d88' `88b 
     `"Y88b   `88..8'   `"Y88b.  888          888   888  888     888ooo888 
oo     .d8P    `888'    o.  )88b `88b    ooo  888   888  888     888    .o 
8""88888P'      .8'     8""888P'  `Y8bood8P'  `Y8bod8P' d888b    `Y8bod8P' 
            .o..P'                                                        
            `Y8P'                                               
    """
    text = Text(ascii_art, no_wrap=True)

    return text


def table_updator():

    while run_time:
        waiting = Text("Loading.....")
        with Live(waiting, refresh_per_second=10, screen=True) as live:
            while main_scr:
                title = program_name()
                table1 = cpu_table_1()
                table2 = cpu_table_2()
                table3 = ram_table()
                table4 = disk_table_1()
                table5 = disk_table_2()
                table6 = network_table()
                table7 = bat_table()
                table8 = fan_table()
                footer = Text(
                    "[ Esc ] : Quit the programe   |   [ -→ ] : Processes Screen"
                )
                content = Group(
                    title,
                    Columns(
                        [
                            Group(table1, table2),
                            Group(table3, table4, table5, table6, table7, table8),
                        ]
                    ),
                    footer,
                )

                live.update(content)
                time.sleep(0.9)

        with Live(waiting, refresh_per_second=15, screen=True) as live:
            while pro_scr:
                global scroll
                console = Console()
                height = console.height
                footer = Text(
                    "[ Esc ] : Quit the programe   |   [ ←- ] : Main Screen   |   [ ↑ ] : Scroll up   |   [ ↓ ] : Scroll down"
                )
                content = Group(process_table_2(scroll, height - 5), footer)
                live.update(content)
                time.sleep(0.5)


def on_press(key):
    global scroll
    global main_scr
    global pro_scr
    global run_time
    try:
        if key == keyboard.Key.up and scroll > 0:
            scroll -= 1
        elif key == keyboard.Key.down:
            scroll += 1
        elif key == keyboard.Key.left:
            main_scr = True
            pro_scr = False
        elif key == keyboard.Key.right:
            main_scr = False
            pro_scr = True
        elif key == keyboard.Key.esc:
            run_time = False
            main_scr = False
            pro_scr = False
    except AttributeError:
        pass


scroll = 0
main_scr = True
pro_scr = False
run_time = True


def main():
    arg = sys.argv[1:]
    if len(arg) == 1:
        if arg[0] == "--p_log":
            console = Console()
            console.print(program_name())
            console.print(process_table_1())
        else:
            sys.exit("Wrong Comand.....")
    elif len(arg) == 0:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        table_updator()
    else:
        sys.exit("Wrong Comand.....")


if __name__ == "__main__":
    main()
