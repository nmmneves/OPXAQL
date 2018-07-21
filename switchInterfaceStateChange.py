import os
import subprocess
import time

def timeLogger():
    start = time.time()
    print(start)
    directory = "SwitchDBCP/Log"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open("SwitchDBCP/Log/times.txt", "a!") as myfile:
        myfile.write('Script| Change Interface Time Start:' + str(start) + '\n')
        myfile.close()

def clearfile():
    print('---')
    directory = "SwitchDBCP/Log"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open("SwitchDBCP/Log/times.txt","a!") as myfile2:
        myfile2.write('-------New Test-------' + '\n')
        myfile2.close()

clearfile()
while (True):
    subprocess.Popen(["sudo","ip","link","set","e101-001-0","up"])
    timeLogger()
    print("UP")
    time.sleep(4)
    subprocess.Popen(["sudo", "ip", "link", "set", "e101-001-0", "down"])
    timeLogger()
    print("DOWN")
    time.sleep(4)





