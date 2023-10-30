# original: https://github.com/Seconb/Arsenal-Colorbot

import winsound
import cv2
import numpy as np
from os import path, system
from urllib.request import urlopen
from mss import mss
from keyboard import is_pressed
from configparser import ConfigParser
from win32api import GetAsyncKeyState
from colorama import Fore, Style
from ctypes import windll
from time import sleep
from threading import Thread

CURRENT_VERSION = "v1.2" # IMPORTANT !!!!!! CHANGE lmfao

system("title Colorbot")

if urlopen("https://raw.githubusercontent.com/AndrewDarkyy/Colorbot-Modded/main/version.txt").read().decode('utf-8')!=CURRENT_VERSION+"\n":
    print(Style.BRIGHT + Fore.CYAN + "This version is outdated, please get the latest one at " + Fore.YELLOW + "https://github.com/AndrewDarkyy/Colorbot-Modded/releases" + Style.RESET_ALL)
    while True:
        pass

switchmodes = ("Hold", "Toggle")

sdir = path.dirname(path.abspath(__file__))

config = ConfigParser()
config.optionxform = str
config.read(path.join(sdir, "config.ini"))

def loadsettings():
    global A1M_KEY, SWITCH_MODE_KEY, TRIGGERBOT_KEY
    global FOV_KEY_UP, FOV_KEY_DOWN, CAM_FOV
    global A1M_OFFSET_Y, A1M_OFFSET_X, A1M_SPEED_X, A1M_SPEED_Y
    global upper, lower, A1M_FOV

    A1M_KEY_STRING = config.get("Config", "A1M_KEY")
    if A1M_KEY_STRING == "win32con.VK_XBUTTON2" or A1M_KEY_STRING == "VK_XBUTTON2":
        A1M_KEY = 0x02
    elif A1M_KEY_STRING == "win32con.XBUTTON1" or A1M_KEY_STRING == "XBUTTON1":
        A1M_KEY = 0x01
    else:
        try:
            is_pressed(A1M_KEY_STRING)
        except:
            print("Please change A1M_KEY to an existing key.")
            while True:
                sleep(0.1) # omggg check if key exists so just, just amazing
                try:
                    new_config = ConfigParser()
                    new_config.optionxform = str
                    new_config.read(path.join(sdir, "config.ini"))
                    is_pressed(new_config.get("Config", "A1M_KEY"))
                    A1M_KEY_STRING = new_config.get("Config", "A1M_KEY")
                    break
                except:
                    pass
        A1M_KEY = A1M_KEY_STRING
    TRIGGERBOT_KEY_STRING = config.get("Config", "TRIGGERBOT_KEY")
    if TRIGGERBOT_KEY_STRING == "win32con.VK_XBUTTON2" or TRIGGERBOT_KEY_STRING == "VK_XBUTTON2":
        TRIGGERBOT_KEY = 0x02
    elif TRIGGERBOT_KEY_STRING == "win32con.XBUTTON1" or TRIGGERBOT_KEY_STRING == "XBUTTON1":
        TRIGGERBOT_KEY = 0x01
    else:
        try:
            is_pressed(TRIGGERBOT_KEY_STRING)
        except:
            print("Please change TRIGGERBOT_KEY to an existing key.")
            while True:
                sleep(0.1)
                try:
                    new_config = ConfigParser()
                    new_config.optionxform = str
                    new_config.read(path.join(sdir, "config.ini"))
                    is_pressed(new_config.get("Config", "TRIGGERBOT_KEY"))
                    TRIGGERBOT_KEY_STRING = new_config.get("Config", "TRIGGERBOT_KEY")
                    break
                except:
                    pass
        TRIGGERBOT_KEY = TRIGGERBOT_KEY_STRING
    SWITCH_MODE_KEY = config.get("Config", "SWITCH_MODE_KEY")
    FOV_KEY_UP = config.get("Config", "FOV_KEY_UP")
    FOV_KEY_DOWN = config.get("Config", "FOV_KEY_DOWN")
    CAM_FOV = int(config.get("Config", "CAM_FOV"))
    A1M_FOV = int(config.get("Config", "A1M_FOV"))
    A1M_OFFSET_Y = int(config.get("Config", "A1M_OFFSET_Y"))
    A1M_OFFSET_X = int(config.get("Config", "A1M_OFFSET_X"))
    A1M_SPEED_X = float(config.get("Config", "A1M_SPEED_X"))
    A1M_SPEED_Y = float(config.get("Config", "A1M_SPEED_Y"))
    upper = np.array((38, 255, 203), dtype="uint8")
    lower = np.array((30, 255, 201), dtype="uint8")

try:
    loadsettings()
except Exception as e:
    print("Error loading settings:", e)

sct = mss()

center = CAM_FOV / 2

screenshot = sct.monitors[1]
screenshot["left"] = int((screenshot["width"] / 2) - center)
screenshot["top"] = int((screenshot["height"] / 2) - center)
screenshot["width"] = CAM_FOV
screenshot["height"] = CAM_FOV

audiodir = path.join(sdir, "audios")

def audio(wavname):
    audiopath = path.join(audiodir, wavname)
    winsound.PlaySound(audiopath, winsound.SND_FILENAME | winsound.SND_ASYNC)

class colorbot:
    def __init__(self):
        self.aimtoggled = False
        self.triggerbot = True
        self.clicks = 0
        self.switchmode = 0

    def stop(self):
        oldclicks = self.clicks
        sleep(.05)
        if self.clicks == oldclicks:
            windll.user32.mouse_event(0x0004)

    def process(self):
        img = np.array(sct.grab(screenshot))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        dilated = cv2.dilate(cv2.inRange(hsv, lower, upper), np.ones((3, 3), np.uint8), iterations=5)
        thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]
        (contours, hierarchy) = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # cv2.imshow("Colorbot" ,img)
        # cv2.setWindowProperty("Colorbot", cv2.WND_PROP_TOPMOST, 1)
        # cv2.waitKey(100)
        if len(contours) != 0:
            contour = max(contours, key=cv2.contourArea)
            topmost = tuple(contour[contour[:, :, 1].argmin()][0])
            x = topmost[0] - center + A1M_OFFSET_X
            y = topmost[1] - center + A1M_OFFSET_Y
            distance = np.sqrt(x**2 + y**2)
            if distance <= A1M_FOV:
                windll.user32.mouse_event(0x0001, int(x * A1M_SPEED_X), int(y * A1M_SPEED_Y), 0, 0)
            if self.triggerbot and distance <= 13:
                windll.user32.mouse_event(0x0002)
                self.clicks += 1
                Thread(target = self.stop).start()

    def a1mtoggle(self):
        self.aimtoggled = not self.aimtoggled
        sleep(.1)
    
    def triggerbotswitch(self):
        self.triggerbot = not self.triggerbot
        sleep(.1)

    def modeswitch(self):
        if self.switchmode == 0:
            self.switchmode = 1
            audio("toggle.wav")
        elif self.switchmode == 1:
            self.switchmode = 0
            audio("hold.wav")
        sleep(.1)

def print_banner(bot: colorbot):
    system("cls")
    print(Style.BRIGHT + Fore.CYAN + "Colorbot for Arsenal!" + Style.RESET_ALL)
    print("====== Controls ======")
    if A1M_KEY == 0x02:
        print("Aimbot Keybind      :", Fore.YELLOW + "RightClick" + Style.RESET_ALL)
    elif A1M_KEY == 0x01:
        print("Aimbot Keybind      :", Fore.YELLOW + "LeftClick" + Style.RESET_ALL)
    else:
        print("Aimbot Keybind      :", Fore.YELLOW + str(A1M_KEY) + Style.RESET_ALL)
    if TRIGGERBOT_KEY == 0x02:
        print("Triggerbot Switch   :", Fore.YELLOW + "RightClick" + Style.RESET_ALL)
    elif TRIGGERBOT_KEY == 0x01:
        print("Triggerbot Switch   :", Fore.YELLOW + "LeftClick" + Style.RESET_ALL)
    else:
        print("Triggerbot Switch   :", Fore.YELLOW + str(TRIGGERBOT_KEY) + Style.RESET_ALL)
    print("Change Mode         :", Fore.YELLOW + SWITCH_MODE_KEY + Style.RESET_ALL)
    print("Change FOV          :", Fore.YELLOW + FOV_KEY_UP + " / " + FOV_KEY_DOWN + Style.RESET_ALL)
    print("==== Information =====")
    print("Aimbot Mode         :", Fore.CYAN + switchmodes[bot.switchmode] + Style.RESET_ALL)
    print("Aimbot FOV          :", Fore.CYAN + str(A1M_FOV) + Style.RESET_ALL)
    print("Camera FOV          :", Fore.CYAN + str(CAM_FOV) + Style.RESET_ALL)
    print("Sensitivity         :", Fore.CYAN + "X: " + str(A1M_SPEED_X) + " Y: " + str(A1M_SPEED_Y) + Style.RESET_ALL)
    print("Offset              :", Fore.CYAN + "X: " + str(A1M_OFFSET_X) + " Y: " + str(A1M_OFFSET_Y) + Style.RESET_ALL)
    print("Aiming              :", (Fore.GREEN if bot.aimtoggled else Fore.RED) + str(bot.aimtoggled) + Style.RESET_ALL)
    print("Triggerbotting      :", (Fore.GREEN if bot.triggerbot else Fore.RED) + str(bot.triggerbot) + Style.RESET_ALL)

def update_triggerbot():
    while True:
        if TRIGGERBOT_KEY != "disabled":
            if TRIGGERBOT_KEY == 0x01 or TRIGGERBOT_KEY == 0x02:
                if GetAsyncKeyState(TRIGGERBOT_KEY) < 0:
                    bot.triggerbotswitch()
                    print_banner(bot)
            elif is_pressed(TRIGGERBOT_KEY):
                bot.triggerbotswitch()
                print_banner(bot)
        if FOV_KEY_UP != "disabled" and is_pressed(FOV_KEY_UP):
            A1M_FOV += 5
            audio("fovup.wav")
            print_banner(bot)
        if FOV_KEY_DOWN != "disabled" and is_pressed(FOV_KEY_DOWN):
            A1M_FOV -= 5
            audio("fovdown.wav")
            print_banner(bot)

        sleep(0.1)

Thread(target = update_triggerbot).start()

if __name__ == "__main__":
    bot = colorbot()
    print_banner(bot)
    while True:
        if SWITCH_MODE_KEY != "disabled" and is_pressed(SWITCH_MODE_KEY):
            bot.modeswitch()
            print_banner(bot)

        sleep(0.1)

        if A1M_KEY == 0x02 or A1M_KEY == 0x01:
            if GetAsyncKeyState(A1M_KEY) < 0:
                if bot.switchmode == 0:
                    while GetAsyncKeyState(A1M_KEY) < 0:
                        if not bot.aimtoggled: 
                            bot.a1mtoggle()
                            print_banner(bot)
                            while bot.aimtoggled: 
                                bot.process()
                                if not GetAsyncKeyState(A1M_KEY) < 0:
                                    bot.a1mtoggle()
                                    print_banner(bot)
                else:
                    bot.a1mtoggle()
                    print_banner(bot)
                    while bot.aimtoggled:
                        bot.process()
                        if GetAsyncKeyState(A1M_KEY) < 0:
                            bot.a1mtoggle()
                            print_banner(bot)
        elif is_pressed(A1M_KEY):
            if bot.switchmode == 0:
                while is_pressed(A1M_KEY):
                    if not bot.aimtoggled:
                        bot.a1mtoggle()
                        print_banner(bot)
                        while bot.aimtoggled:
                            bot.process()
                            if not is_pressed(A1M_KEY):
                                bot.a1mtoggle()
                                print_banner(bot)
            else: 
                bot.a1mtoggle()
                print_banner(bot)
                while bot.aimtoggled:
                    bot.process()
                    if is_pressed(A1M_KEY):
                        bot.a1mtoggle()
                        print_banner(bot)
