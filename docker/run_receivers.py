import subprocess
from sys import argv
import shlex

init_port = int(argv[1])
number = int(argv[2])

command = "slsReceiver --rx_tcpport "

processes = []
print(shlex.split(command + str(init_port)))
for i in range(number):
    processes.append(subprocess.Popen(shlex.split(command + str(init_port + i))))

try:
    for p in processes:
        p.wait()
except:
    for p in processes:
        p.terminate()
