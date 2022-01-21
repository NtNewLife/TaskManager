from select import select
import psutil #Used to retrieve process in cross platform
from datetime import datetime
import pandas as pd
import time
import os
import argparse

def Process_Priority_Windows(x):
    return {
        128     : 'Hight',
        32768   : 'Above Normal',
        16384   : 'Below Normal',
        64      : 'Idle',
        32      : 'Normal',
        1048576 : 'Background Begin',
        2097152 : 'Background End',
        256     : 'Realtime'
    }.get(x, 'Unknown')

def Get_Processes():
    process_list = []
    for process in psutil.process_iter():
        # Get processes info with multithreading
        with process.oneshot():
            process_creation_time = datetime.fromtimestamp(process.create_time())
            cpu_usage = process.cpu_percent()
            status = process.status()

            try:
                # Get processes priority : linux = 0 -> 128
                priority = int(process.nice())
                if(os.name == 'nt'):
                    priority = Process_Priority_Windows(priority)
            except psutil.AccessDenied:
                if(os.name == 'nt'):
                    priority = 'Unknown'
                else:
                    nice = 0
                    
            try:
                memory_usage = process.memory_full_info().uss
            except psutil.AccessDenied:
                memory_usage = 0

            io_counters = process.io_counters()
            read_bytes = io_counters.read_bytes
            write_bytes = io_counters.write_bytes

            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "Unknown"
            process_list.append({
            'name': process.name(), 'pid': process.pid, 'cpu_usage': cpu_usage, 'read_bytes': read_bytes, 'write_bytes': write_bytes, 'username': username, 'create_time': process_creation_time,
            'status': status, 'priority': priority, 'memory_usage': memory_usage
        })

    return process_list

def Create_Dataframe(processes):
    dataframe = pd.DataFrame(processes)

    # PID = index du dataframe
    dataframe.set_index('pid', inplace=True)

    dataframe['create_time'] = dataframe['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",))

    dataframe = dataframe[columns.split(",")]
    return dataframe

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task Manager")
    parser.add_argument("-c", help="""Column to show,
                                                exemple : name,create_time,cpu_usage,status,priority,memory_usage,read_bytes,write_bytes,username.""",
                        default="name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,priority")
    parser.add_argument("-n", help="Number of processes to show. Default = every", default=0)
    parser.add_argument("-u", help="Show processes periodicaly untill manual close.", default=False)

    args        = parser.parse_args()
    columns     = args.c
    n           = int(args.n)
    live_update = args.u

    processes = Get_Processes()
    df = Create_Dataframe(processes)

    if n == 0:
        print(df.to_string())
    elif n > 0:
        print(df.head(n).to_string())


    while live_update:
        processes = Get_Processes()
        df = Create_Dataframe(processes)
        
        if(os.name == 'nt'):
            os.system("cls")
        else:
            os.system("clear")

        if n == 0:
            print(df.to_string())
        elif n > 0:
            print(df.head(n).to_string())
        time.sleep(1)