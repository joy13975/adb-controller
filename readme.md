# adb-controller

A Python interface for sending keyboard presses and screen touches via ADB shell. 

You may use it to automatically debug your Android app or do something on an emulator. 

<b><em>What you do with this tool is your responsibility</em></b>.

## Goal

A Python interface to send key presses and screen touches to ADB.

Status: supports arrow keys and a custom key map that I myself use.

Known bugs: I've observed what looked like broken pipe between the controller and the stdout of the adb shell process. Reason is still unknown.


## Install

For now: download the raw .py file into your source directory.

TODO: Make a wheel?

## Usage

```python
from adb_controller import AdbController
adb_ctrl = AdbController(
		adb_path=your_adb_binary_path,
		ip=your_device_ip,
		port=your_device_port)
```

## API:

```python
AdbController.key_up(key)
AdbController.key_up(key)
AdbController.press_key(key)
AdbController.tell_adb(ev_type, ev_arg1, ev_arg2)
```

Arrow keys are mapped to keyboard arrow keys instead of screen touches because many games support keyboard keys by default and it's much more sensitive than simulating clicks on the UI joystick.

TODO: Proper joystick control for direction keys?

## Keymap

For now: modify the `key_map` dictionary in `adb_controller.py` to your liking (key -> x y position tuple).

TODO: Separate key map into a JSON?