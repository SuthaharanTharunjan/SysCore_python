from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, DataTable
from textual import work
import psutil

from func import (
    program_name,
    cpu_table_1,
    cpu_table_2,
    ram_table,
    disk_table_1,
    disk_table_2,
    network_table,
    bat_table,
    fan_table,
    get_process_data,
)


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with ScrollableContainer(id="main_container"):
            with Vertical(id="top"):
                yield Static(program_name(), id="title")
            with Horizontal():
                with Vertical(id="left"):
                    with ScrollableContainer(id="cpu_table_1_container"):
                        yield Static("Loading CPU...", id="cpu_table_1")
                    with ScrollableContainer(id="cpu_table_2_container"):
                        yield Static(cpu_table_2(), id="cpu_table_2")
                with Vertical(id="right"):
                    with ScrollableContainer(id="ram_table_container"):
                        yield Static("Loading RAM...", id="ram_table")
                    with ScrollableContainer(id="disk_table_1_container"):
                        yield Static(id="disk_table_1")
                    with ScrollableContainer(id="disk_table_2_container"):
                        yield Static(id="disk_table_2")
                    with ScrollableContainer(id="network_table_container"):
                        yield Static(id="network_table")
                    with ScrollableContainer(id="bat_table_container"):
                        yield Static(id="bat_table")
                    with ScrollableContainer(id="fan_table_container"):
                        yield Static(id="fan_table")

    def on_mount(self) -> None:
        self.collect_metrics()
        self.set_interval(1.0, self.collect_metrics)

    @work(thread=True, exclusive=True)
    def collect_metrics(self) -> None:
        c1 = cpu_table_1()
        ram = ram_table()
        d1 = disk_table_1()
        d2 = disk_table_2()
        net = network_table()
        bat = bat_table()
        fan = fan_table()

        self.app.call_from_thread(self._update_ui, c1, ram, d1, d2, net, bat, fan)

    def _update_ui(self, c1, ram, d1, d2, net, bat, fan) -> None:
        # Prevent NoMatches errors if screen was switched mid-worker execution
        if not self.is_mounted:
            return

        self.query_one("#cpu_table_1", Static).update(c1)
        self.query_one("#ram_table", Static).update(ram)
        self.query_one("#disk_table_1", Static).update(d1)
        self.query_one("#disk_table_2", Static).update(d2)
        self.query_one("#network_table", Static).update(net)
        self.query_one("#bat_table", Static).update(bat)
        self.query_one("#fan_table", Static).update(fan)


class ProcessScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield DataTable(id="process_table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "No.", "Name", "PID", "PPID", "Status", "User Name", "CPU", "RAM"
        )

        self.fetch_processes()
        self.set_interval(2.0, self.fetch_processes)

    @work(thread=True, exclusive=True)
    def fetch_processes(self) -> None:
        rows = list(get_process_data())
        self.app.call_from_thread(self._render_processes, rows)

    def _render_processes(self, rows: list) -> None:
        if not self.is_mounted:
            return

        table = self.query_one(DataTable)
        table.clear()
        table.add_rows(rows)


class SysCore(App):
    CSS_PATH = "main.tcss"
    SCREENS = {
        "main": MainScreen,
        "process": ProcessScreen,
    }
    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("ctrl+q", "no_op"),
        ("left", "main_scr", "Main Screen"),
        ("right", "process_scr", "Process Screen"),
    ]

    def on_mount(self) -> None:
        # Calibrate psutil initial counters so first cycle is not 0.0%
        psutil.cpu_percent(interval=None, percpu=False)
        psutil.cpu_percent(interval=None, percpu=True)
        self.push_screen("main")

    def action_no_op(self) -> None:
        pass

    def action_main_scr(self) -> None:
        self.switch_screen("main")

    def action_process_scr(self) -> None:
        self.switch_screen("process")


if __name__ == "__main__":
    app = SysCore()
    app.run()