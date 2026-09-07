from rich.console import Console
from rich.table import Table
from rich import box
from rich.live import Live
import psutil
import time
from pynput import keyboard
import itertools

def get_process_data(scroll, height, pid_dict):
    new_pid_list = dict(itertools.islice(pid_dict.items(), scroll, scroll+height))
    row_list=[]
    for no,pid in new_pid_list.items():
        try:
            p = psutil.Process(pid)
            data = (
                f"{no}",
                f"{p.name()}",
                f"{pid}",
                f"{p.status()}",
                f"{p.username()}",
                f"{p.cpu_percent(interval=0.1):.2f}",
                f"{p.memory_percent():.2f}",
                f"{p.exe()}"
            )
            row_list.append(data)
            no += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return row_list

def process_table(row_list):
    table = Table(show_header=True, box=box.MARKDOWN, padding=(0, 1))
    table.add_column("No.")
    table.add_column("Name")
    table.add_column("PID")
    table.add_column("Status")
    table.add_column("User Name")
    table.add_column("CPU")
    table.add_column("RAM")
    table.add_column("Location")

    for row in row_list:
        table.add_row(*row)
    

    return table

console = Console()
scroll = 0   # shared state

def on_press(key):
    global scroll
    try:
        if key == keyboard.Key.up and scroll > 0:
            scroll -= 1
        elif key == keyboard.Key.down:
            scroll += 1
    except AttributeError:
        pass

def get_pid():
    pid=psutil.pids()
    pid_dict={}
    for i,value in enumerate(pid):
        pid_dict[i]=value
    return pid_dict

console = Console()
scroll = 0   # shared state

def main():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # run in background, non-blocking
    pid_dict=get_pid()
    global scroll
    

    with Live(refresh_per_second=1, screen=True) as live:
        while True:
            height = console.height
            row_list=get_process_data(scroll,height-3,pid_dict)
            table = process_table(row_list)
            live.update(table)
            time.sleep(1)  # smoother updates

if __name__ == "__main__":
    main()