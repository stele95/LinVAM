import json
import os
import shlex
import signal
import subprocess
import threading
import time

import sounddevice
from vosk import Model, KaldiRecognizer

from linvam import keyboard, mouse
from linvam.keyboard import nixkeyboard as _os_keyboard
from linvam.mouse import ButtonEvent
from linvam.mouse import nixmouse as _os_mouse
from linvam.soundfiles import SoundFiles
from linvam.util import (get_language_code, get_voice_packs_folder_path, get_language_name, YDOTOOLD_SOCKET_PATH,
                         KEYS_SPLITTER, save_to_commands_file, is_push_to_listen, get_push_to_listen_hotkey, Command)


def _execute_external_command(cmd_name, is_async):
    if is_async:
        # pylint: disable=consider-using-with
        subprocess.Popen(cmd_name, shell=True)
    else:
        subprocess.run(cmd_name, shell=True)


class ProfileExecutor(threading.Thread):

    def __init__(self, p_parent=None):

        super().__init__()
        self.m_profile = None
        self.ptl_key = None
        self.ptl_keyboard_listener = None
        self.ptl_mouse_listener = None
        self.listening = False
        self.commands_list = []
        self.m_cmd_threads = {}
        self.p_parent = p_parent
        self.ydotoold = None
        if not self.p_parent.m_config['keyboard'] or not self.p_parent.m_config['mouse']:
            self.start_ydotoold()

        self.m_stream = None

        device_info = sounddevice.query_devices(kind='input')
        # sounddevice expects an int, sounddevice provides a float:
        self.samplerate = int(device_info['default_samplerate'])

        self.recognizer = None

        self.m_sound = SoundFiles()

    def set_sound_playback_volume(self, volume):
        self.m_sound.set_volume(volume)

    def start_ydotoold(self):
        command = 'ydotoold -p ' + YDOTOOLD_SOCKET_PATH + ' -P 0666'
        args = shlex.split(command)
        # noinspection PyBroadException
        try:
            # pylint: disable=consider-using-with
            self.ydotoold = subprocess.Popen(args)
        except Exception as e:
            print('Failed to start ydotoold: ' + str(e))

    # noinspection PyUnusedLocal
    # pylint: disable=unused-argument
    def listen_callback(self, in_data, frame_count, time_info, status):
        result_string = self.get_listen_result(in_data)
        if not result_string:
            return
        self.check_commands(result_string)

    # noinspection PyUnusedLocal
    # pylint: disable=unused-argument
    def listen_callback_debug(self, in_data, frame_count, time_info, status):
        result_string = self.get_listen_result(in_data)
        if not result_string:
            return
        print(str(result_string))
        self.check_commands(result_string)

    def check_commands(self, result_string):
        for command in self.commands_list:
            if command in result_string:
                self.recognizer.Result()
                print('Detected: ' + command)
                self._do_command(command)
                break

    def get_listen_result(self, in_data):
        if self.recognizer is None:
            return ''
        if self.recognizer.AcceptWaveform(bytes(in_data)):
            result = self.recognizer.Result()
        else:
            result = self.recognizer.PartialResult()
        result_json = json.loads(result)
        try:
            result_string = result_json['partial']
        except KeyError:
            return ''
            # result_string = result_json['text']
        return result_string

    def set_language(self, language):
        self._stop()
        language_code = get_language_code(language)
        if language_code is None:
            print('Unsupported language: ' + language)
            return
        print('Language: ' + get_language_name(language))
        self.recognizer = KaldiRecognizer(Model(lang=language_code), self.samplerate)

    def _init_stream(self):
        if self.recognizer is None:
            return
        if self.p_parent.m_config['debug']:
            callback = self.listen_callback_debug
        else:
            callback = self.listen_callback
        self.m_stream = sounddevice.RawInputStream(
            samplerate=self.samplerate,
            dtype="int16",
            channels=1,
            blocksize=4000,
            callback=callback
        )

    def _start_stream(self):
        if self.m_stream is None:
            self._init_stream()
        self.m_stream.start()

    def set_profile(self, p_profile):
        self.m_profile = p_profile
        self.commands_list = []
        if self.m_profile is None:
            print('Clearing profile')
            return
        w_commands = self.m_profile['commands']
        for w_command in w_commands:
            parts = w_command['name'].split(',')
            for part in parts:
                self.commands_list.append(part)
        print('Profile: ' + self.m_profile['name'])
        save_to_commands_file(self.commands_list)
        # this is a dirty fix until the whole keywords recognition is refactored
        self.commands_list.sort(key=len, reverse=True)

    def reset_listening(self):
        if self.listening:
            self.set_enable_listening(False)
            self.set_enable_listening(True)

    def set_enable_listening(self, p_enable):
        if self.recognizer is None:
            return
        if not self.listening and p_enable:
            ptl_hotkey = get_push_to_listen_hotkey()
            if is_push_to_listen() and ptl_hotkey:
                self._init_stream()
                print('Stream initialized, press ' + ptl_hotkey.name.upper() + ' to listen for commands')
                self.listening = True
                self._start_ptl(ptl_hotkey)
            else:
                self._start_stream()
                print('Detection started')
                self.listening = True
        elif self.listening and not p_enable:
            self._stop()

    def _start_ptl(self, ptl_hotkey):
        self.ptl_key = ptl_hotkey
        if ptl_hotkey.is_mouse_key:
            self.ptl_mouse_listener = mouse.hook(self._on_mouse_key_event)
        else:
            self.ptl_keyboard_listener = keyboard.hook(self._on_keyboard_key_event)

    def _on_mouse_key_event(self, event):
        if not isinstance(event, ButtonEvent):
            return
        if str(event.button) == str(self.ptl_key.button):
            if event.event_type == mouse.DOWN and not self.m_stream.active:
                self.m_stream.start()
            elif event.event_type == mouse.UP and self.m_stream.active:
                self._stop_ptl_stream()

    def _stop_ptl_stream(self):
        # sleep for 1 second to allow said commands to be processed correctly
        time.sleep(0.5)
        self.m_stream.stop()
        self.recognizer.Result()

    def _on_keyboard_key_event(self, event):
        if event.name == 'unknown':
            return
        if int(event.scan_code) == int(self.ptl_key.code):
            if event.event_type == keyboard.KEY_DOWN and not self.m_stream.active:
                self.m_stream.start()
            elif event.event_type == keyboard.KEY_UP and self.m_stream.active:
                self._stop_ptl_stream()

    def _stop(self):
        if self.m_stream is not None:
            self._stop_ptl_listener()
            self.m_stream.stop()
            self.m_stream.close()
            self.m_stream = None
            self.recognizer.FinalResult()
            self.listening = False
            print('Detection stopped')

    def shutdown(self):
        self.m_sound.stop()
        self._stop()
        if self.ydotoold is not None:
            try:
                os.kill(self.ydotoold.pid, signal.SIGKILL)
                self.ydotoold = None
            except OSError:
                pass

    def _stop_ptl_listener(self):
        # noinspection PyBroadException
        # pylint: disable=bare-except,R0801
        try:
            if self.ptl_keyboard_listener is not None:
                self.ptl_keyboard_listener()
                self.ptl_keyboard_listener = None
            if self.ptl_mouse_listener is not None:
                mouse.unhook(self.ptl_mouse_listener)
                self.ptl_mouse_listener = None
        except Exception as ex:
            print(str(ex))

    def do_action(self, p_action):
        # {'name': 'key action', 'key': 'left', 'type': 0}
        # {'name': 'pause action', 'time': 0.03}
        # {'name': 'command stop action', 'command name': 'down'}
        # {'name': 'mouse move action', 'x':5, 'y':0, 'absolute': False}
        # {'name': 'mouse click action', 'button': 'left', 'type': 0}
        # {'name': 'mouse wheel action', 'delta':10}
        w_action_name = p_action['name']
        match w_action_name:
            case Command.KEY_ACTION:
                self._press_key(p_action)
            case Command.PAUSE_ACTION:
                print("Sleep ", p_action['time'])
                time.sleep(p_action['time'])
            case Command.COMMAND_STOP_ACTION:
                self._stop_command(p_action['command name'])
            case Command.EXECUTE_VOICE_COMMAND_ACTION:
                self._execute_voice_command(p_action['command name'])
            case Command.EXECUTE_EXTERNAL_COMMAND_ACTION:
                _execute_external_command(p_action['command'], False)
            case Command.COMMAND_PLAY_SOUND | Command.PLAY_SOUND:
                self._play_sound(p_action)
            case Command.STOP_SOUND:
                self.m_sound.stop()
            case Command.MOUSE_MOVE_ACTION:
                self._move_mouse(p_action)
            case Command.MOUSE_CLICK_ACTION:
                self._click_mouse_key(p_action)
            case Command.MOUSE_SCROLL_ACTION:
                self._scroll_mouse(p_action)

    def _move_mouse(self, action):
        if self.p_parent.m_config['mouse']:
            self._move_mouse_mouse(action)
        else:
            self._move_mouse_ydotool(action)

    @staticmethod
    def _move_mouse_mouse(p_action):
        if p_action['absolute']:
            _os_mouse.move_to(p_action['x'], p_action['y'])
        else:
            _os_mouse.move_relative(p_action['x'], p_action['y'])

    def _move_mouse_ydotool(self, p_action):
        if p_action['absolute']:
            command = 'mousemove --absolute -x ' + str(p_action['x']) + " -y " + str(p_action['y'])
        else:
            command = 'mousemove -x ' + str(p_action['x']) + " -y " + str(p_action['y'])
        self._execute_ydotool_command(command)

    def _scroll_mouse(self, action):
        if self.p_parent.m_config['mouse']:
            self._scroll_mouse_mouse(action)
        else:
            self._scroll_mouse_ydotool(action)

    @staticmethod
    def _scroll_mouse_mouse(p_action):
        _os_mouse.wheel(int(p_action['delta']))

    def _scroll_mouse_ydotool(self, p_action):
        command = 'mousemove --wheel -x 0 -y ' + str(p_action['delta'])
        self._execute_ydotool_command(command)

    def _click_mouse_key(self, action):
        if self.p_parent.m_config['mouse']:
            self._click_mouse_key_mouse(action)
        else:
            self._click_mouse_key_ydotool(action)

    @staticmethod
    def _click_mouse_key_mouse(p_action):
        w_type = p_action['type']
        w_button = str(p_action['button'])
        match w_type:
            case 1:
                _os_mouse.press(w_button)
            case 0:
                _os_mouse.release(w_button)
            case 10:
                _os_mouse.press(w_button)
                _os_mouse.release(w_button)
            case 11:
                _os_mouse.press(w_button)
                _os_mouse.release(w_button)
                _os_mouse.press(w_button)
                _os_mouse.release(w_button)
            case _:
                print("Unknown mouse type " + w_type + " , skipping")

    def _click_mouse_key_ydotool(self, p_action):
        w_type = p_action['type']
        w_button = p_action['button']
        click_command = '0x'
        match w_type:
            case 1:
                click_command += '4'
            case 0:
                click_command += '8'
            case 10:
                click_command += 'C'
            case 11:
                click_command += 'C'
            case _:
                click_command += '0'

        match w_button:
            case 'left':
                click_command += '0'
            case 'middle':
                click_command += '2'
            case 'right':
                click_command += '1'
            case _:
                click_command += '0'

        args = ""
        if w_type == 11:
            args = "--repeat 2"

        command = 'click ' + args + " --next-delay 25 " + click_command
        self._execute_ydotool_command(command)

    def _execute_ydotool_command(self, command):
        if self.ydotoold is not None:
            os.system('env YDOTOOL_SOCKET=' + YDOTOOLD_SOCKET_PATH + ' ydotool ' + command)
            if self.p_parent.m_config['debug']:
                print('Executed ydotool command: ' + command)
        else:
            print('ydotoold daemon not running')

    class CommandThread(threading.Thread):
        def __init__(self, p_profile_executor, p_actions, p_repeat):
            threading.Thread.__init__(self)
            self.profile_executor = p_profile_executor
            self.m_actions = p_actions
            self.m_repeat = p_repeat
            self.m_stop = False

        def run(self):
            w_repeat = self.m_repeat
            while not self.m_stop and w_repeat > 0:
                for w_action in self.m_actions:
                    self.profile_executor.do_action(w_action)
                w_repeat -= 1

        def stop(self):
            self.m_stop = True
            threading.Thread.join(self)

    def _do_command(self, p_cmd_name):
        w_command = self._get_command_for_executing(p_cmd_name)
        if w_command is None:
            return
        w_actions = w_command['actions']
        w_async = w_command['async']
        if not w_async:
            w_repeat = w_command['repeat']
            w_repeat = max(w_repeat, 1)
            while w_repeat > 0:
                for w_action in w_command['actions']:
                    self.do_action(w_action)
                w_repeat -= 1
        else:
            w_cmd_thread = ProfileExecutor.CommandThread(self, w_actions, w_command['repeat'])
            w_cmd_thread.start()
            self.m_cmd_threads[p_cmd_name] = w_cmd_thread

    def _get_command_for_executing(self, cmd_name):
        if self.m_profile is None:
            return None

        w_commands = self.m_profile['commands']
        command = None
        for w_command in w_commands:
            parts = w_command['name'].split(',')
            for part in parts:
                if part.lower() == cmd_name:
                    command = w_command
                    break

            if command is not None:
                break
        return command

    def _execute_voice_command(self, cmd_name):
        self._do_command(cmd_name)

    def _stop_command(self, p_cmd_name):
        if p_cmd_name in self.m_cmd_threads:
            self.m_cmd_threads[p_cmd_name].stop()
            del self.m_cmd_threads[p_cmd_name]

    def _play_sound(self, p_cmd_name):
        sound_file = (get_voice_packs_folder_path() + p_cmd_name['pack'] + '/' + p_cmd_name['cat'] + '/'
                      + p_cmd_name['file'])
        self.m_sound.play(sound_file)

    def _press_key(self, action):
        if self.p_parent.m_config['keyboard']:
            self._press_key_keyboard(action)
        else:
            self._press_key_ydotool(action)

    def _press_key_ydotool(self, action):
        events = str(action['key_events']).replace(KEYS_SPLITTER, ' ')
        self._execute_ydotool_command('key -d ' + str(action['delay']) + ' ' + events)

    @staticmethod
    def _press_key_keyboard(action):
        events = str(action['key_events']).split(KEYS_SPLITTER)
        for event in events:
            splits = event.split(':')
            code = int(splits[0])
            match splits[1]:
                case '1':
                    _os_keyboard.press(code)
                    time.sleep(int(action['delay']) / 1000)
                case '0':
                    _os_keyboard.release(code)
