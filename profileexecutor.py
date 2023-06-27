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
        self.m_stream = self.m_pyaudio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)

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
            w_type = p_action['type']
            self.pressKey(w_key, w_type)
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
                    print(part)
                    flag = True
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


    def pressKey(self, w_key, w_type):
        if self.p_parent.m_config['noroot'] == 1:
            # xdotool has a different key mapping. translate old existing mappings of special keys
            # use this to find key name: xev -event keyboard
            w_key = re.sub('left ctrl', 'Control_L', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right ctrl', 'Control_R', w_key, flags=re.IGNORECASE)
            w_key = re.sub('left shift', 'Shift_L', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right shift', 'Shift_R', w_key, flags=re.IGNORECASE)
            w_key = re.sub('left alt', 'Alt_L', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right alt', 'Alt_R', w_key, flags=re.IGNORECASE)
            w_key = re.sub('left windows', 'Super_L', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right windows', 'Super_R', w_key, flags=re.IGNORECASE)
            w_key = re.sub('tab', 'Tab', w_key, flags=re.IGNORECASE)
            w_key = re.sub('esc', 'Escape', w_key, flags=re.IGNORECASE)

            w_key = re.sub('left', 'Left', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right', 'Right', w_key, flags=re.IGNORECASE)
            w_key = re.sub('up', 'Up', w_key, flags=re.IGNORECASE)
            w_key = re.sub('down', 'Down', w_key, flags=re.IGNORECASE)

            w_key = re.sub('ins$', 'Insert', w_key, flags=re.IGNORECASE)
            w_key = re.sub('del$', 'Delete', w_key, flags=re.IGNORECASE)
            w_key = re.sub('home', 'Home', w_key, flags=re.IGNORECASE)
            w_key = re.sub('end', 'End', w_key, flags=re.IGNORECASE)
            w_key = re.sub('Page\s?up', 'Prior', w_key, flags=re.IGNORECASE)
            w_key = re.sub('Page\s?down', 'Next', w_key, flags=re.IGNORECASE)
            w_key = re.sub('return', 'Return', w_key, flags=re.IGNORECASE)
            w_key = re.sub('enter', 'Return', w_key, flags=re.IGNORECASE)
            w_key = re.sub('backspace', 'BackSpace', w_key, flags=re.IGNORECASE)

            w_key = w_key.replace('insert', 'Insert')
            w_key = w_key.replace('delete', 'Delete')

            window_cmd = ""
            if not self.p_parent.m_config['xdowindowid'] == None:
                window_cmd = " windowactivate --sync " + str(self.p_parent.m_config['xdowindowid'])

            if w_type == 1:
                os.system('xdotool ' + window_cmd + ' keydown ' + str(w_key) )
                print("pressed key: ", w_key)
            elif w_type == 0:
                os.system('xdotool' + window_cmd + ' keyup ' + str(w_key))
                print("released key: ", w_key)
            elif w_type == 10:
                os.system('xdotool' + window_cmd + ' key ' + str(w_key))
                print("pressed and released key: ", w_key)
        else:
            if w_type == 1:
                keyboard.press(w_key)
                print("pressed key: ", w_key)
            elif w_type == 0:
                keyboard.release(w_key)
                print("released key: ", w_key)
            elif w_type == 10:
                keyboard.press(w_key)
                keyboard.release(w_key)
                print("pressed and released key: ", w_key)