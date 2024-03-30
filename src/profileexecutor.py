import json
import os
import re
import threading
import time

import sounddevice
from vosk import Model, KaldiRecognizer


def get_settings_path(setting):
    home = os.path.expanduser("~") + '/.local/share/LinVAM/'
    if not os.path.exists(home):
        os.mkdir(home)
    file = home + setting
    if not os.path.exists(file):
        with (open(file, "w", encoding="utf-8")) as f:
            f.close()
    return file


class ProfileExecutor(threading.Thread):

    def __init__(self, p_profile=None, p_parent=None):

        super().__init__()
        self.m_profile = None
        self.commands_list = []
        # does nothing?
        self.set_profile(p_profile)
        self.m_stop = False
        self.m_listening = False
        self.m_cmd_threads = {}
        self.p_parent = p_parent
        self.samplerate = 16000
        # noinspection PyBroadException
        # pylint: disable=bare-except
        try:
            self.m_stream = sounddevice.RawInputStream(samplerate=self.samplerate, dtype="int16", channels=1,
                                                       blocksize=4000, callback=self.listen_callback)
        except:
            device_info = sounddevice.query_devices('default.device', 'input')
            # soundfile expects an int, sounddevice provides a float:
            self.samplerate = int(device_info['default_samplerate'])
            self.m_stream = sounddevice.RawInputStream(samplerate=self.samplerate, dtype="int16", channels=1,
                                                       blocksize=4000, callback=self.listen_callback)

        self.model = Model(lang='en-us')
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)

        if self.p_parent is not None:
            self.m_sound = self.p_parent.m_sound

    # noinspection PyUnusedLocal
    # pylint: disable=unused-argument
    def listen_callback(self, in_data, frame_count, time_info, status):
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

    def set_profile(self, p_profile):
        self.m_profile = p_profile
        if self.m_profile is None:
            return
        self.commands_list = []
        w_commands = self.m_profile['commands']
        for w_command in w_commands:
            parts = w_command['name'].split(',')
            for part in parts:
                self.commands_list.append(part)
        print(str(self.commands_list))
        with open(get_settings_path("command.list"), 'w', encoding="utf-8") as f:
            json.dump(self.commands_list, f, indent=4)
            f.close()

    def set_enable_listening(self, p_enable):
        if not self.m_listening and p_enable:
            self.m_stream.start()
            self.m_listening = p_enable
            self.m_stop = False
            self.do_listen()
        elif self.m_listening and not p_enable:
            self.stop()

    def do_listen(self):
        print("Detection started")
        self.m_listening = True

    def stop(self):
        if self.m_listening:
            print("Detection stopped")
            self.m_stop = True
            self.m_listening = False
            self.m_stream.stop()
            self.recognizer.FinalResult()

    def shutdown(self):
        self.stop()
        self.m_stream.close()

    def do_action(self, p_action):
        # {'name': 'key action', 'key': 'left', 'type': 0}
        # {'name': 'pause action', 'time': 0.03}
        # {'name': 'command stop action', 'command name': 'down'}
        # {'name': 'mouse move action', 'x':5, 'y':0, 'absolute': False}
        # {'name': 'mouse click action', 'button': 'left', 'type': 0}
        # {'name': 'mouse wheel action', 'delta':10}
        w_action_name = p_action['name']
        if w_action_name == 'key action':
            w_key = p_action['key']
            self.press_key(w_key)
        elif w_action_name == 'pause action':
            print("Sleep ", p_action['time'])
            time.sleep(p_action['time'])
        elif w_action_name == 'command stop action':
            self.stop_command(p_action['command name'])
        elif w_action_name in ['command play sound', 'play sound']:
            self.play_sound(p_action)
        elif w_action_name == 'mouse move action':
            if p_action['absolute']:
                os.system('ydotool mousemove --absolute -x' + str(p_action['x']) + " -y " + str(p_action['y']))
            else:
                os.system('ydotool mousemove -x' + str(p_action['x']) + " -y " + str(p_action['y']))
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

            print("Mouse button command: ", click_command)
            os.system('ydotool click ' + args + " --next-delay 25 " + click_command)
        elif w_action_name == 'mouse scroll action':
            os.system('ydotool mousemove --wheel -x 0 -y' + str(p_action['delta']))

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
        sound_file = './voicepacks/' + p_cmd_name['pack'] + '/' + p_cmd_name['cat'] + '/' + p_cmd_name['file']
        self.m_sound.play(sound_file)

    def press_key(self, w_key):
        # ydotool has a different key mapping.
        # check /usr/include/linux/input-event-codes.h for key mappings
        original_key = w_key
        keys = w_key.split('+')
        commands = ""
        for key in keys:
            commands += self.create_key_event(key) + " "
        if len(commands) < 1:
            print('Commands not recognized, skipping')
            return
        os.system('ydotool key -d 65 ' + commands)
        print("original command: ", original_key)
        print("ydotool converted command: ", commands)

    def create_key_event(self, w_key):
        if "hold" in w_key:
            w_key = re.sub('hold', '', w_key, flags=re.IGNORECASE)
            w_key = self.map_key(w_key.strip())
            if len(w_key) < 1:
                return ''
            return str(w_key) + ":1"

        if "release" in w_key:
            w_key = re.sub('release', '', w_key, flags=re.IGNORECASE)
            w_key = self.map_key(w_key.strip())
            if len(w_key) < 1:
                return ''
            return str(w_key) + ":0"

        w_key = self.map_key(w_key.strip())
        if len(w_key) < 1:
            return ''
        return str(w_key) + ":1 " + str(w_key) + ":0"

    # pylint: disable=too-many-return-statements
    @staticmethod
    def map_key(w_key):
        match w_key.casefold():
            case 'left ctrl':
                return '29'
            case 'right ctrl':
                return '97'
            case 'left shift':
                return '42'
            case 'right shift':
                return '54'
            case 'left alt':
                return '56'
            case 'right alt':
                return '100'
            case 'left windows':
                return '125'
            case 'right windows':
                return '126'
            case 'left super':
                return '125'
            case 'right super':
                return '126'
            case 'left meta':
                return '125'
            case 'right meta':
                return '126'
            case 'tab':
                return '15'
            case 'esc':
                return '1'
            case 'left':
                return '105'
            case 'right':
                return '106'
            case 'up':
                return '103'
            case 'down':
                return '108'
            case 'insert':
                return '110'
            case 'delete':
                return '111'
            case 'home':
                return '102'
            case 'end':
                return '107'
            case 'pageup':
                return '104'
            case 'pagedown':
                return '109'
            case 'return':
                return '28'
            case 'enter':
                return '28'
            case 'backspace':
                return '14'
            case '1':
                return '2'
            case '2':
                return '3'
            case '3':
                return '4'
            case '4':
                return '5'
            case '5':
                return '6'
            case '6':
                return '7'
            case '7':
                return '8'
            case '8':
                return '9'
            case '9':
                return '10'
            case '0':
                return '11'
            case '-':
                return '12'
            case '=':
                return '13'
            case 'q':
                return '16'
            case 'w':
                return '17'
            case 'e':
                return '18'
            case 'r':
                return '19'
            case 't':
                return '20'
            case 'y':
                return '21'
            case 'u':
                return '22'
            case 'i':
                return '23'
            case 'o':
                return '24'
            case 'p':
                return '25'
            case 'left bracket':
                return '26'
            case 'right bracket':
                return '27'
            case 'a':
                return '30'
            case 's':
                return '31'
            case 'd':
                return '32'
            case 'f':
                return '33'
            case 'g':
                return '34'
            case 'h':
                return '35'
            case 'j':
                return '36'
            case 'k':
                return '37'
            case 'l':
                return '38'
            case ';':
                return '39'
            case '\'':
                return '40'
            case 'backslash':
                return '43'
            case 'z':
                return '44'
            case 'x':
                return '45'
            case 'c':
                return '46'
            case 'v':
                return '47'
            case 'b':
                return '48'
            case 'n':
                return '49'
            case 'm':
                return '50'
            case ',':
                return '51'
            case '.':
                return '52'
            case 'forwardslash':
                return '53'
            case 'space':
                return '57'
            case 'capslock':
                return '58'
            case 'f1':
                return '59'
            case 'f2':
                return '60'
            case 'f3':
                return '61'
            case 'f4':
                return '62'
            case 'f5':
                return '63'
            case 'f6':
                return '64'
            case 'f7':
                return '65'
            case 'f8':
                return '66'
            case 'f9':
                return '67'
            case 'f10':
                return '68'
            case 'f11':
                return '87'
            case 'f12':
                return '88'
            case 'scrolllock':
                return '70'
            case 'numlock':
                return '69'
            case 'n7':  # Num 7
                return '71'
            case 'n8':  # Num 8
                return '72'
            case 'n9':  # Num 9
                return '73'
            case 'n-':  # Num -
                return '74'
            case 'n4':  # Num 4
                return '75'
            case 'n5':  # Num 5
                return '76'
            case 'n6':  # Num 6
                return '77'
            case 'nplus':  # Num +
                return '78'
            case 'n1':  # Num 1
                return '79'
            case 'n2':  # Num 2
                return '80'
            case 'n3':  # Num 3
                return '81'
            case 'n0':  # Num 0
                return '82'
            case 'ndot':  # Num .
                return '83'
            case _:
                return ''