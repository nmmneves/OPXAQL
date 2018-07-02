import time

import os

import errno


class Utils:

    @staticmethod
    def cliLogger(text, level):
        # Different levels of debug output.
        if (level == 0):
            start = time.time()
            print("["+str(start) + "]"+ text)

        #if (level == 1):
            #print(text)

        return

    @staticmethod
    def timeLogger():
          start = time.time()
     #   directory = "SwitchDBCP/Log"
     #   if not os.path.exists(directory):
     #       os.makedirs(directory)

     #   with open("SwitchDBCP/Log/times.txt", "a!") as myfile:
     #       myfile.write(str(start)+'\n')
     #       myfile.close()


