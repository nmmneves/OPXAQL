#Start symetric ds server
import os
import subprocess
import time

while (True):
    subprocess.Popen(["sudo","ip","link","set","e101-001-0","up"])
    timeLogger()
    print("UP")
    time.sleep(4)
    subprocess.Popen(["sudo", "ip", "link", "set", "e101-001-0", "down"])
    timeLogger()
    print("DOWN")
    time.sleep(4)





