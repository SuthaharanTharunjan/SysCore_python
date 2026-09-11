from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich import box
import psutil
import time
from collections import namedtuple
from usage_bar import usage_details

_disk_cache = {}
_net_cache = {}


def cpu_table_1():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)

    cpu_core_usage = psutil.cpu_percent(interval=None, percpu=True)
    cpu_usage = sum(cpu_core_usage) / len(cpu_core_usage) if cpu_core_usage else 0.0

    freq_data = psutil.cpu_freq(percpu=False)
    cpu_freq_str = f"{freq_data.current / 1000:.2f}GHz" if freq_data else "-N/A-"

    cpu_temp = "-N/A-"
    cpu_core_temp = {}

    if psutil.LINUX:
        try:
            temps = psutil.sensors_temperatures(fahrenheit=False)
            sensor_keys = ["coretemp", "k10temp", "cpu_thermal"]
            found_key = next((k for k in sensor_keys if k in temps), None)

            if found_key and temps[found_key]:
                entries = temps[found_key]
                package_temp = None
                core_temps_list = []

                for entry in entries:
                    label = entry.label.strip()

                    # 1. Match package-level readings (Intel & AMD)
                    if any(
                        tag in label
                        for tag in ("Package id 0", "Physical id 0", "Tctl", "Tdie")
                    ):
                        if package_temp is None:
                            package_temp = entry.current

                    # 2. Match individual cores (Intel & some AMD)
                    if "Core" in label:
                        core_no = label.replace("Core", "").strip()
                        try:
                            core_idx = int(core_no)
                            cpu_core_temp[core_idx] = entry.current
                            core_temps_list.append(entry.current)
                        except ValueError:
                            pass

                # 3. Resolve whole CPU temperature
                if package_temp is not None:
                    cpu_temp = f"{package_temp:.1f}°C"
                elif core_temps_list:
                    # Fallback: calculate average across all cores if package sensor isn't exposed
                    avg_temp = sum(core_temps_list) / len(core_temps_list)
                    cpu_temp = f"{avg_temp:.1f}°C"
                elif entries:
                    # Fallback for Raspberry Pi / ARM (often has empty label "")
                    cpu_temp = f"{entries[0].current:.1f}°C"
        except Exception:
            pass

    table.add_column("CPU")
    table.add_column("Usage")
    table.add_column("Temp")

    table.add_row(
        f"Main {cpu_freq_str}", usage_details(cpu_usage, "cpu"), f"{cpu_temp}"
    )
    for i, core_usage in enumerate(cpu_core_usage):
        temp_val = cpu_core_temp.get(i)
        cpu_core_temp_n = f"{temp_val:.1f}°C" if temp_val is not None else "-N/A-"
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

    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)

    table.add_column("RAM")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    ram_v_data = psutil.virtual_memory()
    ram_v_usage = ram_v_data.percent
    used1 = f"{ram_v_data.used/(1024**3):.2f}GB"
    free1 = f"{ram_v_data.available/(1024**3):.2f}GB"
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
        new_r = values.read_bytes / (1024**2)
        new_w = values.write_bytes / (1024**2)
        r_count = values.read_count
        w_count = values.write_count

        if drive in _disk_cache:
            old_time, old_r, old_w = _disk_cache[drive]
            elapsed = current_time - old_time
            if elapsed > 0:
                read = (new_r - old_r) / elapsed
                write = (new_w - old_w) / elapsed
            else:
                read, write = 0.0, 0.0
        else:
            read, write = 0.0, 0.0

        _disk_cache[drive] = (current_time, new_r, new_w)
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
        dev_name = d_detail.device.lower()
        if any(x in dev_name for x in ("wi-fi", "wlp", "wlan", "wireless")):
            emoji = "🛜"
        elif any(x in dev_name for x in ("ethernet", "eth", "enp", "en1", "lan")):
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

        new_s = sent_bytes / (1024**2)
        new_r = recv_bytes / (1024**2)

        if device in _net_cache:
            old_time, old_s, old_r = _net_cache[device]
            elapsed = current_time - old_time
            if elapsed > 0:
                upload = (new_s - old_s) / elapsed
                download = (new_r - old_r) / elapsed
            else:
                upload, download = 0.0, 0.0
        else:
            upload, download = 0.0, 0.0

        _net_cache[device] = (current_time, new_s, new_r)
        info = Info(device, upload, download, new_s, new_r)
        d_details.append(info)

    return d_details


def bat_table():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)
    table.add_column("Battery")

    try:
        battry_details = psutil.sensors_battery()
    except Exception:
        battry_details = None

    if battry_details:
        b_percent = battry_details.percent
        b_plugged = battry_details.power_plugged
        if b_plugged:
            time_left = "--N/A--"
            status = "plugged in"
        else:
            status = "not plugged in"
            secs = battry_details.secsleft
            # Fixed: Check for valid, positive seconds remaining
            if (
                secs
                not in (None, psutil.POWER_TIME_UNKNOWN, psutil.POWER_TIME_UNLIMITED)
                and secs > 0
            ):
                hrs = secs // 3600
                miniut = (secs % 3600) // 60
                time_left = f"{hrs}h {miniut}m"
            else:
                time_left = "--N/A--"

        battery_info = f"🔋 Percentage : {b_percent}%   Status : {status}   Time left : {time_left}"
    else:
        battery_info = "🔋 -------------N/A-------------"

    table.add_row(battery_info)
    return table


def fan_table():
    table = Table(show_header=True, box=None, padding=(0, 1), expand=True)
    table.add_column("Fan Manu.")
    table.add_column("Type")
    table.add_column("Speed")

    if psutil.LINUX:
        try:
            fan_data = psutil.sensors_fans()
            for mf, fan_list in fan_data.items():
                # Added nested loop for the list of fans
                for fan_d in fan_list:
                    label = fan_d.label or "-N/A-"
                    table.add_row(f"❄️ {mf}", f"{label}", f"{fan_d.current}RPM")
        except Exception:
            pass
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
    for p in psutil.process_iter(
        [
            "name",
            "pid",
            "ppid",
            "status",
            "username",
            "cpu_percent",
            "memory_percent",
        ]
    ):
        try:
            proc = p.info
            cpu = proc["cpu_percent"] or 0.0
            mem = proc["memory_percent"] or 0.0
            data = (
                f"{no}",
                f"{proc['name'] or '-'}",
                f"{proc['pid'] or '-'}",
                f"{proc['ppid'] or '-'}",
                f"{proc['status'] or '-'}",
                f"{proc['username'] or '-'}",
                f"{cpu:.2f}",
                f"{mem:.2f}",
            )
            no += 1
            yield data
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
    text = Text(ascii_art, no_wrap=True)

    return text
