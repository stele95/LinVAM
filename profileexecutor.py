import keyboard
from pynput.mouse import Button, Controller
import time
import threading
import os, pyaudio
import shutil
import re
from pocketsphinx import *
from soundfiles import SoundFiles


class ProfileExecutor(threading.Thread):
    mouse = Controller()

    def __init__(self, p_profile = None, p_parent = None):
        # threading.Thread.__init__(self)

        # does nothing?
        self.setProfile(p_profile)
        self.m_stop = False
        self.m_listening = False
        self.m_cmdThreads = {}

        self.m_config = Config(
            hmm=os.path.join('model', 'en-us/en-us'),
            dict=os.path.join('model', 'en-us/cmudict-en-us.dict'),
            kws='command.list',
            logfn='/dev/null'
        )

        self.m_pyaudio = pyaudio.PyAudio()

        try:
            self.m_stream = self.m_pyaudio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)
        except:
            samplerate = int(self.m_pyaudio.get_device_info_by_index(0).get('defaultSampleRate'))
            self.m_stream = self.m_pyaudio.open(format=pyaudio.paInt16, channels=1, rate=samplerate, input=True)

        # Process audio chunk by chunk. On keyword detected perform action and restart search
        self.m_decoder = Decoder(self.m_config)

        self.m_thread = False

        self.p_parent = p_parent
        if not self.p_parent == None:
            self.m_sound = self.p_parent.m_sound


    def getSettingsPath(self, setting):
        home = os.path.expanduser("~") + '/.linvam/'
        if not os.path.exists(home):
            os.mkdir(home)
        if not os.path.exists(home + setting):
            shutil.copyfile(setting, home + setting)

        return home + setting

    def setProfile(self, p_profile):
        #print("setProfile")
        self.m_profile = p_profile
        if self.m_profile == None:
            return
        #print ("writing command list")
        w_commandWordFile = open(self.getSettingsPath('command.list'), 'w')
        w_commands = self.m_profile['commands']
        for w_command in w_commands:
            parts = w_command['name'].split(',')
            for part in parts:
                w_commandWordFile.write(part.lower() + ' /1e-%d/' % w_command['threshold'] + '\n')
        w_commandWordFile.close()
        self.m_config.set_string('-kws', self.getSettingsPath('command.list'))
        # load new command list into decoder and restart it
        if self.m_listening == True:
            self.stop()
            self.m_stream.start_stream()
            # a self.m_decoder.reinit(self.config) will segfault?
            self.m_decoder = Decoder(self.m_config)
            self.m_stop = False
            self.m_thread = threading.Thread(target=self.doListen, args=())
            self.m_thread.start()
        else:
            self.m_decoder.reinit(self.m_config)

    def setEnableListening(self, p_enable):
        if self.m_listening == False and p_enable == True:
            self.m_stream.start_stream()
            self.m_listening = p_enable
            self.m_stop = False
            self.m_thread = threading.Thread(target=self.doListen, args=())
            self.m_thread.start()
        elif self.m_listening == True and p_enable == False:
            self.stop()

    def doListen(self):
        print("Detection started")
        self.m_listening = True
        self.m_decoder.start_utt()
        while self.m_stop != True:
            buf = self.m_stream.read(1024)

            self.m_decoder.process_raw(buf, False, False)

            if self.m_decoder.hyp() != None:
                #print([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in self.m_decoder.seg()])
                #print("Detected keyword, restarting search")

                # hack :)
                for seg in self.m_decoder.seg():
                    print("Detected: ",seg.word)
                    break

                #
                # Here you run the code you want based on keyword
                #
                for w_seg in self.m_decoder.seg():
                    self.doCommand(w_seg.word.rstrip())

                self.m_decoder.end_utt()
                self.m_decoder.start_utt()

   # def run(self):

    def stop(self):
        if self.m_listening == True:
            self.m_stop = True
            self.m_listening = False
            self.m_decoder.end_utt()
            self.m_thread.join()
            self.m_stream.stop_stream()

    def shutdown(self):
        self.stop()
        self.m_stream.close()
        self.m_pyaudio.terminate()


    def doAction(self, p_action):
        # {'name': 'key action', 'key': 'left', 'type': 0}
        # {'name': 'pause action', 'time': 0.03}
        # {'name': 'command stop action', 'command name': 'down'}
        # {'name': 'mouse move action', 'x':5, 'y':0, 'absolute': False}
        # {'name': 'mouse click action', 'button': 'left', 'type': 0}
        # {'name': 'mouse wheel action', 'delta':10}
        w_actionName = p_action['name']
        if w_actionName == 'key action':
            w_key = p_action['key']
            self.pressKey(w_key)
        elif w_actionName == 'pause action':
            print("Sleep ", p_action['time'])
            time.sleep(p_action['time'])
        elif w_actionName == 'command stop action':
            self.stopCommand(p_action['command name'])
        elif w_actionName == 'command play sound' or w_actionName == 'play sound':
            self.playSound(p_action)
        elif w_actionName == 'mouse move action':
            if p_action['absolute']:
                ProfileExecutor.mouse.position([p_action['x'], p_action['y']])
            else:
                ProfileExecutor.mouse.move(p_action['x'], p_action['y'])
        elif w_actionName == 'mouse click action':
            w_type = p_action['type']
            w_button = p_action['button']
            if w_type == 1:
                if w_button == 'left':
                    ProfileExecutor.mouse.press(Button.left)
                elif w_button == 'middle':
                    ProfileExecutor.mouse.press(Button.middle)
                elif w_button == 'right':
                    ProfileExecutor.mouse.press(Button.right)
                print("pressed mouse button: ", w_button)
            elif w_type == 0:
                if w_button == 'left':
                    ProfileExecutor.mouse.release(Button.left)
                elif w_button == 'middle':
                    ProfileExecutor.mouse.release(Button.middle)
                elif w_button == 'right':
                    ProfileExecutor.mouse.release(Button.right)
                print("released mouse button: ", w_button)
            elif w_type == 10:
                if w_button == 'left':
                    ProfileExecutor.mouse.click(Button.left)
                elif w_button == 'middle':
                    ProfileExecutor.mouse.click(Button.middle)
                elif w_button == 'right':
                    ProfileExecutor.mouse.click(Button.right)
                print("pressed and released mouse button: ", w_button)
        elif w_actionName == 'mouse scroll action':
            ProfileExecutor.mouse.scroll(0, p_action['delta'])

    class CommandThread(threading.Thread):
        def __init__(self, p_ProfileExecutor, p_actions, p_repeat):
            threading.Thread.__init__(self)
            self.ProfileExecutor = p_ProfileExecutor
            self.m_actions = p_actions
            self.m_repeat = p_repeat
            self.m_stop = False
        def run(self):
            w_repeat = self.m_repeat
            while self.m_stop != True:
                for w_action in self.m_actions:
                    self.ProfileExecutor.doAction(w_action)
                w_repeat = w_repeat - 1
                if w_repeat == 0:
                    break

        def stop(self):
            self.m_stop = True
            threading.Thread.join(self)

    def doCommand(self, p_cmdName):
        if self.m_profile == None:
            return

        w_commands = self.m_profile['commands']
        flag = False
        for w_command in w_commands:
            parts = w_command['name'].split(',')
            for part in parts:
                if part.lower() == p_cmdName:
                    flag = True
                    break
            if flag == True:
                break

        if flag == False:
            return

        w_actions = w_command['actions']
        w_async = w_command['async']

        if w_async == False:
            w_repeat = w_command['repeat']
            if w_repeat < 1:
                w_repeat = 1
            while True:
                for w_action in w_command['actions']:
                    self.doAction(w_action)
                w_repeat = w_repeat - 1
                if w_repeat == 0:
                    break
        else:
            w_cmdThread = ProfileExecutor.CommandThread(self, w_actions, w_command['repeat'])
            w_cmdThread.start()
            self.m_cmdThreads[p_cmdName] = w_cmdThread

    def stopCommand(self, p_cmdName):
        if p_cmdName in self.m_cmdThreads.keys():
            self.m_cmdThreads[p_cmdName].stop()
            del self.m_cmdThreads[p_cmdName]

    def playSound(self, p_cmdName):
        sound_file = './voicepacks/' + p_cmdName['pack'] + '/' + p_cmdName['cat'] + '/' + p_cmdName['file']
        self.m_sound.play(sound_file)


    def pressKey(self, w_key):
        #if self.p_parent.m_config['noroot'] == 1:
            # ydotool has a different key mapping.
            # check /usr/include/linux/input-event-codes.h for key mappings
            original_key = w_key
            keys = w_key.split('+')
            commands = ""
            for key in keys:
                commands += self.createKeyEvent(key) + " "
            os.system('ydotool key -d 75 ' + commands)
            print("original command: ", original_key)
            print("ydotool converted command: ", commands)

    def createKeyEvent(self, w_key):
        if "hold" in w_key:
            w_key = re.sub('hold', '', w_key, flags=re.IGNORECASE)
            w_key = self.mapKey(w_key.strip())
            return str(w_key) + ":1"
        elif "release" in w_key:
            w_key = re.sub('release', '', w_key, flags=re.IGNORECASE)
            w_key = self.mapKey(w_key.strip())
            return str(w_key) + ":0"
        else:
            w_key = self.mapKey(w_key.strip())
            return str(w_key) + ":1 " + str(w_key) + ":0"

    def mapKey(self, w_key):
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
            case 'n7': # Num 7
                return '71'
            case 'n8': # Num 8
                return '72'
            case 'n9': # Num 9
                return '73'
            case 'n-': # Num -
                return '74'
            case 'n4': # Num 4
                return '75'
            case 'n5': # Num 5
                return '76'
            case 'n6': # Num 6
                return '77'
            case 'nplus': # Num +
                return '78'
            case 'n1': # Num 1
                return '79'
            case 'n2': # Num 2
                return '80'
            case 'n3': # Num 3
                return '81'
            case 'n0': # Num 0
                return '82'
            case 'ndot': # Num .
                return '83'
            case _:
                return w_key
