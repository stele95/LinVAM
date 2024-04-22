# -*- coding: utf-8 -*-
import atexit
import struct
from glob import glob
from threading import Thread
from time import time as now

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

event_bin_format = 'llHHI'

# Taken from include/linux/input.h
# https://www.kernel.org/doc/Documentation/input/event-codes.txt
EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04

INVALID_ARGUMENT_ERRNO = 22


def make_uinput():
    import fcntl, struct

    # Requires uinput driver, but it's usually available.
    uinput = open("/dev/uinput", 'wb')
    UI_SET_EVBIT = 0x40045564

    UI_SET_KEYBIT = 0x40045565

    BTN_MOUSE = 0x110
    BTN_LEFT = 0x110
    BTN_RIGHT = 0x111
    BTN_MIDDLE = 0x112
    BTN_SIDE = 0x113
    BTN_EXTRA = 0x114
    BTN_FORWARD = 0x115
    BTN_BACK = 0x116
    BTN_TASK = 0x117
    BTN_WHEEL = 0x150
    X = 0x00
    Y = 0x01
    WHEEL = 0x08

    try:
        # mouse buttons
        fcntl.ioctl(uinput, UI_SET_EVBIT, EV_KEY)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_MOUSE)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_LEFT)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_RIGHT)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_MIDDLE)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_SIDE)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_EXTRA)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_FORWARD)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_BACK)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_TASK)
        fcntl.ioctl(uinput, UI_SET_KEYBIT, BTN_WHEEL)

        # mouse absolute movement
        fcntl.ioctl(uinput, UI_SET_EVBIT, EV_ABS)
        # fcntl.ioctl(uinput, UI_SET_ABSBIT, X)
        # fcntl.ioctl(uinput, UI_SET_ABSBIT, Y)
        # fcntl.ioctl(uinput, UI_SET_ABSBIT, WHEEL)

        # mouse relative movement
        fcntl.ioctl(uinput, UI_SET_EVBIT, EV_REL)
        # fcntl.ioctl(uinput, UI_SET_RELBIT, X)
        # fcntl.ioctl(uinput, UI_SET_RELBIT, Y)
        # fcntl.ioctl(uinput, UI_SET_RELBIT, WHEEL)
    except OSError as e:
        if e.errno != INVALID_ARGUMENT_ERRNO:
            raise e

    BUS_USB = 0x03
    uinput_user_dev = "80sHHHHi64i64i64i64i"
    axis = [0] * 64 * 4
    uinput.write(struct.pack(uinput_user_dev, b"Virtual Mouse", BUS_USB, 1, 1, 1, 0, *axis))
    uinput.flush()  # Without this you may get Errno 22: Invalid argument.

    UI_DEV_CREATE = 0x5501
    fcntl.ioctl(uinput, UI_DEV_CREATE)
    UI_DEV_DESTROY = 0x5502
    # fcntl.ioctl(uinput, UI_DEV_DESTROY)

    return uinput


class EventDevice(object):
    def __init__(self, path):
        self.path = path
        self._input_file = None
        self._output_file = None

    @property
    def input_file(self):
        if self._input_file is None:
            try:
                self._input_file = open(self.path, 'rb')
            except IOError as e:
                if e.strerror == 'Permission denied':
                    print(
                        "# ERROR: Failed to read device '{}'. You must be in the 'input' group to access global events. Use 'sudo usermod -a -G input USERNAME' to add user to the required group.".format(
                            self.path))
                    exit()

            def try_close():
                try:
                    self._input_file.close
                except:
                    pass

            atexit.register(try_close)
        return self._input_file

    @property
    def output_file(self):
        if self._output_file is None:
            self._output_file = open(self.path, 'wb')
            atexit.register(self._output_file.close)
        return self._output_file

    def read_event(self):
        data = self.input_file.read(struct.calcsize(event_bin_format))
        seconds, microseconds, type, code, value = struct.unpack(event_bin_format, data)
        return seconds + microseconds / 1e6, type, code, value, self.path

    def write_event(self, type, code, value):
        integer, fraction = divmod(now(), 1)
        seconds = int(integer)
        microseconds = int(fraction * 1e6)
        data_event = struct.pack(event_bin_format, seconds, microseconds, type, code, value)

        # Send a sync event to ensure other programs update.
        sync_event = struct.pack(event_bin_format, seconds, microseconds, EV_SYN, 0, 0)

        self.output_file.write(data_event + sync_event)
        self.output_file.flush()


class AggregatedEventDevice(object):
    def __init__(self, devices, output=None):
        self.event_queue = Queue()
        self.devices = devices
        self.output = output or self.devices[0]

        def start_reading(device):
            while True:
                self.event_queue.put(device.read_event())

        for device in self.devices:
            thread = Thread(target=start_reading, args=[device])
            thread.setDaemon(True)
            thread.start()

    def read_event(self):
        return self.event_queue.get(block=True)

    def write_event(self, type, code, value):
        self.output.write_event(type, code, value)


import re
from collections import namedtuple

DeviceDescription = namedtuple('DeviceDescription', 'event_file is_mouse is_keyboard')
device_pattern = r"""N: Name="([^"]+?)".+?H: Handlers=([^\n]+)"""


def list_devices_from_proc(type_name):
    try:
        with open('/proc/bus/input/devices') as f:
            description = f.read()
    except FileNotFoundError:
        return

    devices = {}
    for name, handlers in re.findall(device_pattern, description, re.DOTALL):
        path = '/dev/input/event' + re.search(r'event(\d+)', handlers).group(1)
        if type_name in handlers:
            yield EventDevice(path)


def list_devices_from_by_id(type_name):
    for path in glob('/dev/input/by-id/*-event-' + type_name):
        yield EventDevice(path)


def aggregate_devices(type_name):
    # Some systems have multiple keyboards with different range of allowed keys
    # on each one, like a notebook with a "keyboard" device exclusive for the
    # power button. Instead of figuring out which keyboard allows which key to
    # send events, we create a fake device and send all events through there.
    uinput = make_uinput()
    fake_device = EventDevice('uinput Fake Mouse Device')
    fake_device._input_file = uinput
    fake_device._output_file = uinput

    # We don't aggregate devices from different sources to avoid
    # duplicates.

    devices_from_proc = list(list_devices_from_proc(type_name))
    if devices_from_proc:
        return AggregatedEventDevice(devices_from_proc, output=fake_device)

    # breaks on mouse for virtualbox
    # was getting /dev/input/by-id/usb-VirtualBox_USB_Tablet-event-mouse
    devices_from_by_id = list(list_devices_from_by_id(type_name))
    if devices_from_by_id:
        return AggregatedEventDevice(devices_from_by_id, output=fake_device)

    # If no keyboards were found we can only use the fake device to send keys.
    return fake_device
