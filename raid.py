from adb_controller import *
from time import sleep
from random import random
import code

def main():
    adb_path = "/mnt/d/AppData/Android/SDK/platform-tools/adb.exe"
    ac = AdbController(adb_path=adb_path, port=5555)
    wait_range = 3
    wait_base = wait_range * 1.4

    while True:
        ac.press_key('r')
        sleep(wait_base + (random() - 0.5) * wait_range)
    code.interact(local={**globals(), **locals()})

if __name__ == '__main__':
    main()