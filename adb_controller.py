import subprocess
import time

class AdbController:
    def __init__(self, adb_path, ip='127.0.0.1', port=21513):
        self._down_touches = set()
        self._down_keys = set()
        self._adb = self._get_adb_shell(adb_path, ip, port)

    def __del__(self):
        for key in self._down_keys:
            self.key_up(key)

        self._end_touches()

        try:
            self._adb.kill()
        except Exception as e:
            raise e

    def _get_adb_shell(self, adb_path, ip, port):
        cmd_args = [adb_path, '-s', '{}:{}'.format(ip, port), 'shell']
        return subprocess.Popen(
            cmd_args, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE)

    def tell_adb(self, ev_type, ev_arg1, ev_arg2):
        cmd_args = ' '.join([
            'sendevent',
            '/dev/input/event6',
            str(event_types[ev_type.upper()]), 
            str(arg1_codes[ev_arg1.upper()]), 
            str(ev_arg2),
            '\n'
        ])
        self._adb.stdin.write(cmd_args.encode())
        self._adb.stdin.flush()

    def _end_event(self):
        self.tell_adb('EV_SYN', 'SYN_REPORT', 0)

    def _send_key(self, key, down):
        self.tell_adb('EV_KEY', 'KEY_' + key, down)
        self._end_event()

    def _begin_touches(self):
        self.tell_adb('EV_KEY', 'BTN_TOUCH', 1)

    def _send_touches(self):
        for touch in self._down_touches:
            x, y = key_map[touch]
            self.tell_adb('EV_ABS', 'ABS_MT_PRESSURE', 1)
            self.tell_adb('EV_ABS', 'ABS_MT_POSITION_X', x)
            self.tell_adb('EV_ABS', 'ABS_MT_POSITION_Y', y)
            self.tell_adb('EV_SYN', 'SYN_MT_REPORT', 0)
        if self._down_touches:
            self._end_event()

    def _end_touches(self):
        self.tell_adb('EV_KEY', 'BTN_TOUCH', 0)
        self._end_event()

    def key_down(self, key):
        key = key.lower()
        if key in keyboard_keys:
            if key not in self._down_keys:
                self._down_keys.add(key)
                self._send_key(key, down=1)
        else:
            if key not in self._down_touches:
                if key not in key_map:
                    raise ValueError('Key not mapped: ', key)

                if len(self._down_touches) == 0:
                    self._begin_touches()

                self._down_touches.add(key)
                self._send_touches()

    def key_up(self, key):
        key = key.lower()
        if key in keyboard_keys:
            if key in self._down_keys:
                self._down_keys.remove(key)
                self._send_key(key, down=0)
        else:
            if key in self._down_touches:
                self._down_touches.remove(key)
                self._send_touches()

                if len(self._down_touches) == 0:
                    self._end_touches()

    def press_key(self, key, t_during=0.01, t_after=0.01):
        self.key_down(key)
        time.sleep(t_during)
        self.key_up(key)
        time.sleep(t_after)

    def swipe(self, start_xy, end_xy, t_after=0.01):
        cmd_args = ' '.join([
            'input',
            'swipe',
            str(start_xy[0]),
            str(start_xy[1]),
            str(end_xy[0]),
            str(end_xy[1]),
            '\n'
            ])
        self._adb.stdin.write(cmd_args.encode())
        self._adb.stdin.flush()
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
    'up', 'left', 'down', 'right', 'esc'
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
    'f1': (0x064, 0x033),
    '`': (0x036, 0x109),
    'tab': (0x038, 0x14e),
    'alt': (0x14c, 0x298),
    'z': (0x263, 0x280),
    'n': (0x33d, 0x293),
    'a': (0x3ba, 0x298),
    'x': (0x441, 0x288),
    'c': (0x4be, 0x25b),
    's': (0x3b7, 0x238),
    'd': (0x404, 0x1e7),
    'f': (0x46b, 0x1e6),
    'g': (0x4cb, 0x1e5),
    'o': (0x3dd, 0x183),
    'p': (0x42b, 0x181),
    '[': (0x47b, 0x181),
    ']': (0x4cb, 0x17f),
    '\\': (0x477, 0x11e),
    'h': (0x1bc, 0x211), # dialog NO
    'r': (0x22f, 0x0d7), # cancel auto quest guide
    't': (0x281, 0x243), # confirm autoplay
    'y': (0x2d7, 0x0d8), # quest teleport
    'k': (0x35d, 0x212), # dialog YES
    'l': (0x498, 0x09f), # task GET button

    'quest-dialog-multiple-1': (0x164, 0x215),

    'guide-mission': (0x2ab, 0x025),
    'event': (0x2e9, 0x024),
    'package': (0x3d8, 0x023),
    'cash-shop': (0x415, 0x022),
    'mailbox': (0x453, 0x023),

    'bag': (0x48f, 0x023),
    'bag-extract': (0x400, 0x297),
    'bag-extract-extract': (0x274, 0x297),
    'bag-extract-extract-confirm': (0x317, 0x285),
    'bag-extract-extract-confirm-complete': (0x281, 0x289),

    'shop': (0x39e, 0x024),
    'shop-potion-hp': (0xfb, 0x7d),
    'shop-potion-mp': (0x19a, 0x7d),
    'shop-potion-hp-v3': (0x27d, 0x10d),
    'shop-potion-hp-v4': (0x32c, 0x10d),
    'shop-potion-hp-v5': (0x3df, 0x10d),
    'shop-potion-mp-v3': (0x27d, 0x10d),
    'shop-potion-mp-v4': (0x32c, 0x10d),
    'shop-potion-mp-v5': (0x3df, 0x10d),
    'shop-potion-buy-100': (0x4a5, 0x1a5),
    'shop-potion-buy-confirm': (0x3b8, 0x282),

    'task': (0x328, 0x023),
    'task-get': (0x498, 0x09f), # task GET button

    'dungeons': (0x362, 0x025),
    'daily-duty-1': (0x234, 0x251),
    'daily-duty-2': (0x341, 0x24c),
    'daily-duty-3': (0x4ab, 0x250),

    'task-daily-mission': (0x6d, 0x82),
    'task-achievement': (0x6e, 0x138),
    'task-weekly-mission': (0x70, 0x18e),
    'task-daily-hunt': (0x6e, 0x1e4),

    'dungeons-daily': (0x8a, 0xd4),
    'dungeons-daily-hard': (0x63, 0x196),
    'dungeons-daily-very-hard': (0x68, 0x1df),
    'dungeons-daily-hell': (0x67, 0x21d),
    'dungeons-daily-snow-witch': (0x97, 0x9e),
    'dungeons-daily-lich': (0x183, 0x97),
    'dungeons-daily-angry-frankenroid': (0x295, 0x95),
    'dungeons-daily-master-specter': (0x37b, 0x96),
    'dungeons-daily-manon': (0x67d, 0x9a),

    'dungeons-elite': (0x165, 0xc8),
    # No point auto-ing elite...

    'dungeons-mini': (0x251, 0xc3),
    'dungeons-mini-swip-start': (0xa5, 0x27f),
    'dungeons-mini-swip-end': (0xa5, 0xd6),
    'dungeons-mini-30m': (0x366, 0x18e),
    'dungeons-mini-60m': (0x3ee, 0x18e),
    'dungeons-mini-120m': (0x47d, 0x18e),

    'dungeons-mulung': (0x417, 0xce),

    'dungeons-nett': (0x4c0, 0xd9),
    'dungeons-nett-chaos': (0x67, 0x111),

    'menu': (0x4d8, 0x20),
    'menu-challenge': (0x16c, 0x3a),
    'menu-challenge-quest': (0xe2, 0xae),
    'menu-challenge-quest-top': (0x21e, 0x98),
    'menu-challenge-quest-auto': (0x495, 0x297),

    'side-menu': (0x4e0, 0x127),
    'side-achievement': (0x4d6, 0xf6),

    'quick-revive': (0x28e, 0x20e),
    'normal-revive': (0x190, 0x20e)
}

# from adb_controller import AdbController as AC             
# ac=AC(adb_path='/mnt/d/AndroidSDK/platform-tools/adb.exe') 