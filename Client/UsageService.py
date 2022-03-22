import os
import psutil
import shutil
import time
import requests

def start(  DataPath , Id , secret , ServerAddress , rpc_address ):
    while 1:
        # Getting loadover15 minutes

        load1 , _ , _ = psutil.getloadavg()
        CpuUsage    = ( load1/os.cpu_count() ) * 100
        MemoryAvialable = psutil.virtual_memory().available / 1024**3
        MemoryTotal     = psutil.virtual_memory().total / 1024**3
        MemoryUsage     = MemoryTotal - MemoryAvialable

        total, used, free = shutil.disk_usage( DataPath )
        DiskTotal = (total / (2**30))
        DiskUsage = (used / (2**30))

        payload = { "CPU" : CpuUsage , "MemTotal" : MemoryTotal , "MemUsage" : MemoryUsage , "DiskTotal" : DiskTotal , "DiskUsage" : DiskUsage , "secret" : secret , "Id" : Id }
        
        res = requests.post( f"{ServerAddress}submitStatistic" , data = payload )
        if res.status_code != 200:
            raise Exception("Error with connection to main server ( Usage service )")
        # Send request
        print( payload )

        time.sleep(60)