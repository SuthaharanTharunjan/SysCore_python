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


class FrequencyColumn(ProgressColumn):
    def render(self, task):
        return Text(f"[{task.fields['freq']:.2f} GHz]")


def usage_details(usage, name=None):
    progress = Progress(
        TextColumn("{task.description}", justify="right"),
        BarColumn(bar_width=30),
        TaskProgressColumn(),
    )
    if name == "cpu":
        progress.add_task(":", total=100, completed=usage)
    else:
        progress.add_task("", total=100, completed=usage)

    return progress


def cpu_table():
    table = Table(show_header=True, box=None)

    cpu_usage = psutil.cpu_percent(interval=None, percpu=False)
    cpu_freq = (psutil.cpu_freq(percpu=False).current) / 1000

    cpu_core_usage = psutil.cpu_percent(interval=None, percpu=True)

    table.add_column("CPU")
    table.add_column(usage_details(cpu_usage, "cpu"))
    table.add_column(f"[{cpu_freq:.2f}GHz]")

    for i, core_usage in enumerate(cpu_core_usage):
        table.add_row(f"⚙️ Core {i}", usage_details(core_usage, "cpu"), "")
    return table


def table_updator():
    with Live(refresh_per_second=1) as live:
        while True:
            table1 = cpu_table()
            table2 = ram_table()
            col = Columns([table1, table2])
            live.update(col)

            time.sleep(1)


def ram_table():

    table = Table(show_header=True, box=None)

    table.add_column("RAM")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Total")

    used1 = f"{psutil.virtual_memory().used*1e-9:.2f}GB"
    free1 = f"{psutil.virtual_memory().free*1e-9:.2f}GB"
    total1 = f"{psutil.virtual_memory().total*1e-9:.2f}GB"

    used2 = f"{psutil.swap_memory().used*1e-9:.2f}GB"
    free2 = f"{psutil.swap_memory().free*1e-9:.2f}GB"
    total2 = f"{psutil.swap_memory().total*1e-9:.2f}GB"

    ram_v_usage = psutil.virtual_memory().percent
    table.add_row("📀 Virtual", usage_details(ram_v_usage, "ram"), used1, free1, total1)
    ram_s_usage = psutil.swap_memory().percent
    table.add_row("💿 Swap", usage_details(ram_s_usage, "ram"), used2, free2, total2)
    return table


def main():
    console = Console()
    table_updator()


if __name__ == "__main__":
    main()
