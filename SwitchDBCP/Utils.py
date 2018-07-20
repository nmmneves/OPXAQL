import time
import os

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
    def timeLogger(text):
        start = time.time()
        directory = "SwitchDBCP/Log"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open("SwitchDBCP/Log/times.txt", "a!") as myfile:
            myfile.write(text + str(start)+'\n')
            myfile.close()