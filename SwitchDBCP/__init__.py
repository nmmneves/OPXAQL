import shutil
import sys
from SwitchDBCP.DataHandler import Handler
from SwitchDBCP.Utils import Utils

han = Handler()

han.get_all_switch_data()
han.get_all_interface_data()
han.get_all_current_neighbours()
