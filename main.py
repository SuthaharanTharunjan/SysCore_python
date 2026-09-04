from rich.console import Console, Group
from rich.table import Table 
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn ,ProgressColumn
from rich.live import Live
from rich.text import Text
import psutil
import platform
import time

class FrequencyColumn(ProgressColumn):
    def render(self,task):
        return Text(f"[{task.fields['freq']:.2f} GHz]")

def main_cpu_usage_details():
    usage = Progress(
        TextColumn("{task.description}"),
        BarColumn(bar_width=38),                              
        TaskProgressColumn(),
        FrequencyColumn()
        )
    cpu_task = usage.add_task("", total=100, freq=0.00)
    main_cpu_usage_detail=(usage,cpu_task)
    return main_cpu_usage_detail


    
def cpu_table(main_cpu_usage_detail,sub_cpu_usage_detail):
    usage=main_cpu_usage_detail[0]

    table = Table(show_header=False, box=None)
    table.add_column("CPU")
    table.add_column("Usage")

    table.add_row("CPU",usage,)
    for i in range(len(sub_cpu_usage_detail)):
        table.add_row("⚙️",sub_cpu_usage_detail[i][0],)
    return table

def table_updator(
        table1,
        table2,
        main_cpu_detail,
        sub_cpu_detail,
        ram_vertual_usage_detail,
        ram_swap_usage_detail,
        ):
    usage=main_cpu_detail[0]
    cpu_task=main_cpu_detail[1]
    
    with Live(Group(table1, table2),refresh_per_second=10):
        while True:
            cpu_usage=psutil.cpu_percent(interval=None,percpu=False)
            cpu_freq=(psutil.cpu_freq(percpu=False).current)/1000
            usage.update(cpu_task, completed=cpu_usage ,freq=cpu_freq)
            cpu_core_usage=psutil.cpu_percent(interval=None,percpu=True)

            ram_v_usage=psutil.virtual_memory().percent
            ram_vertual_usage_detail[0][0].update(ram_vertual_usage_detail[0][1],completed=ram_v_usage)

            ram_s_usage=psutil.swap_memory().percent
            ram_swap_usage_detail[0][0].update(ram_swap_usage_detail[0][1],completed=ram_s_usage)

            table2.columns[2]._cells[0]=f"{psutil.virtual_memory().used*1e-9:.2f}GB"
            table2.columns[3]._cells[0]=f"{psutil.virtual_memory().free*1e-9:.2f}GB"
            table2.columns[4]._cells[0]=f"{psutil.virtual_memory().total*1e-9:.2f}GB"
            table2.columns[2]._cells[1]=f"{psutil.swap_memory().used*1e-9:.2f}GB"
            table2.columns[3]._cells[1]=f"{psutil.swap_memory().free*1e-9:.2f}GB"
            table2.columns[4]._cells[1]=f"{psutil.swap_memory().total*1e-9:.2f}GB"
            for i in  range(len(sub_cpu_detail)):
                progress=sub_cpu_detail[i]
                progress[0].update(progress[1], completed=cpu_core_usage[i])
                
                
            time.sleep(1)

def ram_table(ram_vertual_usage_detail,ram_swap_usage_detail):
    table = Table(show_header=True, box=None)
    table.add_column("RAM")
    table.add_column("Usage")
    table.add_column("Used")
    table.add_column("Available")
    table.add_column("Total")
    table.add_row("📀 Virtual",ram_vertual_usage_detail[0][0],"g","hi","hi")
    table.add_row("💿 Swap",ram_swap_usage_detail[0][0],"g","hi","hi")
    return table


def usage_details(times,name=None):
    usage_detail=[]
    for i in range(times):
        progress=Progress(
                    TextColumn("{task.description}"),
                    BarColumn(),                              
                    TaskProgressColumn()
                    )
        if name == "cpu":
            cpu=f"Core {i} : "
            task_id=progress.add_task(cpu, total=100)
        else:
            task_id=progress.add_task("", total=100)
        data=(progress,task_id)
        usage_detail.append(data)
    return usage_detail

def main():
    console = Console()
    ram_vertual_usage_detail=usage_details(1,"ram")
    ram_swap_usage_detail=usage_details(1,"ram")

    main_cpu_usage_detail = main_cpu_usage_details()
    n_of_cores=psutil.cpu_count(logical=False)
    sub_cpu_usage_detail= usage_details(n_of_cores,"cpu")
    table1=cpu_table(main_cpu_usage_detail,sub_cpu_usage_detail)
    table2=ram_table(ram_vertual_usage_detail,ram_swap_usage_detail)
    table_updator(
        table1,
        table2,
        main_cpu_usage_detail,
        sub_cpu_usage_detail,
        ram_vertual_usage_detail,
        ram_swap_usage_detail,
        )
    


    
if __name__=="__main__":
    main()