from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, DataTable
from textual import work
from textual.worker import Worker, WorkerState
from rich.console import Console
from textual.events import MouseMove
from textual.theme import Theme
import sys
import shelve
from func import (
    bat_table,
    cpu_table_1,
    cpu_table_2,
    disk_table_1,
    disk_table_2,
    get_process_data,
    fan_table,
    network_table,
    process_table_1,
    #process_table_2,
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
            yield DataTable(id="process_table")

    def on_mount(self):
        self.is_active_screen = True
        self.process_limit_active = True 
        self.old_processes_pid = set()

        self.table = self.query_one(DataTable)
        self.table.cursor_type="row"
        self.table.add_column("Name", key="0")
        self.table.add_column("PID", key="1")
        self.table.add_column("PPID", key="2")
        self.table.add_column("Status", key="3")
        self.table.add_column("User Name", key="4")
        self.table.add_column("CPU", key="5")
        self.table.add_column("RAM", key="6")

    def on_key(self, event):
        if event.character == "l":
            self.process_limit_active = not self.process_limit_active
            self.notify(f"Process Limit (50): {'ON' if self.process_limit_active else 'OFF'}")
            self.fetch_process_table_data()

    def row_updator(self, processes):
        old_pids = self.old_processes_pid
        new_pids = set()
        update_cell = self.table.update_cell
        add_row = self.table.add_row
        remove_row = self.table.remove_row

        with self.app.batch_update():
            for data in processes:
                pid = data[1] # PID
                new_pids.add(pid)

                if pid in old_pids:
                    update_cell(pid, "0", data[0])
                    update_cell(pid, "2", data[2])
                    update_cell(pid, "3", data[3])
                    update_cell(pid, "4", data[4])
                    update_cell(pid, "5", data[5])
                    update_cell(pid, "6", data[6])
                else:
                    add_row(*data, key=pid)

            for pid in old_pids - new_pids:
                try:
                    remove_row(pid)
                except Exception:
                    pass

        self.old_processes_pid = new_pids

        try:
            self.table.sort("5", key=float, reverse=True)
        except Exception:
            pass

    def on_screen_resume(self):
        self.is_active_screen = True
        self.fetch_process_table_data()

    def on_screen_suspend(self):
        self.is_active_screen = False

    @work(thread=True, name="process_fetcher", exclusive=True)
    def fetch_process_table_data(self):
        limit = 50 if getattr(self, "process_limit_active", True) else None
        return list(get_process_data(limit))

    def on_worker_state_changed(self, event: Worker.StateChanged):
        if self.is_active_screen and event.worker.name == "process_fetcher":
            if event.state == WorkerState.SUCCESS:
                self.row_updator(event.worker.result)
                self.set_timer(1.2, self.fetch_process_table_data)

            elif event.state == WorkerState.ERROR:
                self.notify(f"Process fetch failed: {event.worker.error}", severity="error", timeout=5)
                self.set_timer(2.0, self.fetch_process_table_data)

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
        self.register_theme(dusk_light)
        self.register_theme(dusk_dark)
        self.register_theme(cyber_neon)
        self.register_theme(forest_moss)
        self.register_theme(magma)
        self.register_theme(bioluminescence)
        self.register_theme(copper_patina)
        self.register_theme(arcade_carpet)
        self.register_theme(midnight_desert)
        self.register_theme(paper_ink)
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


dusk_light = Theme(
    name="dusklight",
    primary="#99dfff",       # Fluorescent Azure / Aqua
    secondary="#3c96fc",     # Deep Vibrant Blue
    warning="#fff86b",       # Bright Fluorescent Yellow
    error="#ff5252",         # Vibrant Red
    success="#6bffa3",       # Fluorescent Green
    accent="#fff86b",        # Yellow Accent
    background="#0d131f",    # Deep Midnight Blue Base
    surface="#151e2e",       # Elevated Midnight Blue (for cards/containers)
    panel="#1c283d",         # Lighter Panel Blue (for modals/popups)
    dark=True,
)

dusk_dark = Theme(
    name="duskdark",
    primary="#00d7ff",      # Cyan borders, graphs, and default text
    secondary="#2a7bde",    # Deep blue (seen in 'Avail' memory bar)
    warning="#dce775",      # Yellow-green (seen in 'Cache' and 'Page+Virt' bars)
    error="#ff3333",        # Red for critical alerts (inferred from btop standards)
    success="#00d7ff",      # Cyan for stable states
    accent="#ff8c00",       # Bright orange (seen in highlighted letters like 'menu' or 'mem')
    background="#000000",   # Pure black terminal background from the screenshot
    surface="#0f1419",      # Slight elevation for Textual containers
    panel="#171d24",        # Lighter elevation for popups/modals
    dark=True,
)

cyber_neon = Theme(
    name="cyber_neon",
    primary="#ff007f",      # Neon Pink
    secondary="#7100b8",    # Deep Purple
    warning="#fcee0a",      # Cyber Yellow
    error="#ff003c",        # Crimson Red
    success="#00ff9f",      # Mint Green
    accent="#00f0ff",       # Neon Cyan
    background="#050514",   # Almost black, slight blue-purple tint
    surface="#10102b",      
    panel="#1a1a40",        
    dark=True,
)

forest_moss = Theme(
    name="forest_moss",
    primary="#8ebd6b",      # Moss Green
    secondary="#5c7551",    # Dark Leaf
    warning="#d6a848",      # Golden Earth
    error="#c46c49",        # Clay Red
    success="#a2b374",      # Pale Grass
    accent="#e3c28a",       # Sandstone
    background="#191f1b",   # Very dark forest green/grey
    surface="#252d27",      
    panel="#313b33",        
    dark=True,
)

magma = Theme(
    name="magma",
    primary="#ff5a00",      # Bright Magma Orange
    secondary="#9e2a2b",    # Cooled Lava Red
    warning="#ff9f1c",      # Glowing Yellow
    error="#540b0e",        # Deep Burn Red
    success="#e09f3e",      # Amber
    accent="#fff3b0",       # White-hot center
    background="#0d0d0d",   # Charred Black
    surface="#1a1515",      
    panel="#261b1b",        
    dark=True,
)

bioluminescence = Theme(
    name="bioluminescence",
    primary="#00f5d4",      # Glowing Neon Teal
    secondary="#00bbf9",    # Deep Sea Bright Blue
    warning="#fee440",      # Yellow Tang
    error="#f15bb5",        # Hot Magenta
    success="#38b000",      # Algae Green
    accent="#9b5de5",       # Ultraviolet Coral
    background="#040d14",   # Deep Abyss Blue-Black
    surface="#0a1c29",      # Elevated Oceanic Blue
    panel="#102b40",        # Lighter Water Column
    dark=True,
)

copper_patina = Theme(
    name="copper_patina",
    primary="#c27a5d",      # Raw Copper / Rust
    secondary="#7a9c96",    # Oxidized Teal Patina
    warning="#d4a373",      # Polished Brass
    error="#9c4a3a",        # Iron Red
    success="#6b8e23",      # Olive Drab
    accent="#e0c097",       # Bleached Bone / Ash
    background="#1a1817",   # Soot Black
    surface="#2b2624",      # Dark Industrial Brown
    panel="#3d3532",        # Weathered Steel
    dark=True,
)

arcade_carpet = Theme(
    name="arcade_carpet",
    primary="#39ff14",      # CRT Phosphor Green
    secondary="#ff00ff",    # Laser Magenta
    warning="#ffea00",      # Pac-Man Yellow
    error="#ff073a",        # Arcade Cabinet Red
    success="#00ffff",      # Electric Cyan
    accent="#b026ff",       # Blacklight Purple
    background="#0d0514",   # Pitch Purple-Black
    surface="#180a2b",      # Shadow Purple
    panel="#250f45",        # Arcade Dim Lighting
    dark=True,
)

midnight_desert = Theme(
    name="midnight_desert",
    primary="#ff9e00",      # Horizon Orange
    secondary="#c77dff",    # Night Sky Violet
    warning="#ffc300",      # Starlight Yellow
    error="#d00000",        # Canyon Red
    success="#74c69d",      # Saguaro Green
    accent="#ffdb3a",       # Brilliant Flare
    background="#120e1f",   # Midnight Blue-Purple
    surface="#1e172e",      # Distant Mountains
    panel="#2a1f3d",        # Elevated Mesa
    dark=True,
)

paper_ink = Theme(
    name="paper_ink",
    primary="#2c363f",      # Graphite / Pen Ink
    secondary="#596c68",    # Faded Teal Ink
    warning="#d08c60",      # Sepia Wash
    error="#9e2a2b",        # Red Proofing Ink
    success="#52796f",      # Muted Forest Green
    accent="#8f3d4c",       # Burgundy Wax Seal
    background="#f4f1ea",   # Warm Vellum Paper
    surface="#e6e1d6",      # Pressed Cardboard
    panel="#d9d3c5",        # Darker Paper Grain
    dark=False,             # Note: Light theme for a completely different TUI feel
)

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