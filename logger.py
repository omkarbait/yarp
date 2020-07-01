import time
import subprocess
import glob
import os

list_of_files = glob.glob('/mnt/work/work/HI_DATA/yarrp/*.log')

while True:
    logfile = max(list_of_files, key=os.path.getctime)
    subprocess.run('cat {}'.format(logfile), shell=True, check=True) 
    time.sleep(10)

