import json
import os
import shlex
import signal
import subprocess
import threading
import time

import sounddevice
from vosk import Model, KaldiRecognizer

from util import (get_language_code, get_voice_packs_folder_path, get_language_name, YDOTOOLD_SOCKET_PATH,
                  KEYS_SPLITTER, save_to_commands_file)


class ProfileExecutor(threading.Thread):

    def __init__(self, p_parent=None):

        super().__init__()
        self.m_profile = None
        self.commands_list = []
        self.m_cmd_threads = {}
        self.p_parent = p_parent
        self.ydotoold = None
        self.start_ydotoold()

        self.m_stream = None

        device_info = sounddevice.query_devices(kind='input')
        # sounddevice expects an int, sounddevice provides a float:
        self.samplerate = int(device_info['default_samplerate'])

        self.recognizer = None

        if self.p_parent is not None:
            self.m_sound = self.p_parent.m_sound

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
        if self.recognizer is None:
            return
        if self.recognizer.AcceptWaveform(bytes(in_data)):
            result = self.recognizer.Result()
        else:
            result = self.recognizer.PartialResult()
        result_json = json.loads(result)
        try:
            result_string = result_json['partial']
        except KeyError:
            return
            # result_string = result_json['text']

        if result_string == '':
            return

        for command in self.commands_list:
            if command in result_string:
                self.recognizer.Result()
                print('Detected: ' + command)
                self.do_command(command)
                break

    def set_language(self, language):
        listening = self.m_stream is not None
        self.stop()
        language_code = get_language_code(language)
        if language_code is None:
            print('Unsupported language: ' + language)
            return
        print('Language: ' + get_language_name(language))
        self.recognizer = KaldiRecognizer(Model(lang=language_code), self.samplerate)
        if listening:
            self.start_stream()

    def start_stream(self):
        if self.recognizer is None:
            return
        self.m_stream = sounddevice.RawInputStream(samplerate=self.samplerate, dtype="int16", channels=1,
                                                   blocksize=4000, callback=self.listen_callback)
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

    def set_enable_listening(self, p_enable):
        if self.recognizer is None:
            return
        if self.m_stream is None and p_enable:
            self.start_stream()
            print("Detection started")
        elif self.m_stream is not None and not p_enable:
            self.stop()

    def stop(self):
        if self.m_stream is not None:
            print("Detection stopped")
            self.m_stream.stop()
            self.m_stream.close()
            self.m_stream = None
            self.recognizer.FinalResult()

    def shutdown(self):
        self.m_sound.stop()
        self.stop()
        if self.ydotoold is not None:
            try:
                os.kill(self.ydotoold.pid, signal.SIGKILL)
                self.ydotoold = None
            except OSError:
                pass

    def do_action(self, p_action):
        # {'name': 'key action', 'key': 'left', 'type': 0}
        # {'name': 'pause action', 'time': 0.03}
        # {'name': 'command stop action', 'command name': 'down'}
        # {'name': 'mouse move action', 'x':5, 'y':0, 'absolute': False}
        # {'name': 'mouse click action', 'button': 'left', 'type': 0}
        # {'name': 'mouse wheel action', 'delta':10}
        w_action_name = p_action['name']
        if w_action_name == 'key action':
            self.press_key(p_action)
        elif w_action_name == 'pause action':
            print("Sleep ", p_action['time'])
            time.sleep(p_action['time'])
        elif w_action_name == 'command stop action':
            self.stop_command(p_action['command name'])
        elif w_action_name in ['command play sound', 'play sound']:
            self.play_sound(p_action)
        elif w_action_name == 'stop sound':
            self.m_sound.stop()
        elif w_action_name == 'mouse move action':
            if p_action['absolute']:
                command = 'mousemove --absolute -x' + str(p_action['x']) + " -y " + str(p_action['y'])
            else:
                command = 'mousemove -x' + str(p_action['x']) + " -y " + str(p_action['y'])
            self.execute_ydotool_command(command)
        elif w_action_name == 'mouse click action':
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
            self.execute_ydotool_command(command)
        elif w_action_name == 'mouse scroll action':
            command = 'mousemove --wheel -x 0 -y' + str(p_action['delta'])
            self.execute_ydotool_command(command)

    def execute_ydotool_command(self, command):
        if self.ydotoold is not None:
            os.system('env YDOTOOL_SOCKET=' + YDOTOOLD_SOCKET_PATH + ' ydotool ' + command)
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

    def do_command(self, p_cmd_name):
        w_command = self.get_command_for_executing(p_cmd_name)
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

    def get_command_for_executing(self, cmd_name):
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

    def stop_command(self, p_cmd_name):
        if p_cmd_name in self.m_cmd_threads:
            self.m_cmd_threads[p_cmd_name].stop()
            del self.m_cmd_threads[p_cmd_name]

    def play_sound(self, p_cmd_name):
        sound_file = (get_voice_packs_folder_path() + p_cmd_name['pack'] + '/' + p_cmd_name['cat'] + '/'
                      + p_cmd_name['file'])
        self.m_sound.play(sound_file)

    def press_key(self, action):
        print("Command: ", action['key'])
        events = str(action['key_events']).replace(KEYS_SPLITTER, ' ')
        self.execute_ydotool_command('key -d ' + str(action['delay']) + ' ' + events)
