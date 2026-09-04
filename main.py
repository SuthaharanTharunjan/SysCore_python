from rich.console import Console
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

def main_cpu_details():
    usage = Progress(
        TextColumn("{task.description}"),
        BarColumn(bar_width=38),                              
        TaskProgressColumn(),
        FrequencyColumn()
        )
    cpu_task = usage.add_task("", total=100, freq=0.00)
    main_cpu_detail=(usage,cpu_task)
    return main_cpu_detail

def sub_cpu_details():
    n_of_cores=psutil.cpu_count(logical=False)
    sub_cpu_detail=[]
    for i in range(n_of_cores):
        progress=Progress(
            TextColumn("{task.description}"),
            BarColumn(),                              
            TaskProgressColumn()
            )
        task_id = progress.add_task(f"Core {i} : ", total=100)
        data=(progress,task_id)
        sub_cpu_detail.append(data)
    return sub_cpu_detail

    
def cpu_table(main_cpu_detail,sub_cpu_detail):
    usage=main_cpu_detail[0]

    table = Table(show_header=False, box=None)
    table.add_column("CPU")
    table.add_column("Usage")

    table.add_row("CPU",usage,)
    for i in range(len(sub_cpu_detail)):
        table.add_row("⚙️",sub_cpu_detail[i][0],)
    return table

def cpu_table_updator(table,main_cpu_detail,sub_cpu_detail):
    usage=main_cpu_detail[0]
    cpu_task=main_cpu_detail[1]
    
    with Live(table, refresh_per_second=10):
        while True:
            cpu_usage=psutil.cpu_percent(interval=None,percpu=False)
            cpu_freq=(psutil.cpu_freq(percpu=False).current)/1000
            usage.update(cpu_task, completed=cpu_usage ,freq=cpu_freq)
            cpu_core_usage=psutil.cpu_percent(interval=None,percpu=True)
            
            for i in  range(len(sub_cpu_detail)):
                progress=sub_cpu_detail[i]
                progress[0].update(progress[1], completed=cpu_core_usage[i])
                
                
            time.sleep(1)


def main():
    console = Console()
    

    main_cpu_detail = main_cpu_details()
    sub_cpu_detail= sub_cpu_details()
    cpu_table_updator(cpu_table(main_cpu_detail,sub_cpu_detail),main_cpu_detail,sub_cpu_detail)
    

if __name__=="__main__":
    main()