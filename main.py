from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static
from textual import work
from textual.worker import Worker, WorkerState
from rich.console import Console
from textual.events import MouseMove
import sys
import shelve
from func import (
    bat_table,
    cpu_table_1,
    cpu_table_2,
    disk_table_1,
    disk_table_2,
    fan_table,
    network_table,
    process_table_1,
    process_table_2,
    program_name,
    ram_table,
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
                        yield Static(cpu_table_1(), id="cpu_table_1")
                    with ScrollableContainer(id="cpu_table_2_container"):
                        yield Static(cpu_table_2(), id="cpu_table_2")
                with Vertical(id="right"):
                    with ScrollableContainer(id="ram_table_container"):
                        yield Static(ram_table(), id="ram_table")
                    with ScrollableContainer(id="disk_table_1_container"):
                        yield Static(disk_table_1(), id="disk_table_1")
                    with ScrollableContainer(id="disk_table_2_container"):
                        yield Static(disk_table_2(), id="disk_table_2")
                    with ScrollableContainer(id="network_table_container"):
                        yield Static(network_table(), id="network_table")
                    with ScrollableContainer(id="bat_table_container"):
                        yield Static(bat_table(), id="bat_table")
                    with ScrollableContainer(id="fan_table_container"):
                        yield Static(fan_table(), id="fan_table")

    def update_fast_table(self):
        # cpu_table
        self.query_one("#cpu_table_1", Static).update(cpu_table_1())
        # ram_table
        self.query_one("#ram_table", Static).update(ram_table())
        # disk_table
        self.query_one("#disk_table_2", Static).update(disk_table_2())
        # network_table
        self.query_one("#network_table", Static).update(network_table())
        
    def update_slow_table(self):
        # disk_table
        self.query_one("#disk_table_1", Static).update(disk_table_1())
        # bat_table
        self.query_one("#bat_table", Static).update(bat_table())
        # fan_table
        self.query_one("#fan_table", Static).update(fan_table())

    def on_mount(self):
        self.query_one("#title", Static).update(program_name())
        self.query_one("#cpu_table_2", Static).update(cpu_table_2())
        self.set_interval(1.2, self.update_fast_table)
        self.set_interval(3,self.update_slow_table)

class ProcessScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with ScrollableContainer(id="process_container"):
            yield Static("Loading......", id="process_table_2")

    def on_mount(self):
        self.is_active_screen = True

    def on_screen_resume(self):
        # 1. When you enter the screen, set the flag to True and start the loop
        self.is_active_screen = True
        self.process_table()

    def on_screen_suspend(self):
        # 2. When you leave the screen, set to False. This breaks the infinite loop!
        self.is_active_screen = False

    @work(thread=True, name="process_fetcher",exclusive=True)
    def process_table(self):
        return process_table_2()

    def on_worker_state_changed(self, event: Worker.StateChanged):
        if self.is_active_screen == True:
            if event.worker.name == "process_fetcher":
                if event.state == WorkerState.SUCCESS:
                    self.query_one("#process_table_2", Static).update(event.worker.result)
                    self.set_timer(1.5, self.process_table)

                elif event.state == WorkerState.ERROR:
                    self.query_one("#process_table_2", Static).update(
                        f"[red]Pipeline failed: {event.worker.error}[/red]"
                    )


class SysCore(App):
    CSS_PATH = "main.tcss"
    SCREENS = {
        "main": MainScreen,
        "process": ProcessScreen,
    }
    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("ctrl+a", "main_scr", "Main Screen"),
        ("ctrl+d", "process_scr", "Process Screen"),
    ]

    def watch_theme(self, new_theme: str) -> None:
        with shelve.open("theme.db") as db:
            db["theme"] = new_theme

    def on_mount(self):
        with shelve.open("theme.db") as db:
            self.theme = db.get("theme", "textual-dark")
        self.push_screen("main")
        
        # Default hover tracking to False to save CPU
        self.mouse_tracking_active = False 

    def on_key(self, event):
        # Press 'm' to toggle hover tracking on and off
        if event.character == "m":
            self.mouse_tracking_active = not self.mouse_tracking_active
            self.notify(f"Mouse Hover Tracking: {'ON' if self.mouse_tracking_active else 'OFF'}")

    def post_message(self, message) -> bool:
        # Intercept messages before they enter Textual's event loop
        if isinstance(message, MouseMove):
            # If no button is clicked (hovering) AND tracking is off, destroy the event
            if message.button == 0 and not getattr(self, "mouse_tracking_active", False):
                return False # 0 CPU overhead!
        
        # Allow all other events (clicks, scroll wheel, key presses) to pass normally
        return super().post_message(message)

    def action_main_scr(self):
        self.switch_screen("main")

    def action_process_scr(self):
        self.switch_screen("process")

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
        app = SysCore()
        app.run()
    else:
        sys.exit("Wrong Comand.....")


if __name__ == "__main__":
    main()