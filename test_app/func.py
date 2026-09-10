import sys
import time
from collections import namedtuple
import psutil
from rich import box
from rich.table import Table
from rich.text import Text
from usage_bar import usage_details

# Module-level private caches for non-blocking I/O calculation
_disk_cache = {}
_net_cache = {}


def cpu_table_1():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)

    cpu_usage = psutil.cpu_percent(interval=None, percpu=False)

    # Handle environments where cpu_freq() returns None (VMs, Docker, WSL)
    freq_data = psutil.cpu_freq(percpu=False)
    cpu_freq_str = f"{freq_data.current / 1000:.2f}GHz" if freq_data else "-N/A-"

    cpu_temp = "-N/A-"
    cpu_core_temp = {}

    # Multi-platform temperature inspection (Intel, AMD, ARM)
    if psutil.LINUX:
        try:
            temps = psutil.sensors_temperatures(fahrenheit=False)
            sensor_keys = ["coretemp", "k10temp", "cpu_thermal"]
            found_key = next((k for k in sensor_keys if k in temps), None)

            if found_key and temps[found_key]:
                # Safe first-entry lookup
                cpu_temp = f"{temps[found_key][0].current:.1f}°C"

                for entry in temps[found_key]:
                    if "Core" in entry.label:
                        clean_no = entry.label.replace("Core", "").strip()
                        try:
                            cpu_core_temp[int(clean_no)] = entry.current
                        except ValueError:
                            pass
        except Exception:
            pass

    cpu_core_usage = psutil.cpu_percent(interval=None, percpu=True)

    table.add_column("CPU")
    table.add_column("Usage")
    table.add_column("Temp")

    table.add_row(f"Main {cpu_freq_str}", usage_details(cpu_usage, "cpu"), f"{cpu_temp}")

    for i, core_usage in enumerate(cpu_core_usage):
        temp_val = cpu_core_temp.get(i)
        cpu_core_temp_n = f"{temp_val:.1f}°C" if temp_val is not None else "-N/A-"
        table.add_row(
            f"⚙️ Core {i}", usage_details(core_usage, "cpu"), f"{cpu_core_temp_n}"
        )

    return table


def cpu_table_2():
    table = Table(show_header=True, box=None, padding=(0, 1))
    table.add_column("Core count")
    table.add_column()
    table.add_row(
        f"Physical : {psutil.cpu_count(logical=False)}",
        f"Logical : {psutil.cpu_count(logical=True)}",
    )
    return table


def ram_table():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)
    table.add_column("RAM")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    ram_v_data = psutil.virtual_memory()
    used1 = f"{ram_v_data.used / (1024**3):.2f}GB"
    free1 = f"{ram_v_data.free / (1024**3):.2f}GB"
    total1 = f"{ram_v_data.total / (1024**3):.2f}GB"

    ram_s_data = psutil.swap_memory()
    used2 = f"{ram_s_data.used / (1024**3):.2f}GB"
    free2 = f"{ram_s_data.free / (1024**3):.2f}GB"
    total2 = f"{ram_s_data.total / (1024**3):.2f}GB"

    table.add_row("📀 Virtual", usage_details(ram_v_data.percent, "ram"), used1, free1, total1)
    table.add_row("💿 Swap", usage_details(ram_s_data.percent, "ram"), used2, free2, total2)
    return table


def disk_table_1():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)
    table.add_column("DISK")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    try:
        drive_data_list = psutil.disk_partitions(all=False)
    except Exception:
        drive_data_list = []

    for drive_data in drive_data_list:
        try:
            disk_data = psutil.disk_usage(drive_data.mountpoint)
            used = f"{disk_data.used / (1024**3):.2f}GB"
            free = f"{disk_data.free / (1024**3):.2f}GB"
            total = f"{disk_data.total / (1024**3):.2f}GB"
            table.add_row(f"{drive_data.device}")
            table.add_row(
                f"💾 [{drive_data.fstype}]",
                usage_details(disk_data.percent, "disk"),
                used,
                free,
                total,
            )
        except (PermissionError, OSError):
            continue

    return table


def disk_table_2():
    table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
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
    data = psutil.disk_io_counters(perdisk=True, nowrap=True) or {}
    d_details = []
    current_time = time.monotonic()
    Info = namedtuple("Info", ["drive", "read", "write", "count_r", "count_w"])

    for drive, values in data.items():
        read_bytes = values.read_bytes
        write_bytes = values.write_bytes
        r_count = values.read_count
        w_count = values.write_count

        if drive in _disk_cache:
            old_time, old_read, old_write = _disk_cache[drive]
            elapsed = current_time - old_time
            if elapsed > 0:
                read = ((read_bytes - old_read) / (1024**2)) / elapsed
                write = ((write_bytes - old_write) / (1024**2)) / elapsed
            else:
                read, write = 0.0, 0.0
        else:
            read, write = 0.0, 0.0

        _disk_cache[drive] = (current_time, read_bytes, write_bytes)
        d_details.append(Info(drive, read, write, r_count, w_count))

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
        dev = d_detail.device.lower()
        if any(x in dev for x in ("wi-fi", "wlp", "wlan", "wireless")):
            emoji = "🛜"
        elif any(x in dev for x in ("ethernet", "eth", "enp", "en1", "lan")):
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
    data = psutil.net_io_counters(pernic=True, nowrap=True) or {}
    d_details = []
    current_time = time.monotonic()

    for device, values in data.items():
        sent_bytes = values.bytes_sent
        recv_bytes = values.bytes_recv

        if sent_bytes == 0 and recv_bytes == 0:
            continue

        if device in _net_cache:
            old_time, old_sent, old_recv = _net_cache[device]
            elapsed = current_time - old_time
            if elapsed > 0:
                upload = ((sent_bytes - old_sent) / (1024**2)) / elapsed
                download = ((recv_bytes - old_recv) / (1024**2)) / elapsed
            else:
                upload, download = 0.0, 0.0
        else:
            upload, download = 0.0, 0.0

        _net_cache[device] = (current_time, sent_bytes, recv_bytes)
        d_details.append(
            Info(
                device,
                upload,
                download,
                sent_bytes / (1024**2),
                recv_bytes / (1024**2),
            )
        )

    return d_details


def bat_table():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)
    table.add_column("Battery")

    try:
        battery = psutil.sensors_battery()
    except Exception:
        battery = None

    if battery:
        b_percent = battery.percent
        if battery.power_plugged:
            status = "plugged in"
            time_left = "--N/A--"
        else:
            status = "not plugged in"
            if battery.secsleft not in (
                None,
                psutil.POWER_TIME_UNKNOWN,
                psutil.POWER_TIME_UNLIMITED,
            ) and battery.secsleft > 0:
                hrs = battery.secsleft // 3600
                mins = (battery.secsleft % 3600) // 60
                time_left = f"{hrs}h {mins}m"
            else:
                time_left = "--N/A--"

        battery_info = f"🔋 Percentage : {b_percent}%   Status : {status}   Time left : {time_left}"
    else:
        battery_info = "🔋 -------------N/A-------------"

    table.add_row(battery_info)
    return table


def fan_table():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)
    table.add_column("Manufacturer")
    table.add_column("Type")
    table.add_column("Speed")

    has_fans = False
    if psutil.LINUX:
        try:
            fan_data = psutil.sensors_fans()
            for mf, fan_list in fan_data.items():
                for fan_d in fan_list:
                    has_fans = True
                    table.add_row(f"❄️ {mf}", f"{fan_d.label}", f"{fan_d.current}RPM")
        except Exception:
            pass

    if not has_fans:
        table.add_row("❄️ -N/A-", "-N/A-", "-N/A-")

    return table


def get_process_data():
    no = 1
    for p in psutil.process_iter(
        ["name", "pid", "ppid", "status", "username", "cpu_percent", "memory_percent"]
    ):
        try:
            proc = p.info
            if proc.get("username") is not None:
                cpu = proc.get("cpu_percent") or 0.0
                mem = proc.get("memory_percent") or 0.0
                yield (
                    str(no),
                    str(proc.get("name") or "-"),
                    str(proc.get("pid") or "-"),
                    str(proc.get("ppid") or "-"),
                    str(proc.get("status") or "-"),
                    str(proc.get("username") or "-"),
                    f"{cpu:.2f}",
                    f"{mem:.2f}",
                )
                no += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


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
    return Text(ascii_art, no_wrap=True)