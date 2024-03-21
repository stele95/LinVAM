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


    def pressKey(self, w_key, w_type):
        if self.p_parent.m_config['noroot'] == 1:
            # ydotool has a different key mapping.
            # check /usr/include/linux/input-event-codes.h for key mappings
            original_key = w_key
            w_key = re.sub('left ctrl', '29', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right ctrl', '97', w_key, flags=re.IGNORECASE)
            w_key = re.sub('left shift', '42', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right shift', '54', w_key, flags=re.IGNORECASE)
            w_key = re.sub('left alt', '56', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right alt', '100', w_key, flags=re.IGNORECASE)
            w_key = re.sub('left windows', '125', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right windows', '126', w_key, flags=re.IGNORECASE)
            w_key = re.sub('tab', '15', w_key, flags=re.IGNORECASE)
            w_key = re.sub('esc', '1', w_key, flags=re.IGNORECASE)

            w_key = re.sub('left', '105', w_key, flags=re.IGNORECASE)
            w_key = re.sub('right', '106', w_key, flags=re.IGNORECASE)
            w_key = re.sub('up', '103', w_key, flags=re.IGNORECASE)
            w_key = re.sub('down', '108', w_key, flags=re.IGNORECASE)

            w_key = re.sub('ins$', '110', w_key, flags=re.IGNORECASE)
            w_key = re.sub('del$', '111', w_key, flags=re.IGNORECASE)
            w_key = re.sub('home', '102', w_key, flags=re.IGNORECASE)
            w_key = re.sub('end', '107', w_key, flags=re.IGNORECASE)
            w_key = re.sub('Page\s?up', '104', w_key, flags=re.IGNORECASE)
            w_key = re.sub('Page\s?down', '109', w_key, flags=re.IGNORECASE)
            w_key = re.sub('return', '28', w_key, flags=re.IGNORECASE)
            w_key = re.sub('enter', '28', w_key, flags=re.IGNORECASE)
            w_key = re.sub('backspace', '14', w_key, flags=re.IGNORECASE)

            w_key = re.sub('1', '2', w_key, flags=re.IGNORECASE)
            w_key = re.sub('2', '3', w_key, flags=re.IGNORECASE)
            w_key = re.sub('3', '4', w_key, flags=re.IGNORECASE)
            w_key = re.sub('4', '5', w_key, flags=re.IGNORECASE)
            w_key = re.sub('5', '6', w_key, flags=re.IGNORECASE)
            w_key = re.sub('6', '7', w_key, flags=re.IGNORECASE)
            w_key = re.sub('7', '8', w_key, flags=re.IGNORECASE)
            w_key = re.sub('8', '9', w_key, flags=re.IGNORECASE)
            w_key = re.sub('9', '10', w_key, flags=re.IGNORECASE)
            w_key = re.sub('0', '11', w_key, flags=re.IGNORECASE)
            w_key = re.sub('-', '12', w_key, flags=re.IGNORECASE)
            w_key = re.sub('=', '13', w_key, flags=re.IGNORECASE)
            w_key = re.sub('q', '16', w_key, flags=re.IGNORECASE)
            w_key = re.sub('w', '17', w_key, flags=re.IGNORECASE)
            w_key = re.sub('e', '18', w_key, flags=re.IGNORECASE)
            w_key = re.sub('r', '19', w_key, flags=re.IGNORECASE)
            w_key = re.sub('t', '20', w_key, flags=re.IGNORECASE)
            w_key = re.sub('y', '21', w_key, flags=re.IGNORECASE)
            w_key = re.sub('u', '22', w_key, flags=re.IGNORECASE)
            w_key = re.sub('i', '23', w_key, flags=re.IGNORECASE)
            w_key = re.sub('o', '24', w_key, flags=re.IGNORECASE)
            w_key = re.sub('p', '25', w_key, flags=re.IGNORECASE)
            w_key = re.sub('[', '26', w_key, flags=re.IGNORECASE)
            w_key = re.sub(']', '27', w_key, flags=re.IGNORECASE)
            w_key = re.sub('a', '30', w_key, flags=re.IGNORECASE)
            w_key = re.sub('s', '31', w_key, flags=re.IGNORECASE)
            w_key = re.sub('d', '32', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f', '33', w_key, flags=re.IGNORECASE)
            w_key = re.sub('g', '34', w_key, flags=re.IGNORECASE)
            w_key = re.sub('h', '35', w_key, flags=re.IGNORECASE)
            w_key = re.sub('j', '36', w_key, flags=re.IGNORECASE)
            w_key = re.sub('k', '37', w_key, flags=re.IGNORECASE)
            w_key = re.sub('l', '38', w_key, flags=re.IGNORECASE)
            w_key = re.sub(';', '39', w_key, flags=re.IGNORECASE)
            w_key = re.sub('\'', '40', w_key, flags=re.IGNORECASE)
            w_key = re.sub('\\', '43', w_key, flags=re.IGNORECASE)
            w_key = re.sub('z', '44', w_key, flags=re.IGNORECASE)
            w_key = re.sub('x', '45', w_key, flags=re.IGNORECASE)
            w_key = re.sub('c', '46', w_key, flags=re.IGNORECASE)
            w_key = re.sub('v', '47', w_key, flags=re.IGNORECASE)
            w_key = re.sub('b', '48', w_key, flags=re.IGNORECASE)
            w_key = re.sub('n', '49', w_key, flags=re.IGNORECASE)
            w_key = re.sub('m', '50', w_key, flags=re.IGNORECASE)
            w_key = re.sub(',', '51', w_key, flags=re.IGNORECASE)
            w_key = re.sub('.', '52', w_key, flags=re.IGNORECASE)
            w_key = re.sub('/', '53', w_key, flags=re.IGNORECASE)
            w_key = re.sub('space', '57', w_key, flags=re.IGNORECASE)
            w_key = re.sub('capslock', '58', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f1', '59', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f2', '60', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f3', '61', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f4', '62', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f5', '63', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f6', '64', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f7', '65', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f8', '66', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f9', '67', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f10', '68', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f11', '87', w_key, flags=re.IGNORECASE)
            w_key = re.sub('f12', '88', w_key, flags=re.IGNORECASE)
            w_key = re.sub('scrolllock', '70', w_key, flags=re.IGNORECASE)
            w_key = re.sub('numlock', '69', w_key, flags=re.IGNORECASE)
            w_key = re.sub('n7', '71', w_key, flags=re.IGNORECASE) # Num 7
            w_key = re.sub('n8', '72', w_key, flags=re.IGNORECASE) # Num 8
            w_key = re.sub('n9', '73', w_key, flags=re.IGNORECASE) # Num 9
            w_key = re.sub('n-', '74', w_key, flags=re.IGNORECASE) # Num -
            w_key = re.sub('n4', '75', w_key, flags=re.IGNORECASE) # Num 4
            w_key = re.sub('n5', '76', w_key, flags=re.IGNORECASE) # Num 5
            w_key = re.sub('n6', '77', w_key, flags=re.IGNORECASE) # Num 6
            w_key = re.sub('n+', '78', w_key, flags=re.IGNORECASE) # Num +
            w_key = re.sub('n1', '79', w_key, flags=re.IGNORECASE) # Num 1
            w_key = re.sub('n2', '80', w_key, flags=re.IGNORECASE) # Num 2
            w_key = re.sub('n3', '81', w_key, flags=re.IGNORECASE) # Num 3
            w_key = re.sub('n0', '82', w_key, flags=re.IGNORECASE) # Num 0
            w_key = re.sub('n.', '83', w_key, flags=re.IGNORECASE) # Num .

            w_key = w_key.replace('insert', '110')
            w_key = w_key.replace('delete', '111')

            if w_type == 1:
                os.system('ydotool key ' + str(w_key) + ':1')
                print("ydotool pressed key: ", original_key)
            elif w_type == 0:
                os.system('ydotool key ' + str(w_key) + ':0')
                print("ydotool released key: ", original_key)
            elif w_type == 10:
                os.system('ydotool key ' + str(w_key) + ':1 ' + str(w_key) + ':0')
                print("ydotool pressed and released key: ", original_key)
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
