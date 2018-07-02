import networkx as nx
#import matplotlib
import os

#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
import time
class Utils:

    @staticmethod
    def cliLogger(text, level):
        # Different levels of debug output.
        if (level == 0):
            start = time.time()
            print("[" + str(start) + "]" + text)

        # if (level == 1):
        # print(text)

        return

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
