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
from rich.panel import Panel
import psutil
import platform
import time
from collections import namedtuple
from pynput import keyboard


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


def get_process_data():
    for i, p in enumerate(
        psutil.process_iter(
            ["name", "pid", "status", "username", "cpu_percent", "memory_percent"]
        )
    ):
        proc = p.info
        data = (
            f"{i}",
            f"{proc.get("name")}",
            f"{proc.get("pid")}",
            f"{proc.get("status")}",
            f"{proc.get("username")}",
            f"{proc.get("cpu_percent"):.2f}",
            f"{proc.get("memory_percent"):.2f}",
        )
        yield data


def process_table(scroll, height):
    table = Table(show_header=True, box=None, padding=(0, 1))
    table.add_column("No.")
    table.add_column("Name")
    table.add_column("PID")
    table.add_column("Status")
    table.add_column("User Name")
    table.add_column("CPU")
    table.add_column("RAM")
    old_data = []
    for data in get_process_data():
        old_data.append(data)
        if len(old_data) == scroll + height:
            break
    new_row_data = old_data[scroll : scroll + height]
    for row in new_row_data:
        table.add_row(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

    return table


console = Console()
scroll = 0  # shared state


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

    with Live(refresh_per_second=3, screen=True) as live:
        while True:
            height = console.height
            table = process_table(scroll, height - 1)
            live.update(table)
            time.sleep(0.5)  # smoother updates


if __name__ == "__main__":
    main()
