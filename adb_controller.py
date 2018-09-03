import subprocess
import time

class AdbController:
    def __init__(self, adb_path, ip='127.0.0.1', port=21503):
        self._down_touches = set()
        self._down_keys = set()
        self._adb = self._get_adb_shell(adb_path, ip, port)
            
    def _get_adb_shell(self, adb_path, ip, port):
        cmd = lambda args: [adb_path, *args] 
        devices = subprocess.check_output(cmd(['devices'])).decode('utf-8')

        def rem_nl(s):
            i = len(s) - 1
            while i > 0 and not s[i].isalnum():
                i -= 1
            return s[:i+1]

        print(rem_nl(devices))
        if 'offline' in devices:
            print('Could not connect to server')
            exit(1)

        cmd_args = cmd(['-s', '{}:{}'.format(ip, port), 'shell'])
        return subprocess.Popen(
            cmd_args, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE)

    def tell_adb(self, ev_type, ev_arg1, ev_arg2):
        cmd_args = ' '.join([
            'sendevent',
            '/dev/input/event6',
            str(event_types[ev_type]), 
            str(arg1_codes[ev_arg1]), 
            str(ev_arg2),
            '\n'
        ])
        self._adb.stdin.write(cmd_args.encode())
        self._adb.stdin.flush()

    def _end_event(self):
        self.tell_adb('EV_SYN', 'SYN_REPORT', 0)

    def _send_touches(self):
        for touch in self._down_touches:
            x, y = key_map[touch]
            self.tell_adb('EV_ABS', 'ABS_MT_PRESSURE', 1)
            self.tell_adb('EV_ABS', 'ABS_MT_POSITION_X', x)
            self.tell_adb('EV_ABS', 'ABS_MT_POSITION_Y', y)
            self.tell_adb('EV_SYN', 'SYN_MT_REPORT', 0)
        if self._down_touches:
            self._end_event()

    def key_down(self, key):
        key = key.upper()
        if key in keyboard_keys:
            if key not in self._down_keys:
                self._down_keys.add(key)
                self.tell_adb('EV_KEY', 'KEY_' + key, 1)
                self._end_event()
        else:
            if key not in self._down_touches:
                if key not in key_map:
                    raise ValueError('Key not mapped: ', key)

                if len(self._down_touches) == 0:
                    self.tell_adb('EV_KEY', 'BTN_TOUCH', 1)

                self._down_touches.add(key)
                self._send_touches()

    def key_up(self, key):
        key = key.upper()
        if key in keyboard_keys:
            if key in self._down_keys:
                self._down_keys.remove(key)
                self.tell_adb('EV_KEY', 'KEY_' + key, 0)
                self._end_event()
        else:
            if key in self._down_touches:
                self._down_touches.remove(key)
                self._send_touches()

                if len(self._down_touches) == 0:
                    self.tell_adb('EV_KEY', 'BTN_TOUCH', 0)
                    self._end_event()

    def press_key(self, key, t_during=0.01, t_after=0.02):
        self.key_down(key)
        time.sleep(t_during)
        self.key_up(key)
        time.sleep(t_after)

# key press:
# EV_KEY       KEY_LEFT             DOWN    
# EV_SYN       SYN_REPORT           00000000
# EV_KEY       KEY_LEFT             UP      
# EV_SYN       SYN_REPORT           00000000

# touch:
# EV_KEY       BTN_TOUCH            DOWN    
# EV_ABS       ABS_MT_PRESSURE      00000001
# EV_ABS       ABS_MT_POSITION_X    000004bf
# EV_ABS       ABS_MT_POSITION_Y    00000261
# EV_SYN       SYN_MT_REPORT        00000000
# EV_SYN       SYN_REPORT           00000000
# EV_KEY       BTN_TOUCH            UP      
# EV_SYN       SYN_REPORT           00000000

# multitouch:
# EV_KEY       BTN_TOUCH            DOWN     
# EV_ABS       ABS_MT_PRESSURE      00000001 
# EV_ABS       ABS_MT_POSITION_X    000004bf 
# EV_ABS       ABS_MT_POSITION_Y    00000261 
# EV_SYN       SYN_MT_REPORT        00000000 
# EV_SYN       SYN_REPORT           00000000 
# EV_ABS       ABS_MT_PRESSURE      00000001 
# EV_ABS       ABS_MT_POSITION_X    000004bf 
# EV_ABS       ABS_MT_POSITION_Y    00000261 
# EV_SYN       SYN_MT_REPORT        00000000 
# EV_ABS       ABS_MT_PRESSURE      00000001 
# EV_ABS       ABS_MT_POSITION_X    000003b3 
# EV_ABS       ABS_MT_POSITION_Y    00000236 
# EV_SYN       SYN_MT_REPORT        00000000 
# EV_SYN       SYN_REPORT           00000000 
# EV_ABS       ABS_MT_PRESSURE      00000001 
# EV_ABS       ABS_MT_POSITION_X    000004bf 
# EV_ABS       ABS_MT_POSITION_Y    00000261 
# EV_SYN       SYN_MT_REPORT        00000000 
# EV_SYN       SYN_REPORT           00000000 
# EV_KEY       BTN_TOUCH            UP       
# EV_SYN       SYN_REPORT           00000000 

keyboard_keys = {
    'UP', 'LEFT', 'DOWN', 'RIGHT', 'ESC'
}
arg1_codes = {
    'SYN_REPORT': 0x0,
    'SYN_MT_REPORT': 0x2,
    'ABS_MT_PRESSURE': 0x3a,
    'ABS_MT_POSITION_X': 0x35,
    'ABS_MT_POSITION_Y': 0x36,
    'BTN_TOUCH': 0x14a,
    'KEY_UP': 0x67,
    'KEY_LEFT': 0x69,
    'KEY_DOWN': 0x6c,
    'KEY_RIGHT': 0x6a,
    'KEY_ESC': 0x01
}
event_types = {
    'EV_SYN': 0x0,
    'EV_KEY': 0x1,
    'EV_ABS': 0x3
}
key_map = {
    'UP': (0x9d, 0x1e4),
    'DOWN': (0x9d, 0x295),
    'LEFT': (0x44, 0x23c),
    'RIGHT': (0xf5, 0x23c),
    '`': (0x3f, 0x10c),
    'TAB': (0x14d, 0x295),
    'T': (0x280, 0x23b),
    'B': (0x280, 0x287),
    'N': (0x33f, 0x295),
    'A': (0x3b8, 0x299),
    'X': (0x441, 0x279),
    'C': (0x4bf, 0x260),
    'S': (0x3b5, 0x236),
    'D': (0x401, 0x1e7),
    'F': (0x46f, 0x1e8),
    'G': (0x4ca, 0x1ea),
    'I': (0x398, 0x190),
    'O': (0x3e0, 0x185),
    'P': (0x42d, 0x183),
    '[': (0x478, 0x182),
    ']': (0x4cd, 0x183),
    '=': (0x4d6, 0x136),
    '-': (0x4d6, 0xf0),
    'L': (0x498, 0xa1),
    'U': (0x3d7, 0x80),
    '1': (0x2a9, 0x29),
    '2': (0x2ec, 0x29),
    '3': (0x328, 0x2a),
    '4': (0x364, 0x29),
    '5': (0x3a2, 0x29),
    '6': (0x3db, 0x28),
    '7': (0x414, 0x26),
    '8': (0x454, 0x26),
    '9': (0x493, 0x26),
    'E': (0x280, 0xda),
    'E': (0x280, 0xda),
    '0': (0x4d5, 0x28)
}