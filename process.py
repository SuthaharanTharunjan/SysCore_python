from rich.console import Console
from rich.table import Table
from rich import box
from rich.live import Live
import psutil
import time
from pynput import keyboard


def get_process_data():
    no=1
    for i,p in enumerate(psutil.process_iter(
        ["name", "pid", "status", "username", "cpu_percent", "memory_percent","exe"]
    )):
        proc = p.info
        if proc.get("username") != None :
            data=(
                f"{no}",
                f"{proc.get("name")}",
                f"{proc.get("pid")}",
                f"{proc.get("status")}",
                f"{proc.get("username")}",
                f"{proc.get("cpu_percent"):.2f}",
                f"{proc.get("memory_percent"):.2f}",
                f"{proc.get("exe")}"
            )
            no += 1
        yield data
    

def process_table(scroll,height):
    table = Table(show_header=True, box=box.MARKDOWN, padding=(0, 1))
    table.add_column("No.")
    table.add_column("Name")
    table.add_column("PID")
    table.add_column("Status")
    table.add_column("User Name")
    table.add_column("CPU")
    table.add_column("RAM")
    table.add_column("Location")
    old_data=[]
    for data in get_process_data():
        old_data.append(data)
        if len(old_data)==scroll+height :
            break
    new_row_data=old_data[scroll:scroll+height]
    for row in new_row_data:
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


def main():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # run in background, non-blocking

    with Live(refresh_per_second=1, screen=True) as live:
        while True:
            height = console.height
            table = process_table(scroll, height-1)
            live.update(table)
            time.sleep(0.5)  # smoother updates

if __name__ == "__main__":
    main()
