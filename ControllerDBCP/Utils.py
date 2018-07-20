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
        directory = "ControllerDBCP/Log"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open("ControllerDBCP/Log/times.txt", "a!") as myfile:
            myfile.write(text + str(start)+'\n')
            myfile.close()

    @staticmethod
    def extractNetworkFromIpv4(ip, prefix):

        # Assuming the ip address is well formatted...
        # Extract network
        split = ip.split(".")

        result = ""
        if (prefix == 32):
            result = ip

        if (prefix == 24):
            result = split[0] + "." + split[1] + "." + split[2] + ".0"

        if (prefix == 16):
            result = split[0] + "." + split[1] + ".0.0"

        if (prefix == 8):
            result = split[0] + ".0.0.0"

        return result
