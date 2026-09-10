from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header ,Static
from textual import work
from func import program_name
from func import cpu_table_1
from func import cpu_table_2
from func import ram_table
from func import disk_table_1
from func import disk_table_2
from func import network_table
from func import bat_table
from func import fan_table
from func import process_table_2

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
                        yield Static(cpu_table_2(),id="cpu_table_2")
                with Vertical(id="right"):
                    with ScrollableContainer(id="ram_table_container"):
                        yield Static(ram_table(),id="ram_table")
                    with ScrollableContainer(id="disk_table_1_container"):
                        yield Static(disk_table_1(),id="disk_table_1")
                    with ScrollableContainer(id="disk_table_2_container"):
                        yield Static(disk_table_2(),id="disk_table_2")
                    with ScrollableContainer(id="network_table_container"):
                        yield Static(network_table(),id="network_table")        
                    with ScrollableContainer(id="bat_table_container"):
                        yield Static(bat_table(),id="bat_table")
                    with ScrollableContainer(id="fan_table_container"):
                        yield Static(fan_table(),id="fan_table")
                        
    def update_all_table(self):
        #cpu_table
        self.query_one("#cpu_table_1",Static).update(cpu_table_1())
        self.query_one("#cpu_table_2",Static).update(cpu_table_2())
        #ram_table
        self.query_one("#ram_table",Static).update(ram_table())
        #disk_table
        self.query_one("#disk_table_1",Static).update(disk_table_1())
        self.query_one("#disk_table_2",Static).update(disk_table_2())
        #network_table
        self.query_one("#network_table",Static).update(network_table())
        #bat_table
        self.query_one("#bat_table",Static).update(bat_table())
        #fan_table
        self.query_one("#fan_table",Static).update(fan_table())
                
        
    def on_mount(self):
        self.query_one("#title",Static).update(program_name())
        self.set_interval(1,self.update_all_table)

        
class ProcessScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()    
        with ScrollableContainer(id="process_container"):
            yield Static(process_table_2(),id="process_table_2")  

    def process_table(self):
        self.query_one("#process_table_2",Static).update(process_table_2())

    def on_mount(self):
        self.set_interval(5,self.process_table)
    
class SysCore(App):
    CSS_PATH = "main.tcss"
    SCREENS = {
        "main":MainScreen,
        "process":ProcessScreen,
    }
    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("ctrl+q", "no_op"),
        ("left", "main_scr", "Main Screen"),
        ("right", "process_scr", "Process Screen"),
        ]

    def on_mount(self):
        self.push_screen("main")
    
    def action_no_op(self):
        pass
    
    def action_main_scr(self):
        self.switch_screen("main")

    def action_process_scr(self):
        self.switch_screen("process")

if __name__ == "__main__":
    app = SysCore()
    app.run()