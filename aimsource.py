# original: https://github.com/Seconb/Arsenal-Colorbot

from cv2 import findContours, threshold, dilate, inRange, cvtColor, COLOR_BGR2HSV, THRESH_BINARY, RETR_EXTERNAL, CHAIN_APPROX_NONE, contourArea
from numpy import array, ones, uint8
from os import path, system
from math import sqrt
from mss import mss
from keyboard import is_pressed
from configparser import ConfigParser
from win32api import GetAsyncKeyState
from colorama import Fore, Style
from ctypes import windll
from time import sleep
from threading import Thread
from urllib.request import urlopen
from webbrowser import open
from pygetwindow import getActiveWindow

range = range
len = len
print = print
tuple = tuple
int = int
max = max
sleep = sleep

user32 = windll.user32

switchmodes = ("Hold", "Toggle")
resetall = Style.RESET_ALL

system("title Colorbot")

if urlopen("https://raw.githubusercontent.com/AndrewDarkyy/Colorbot-Modded/main/version.txt").read().decode("utf-8") != "v1.6\n":
    print(Style.BRIGHT + Fore.CYAN + "This version is outdated, please get the latest one at " + Fore.YELLOW + "https://github.com/AndrewDarkyy/Colorbot-Modded/releases" + resetall)
    open("https://github.com/AndrewDarkyy/Colorbot-Modded/releases")
    while True:
        pass

def string_tokey(string, key):
    if string.lower() == "leftclick":
        return 0x01
    elif string.lower() == "rightclick":
        return 0x02
    elif string.lower() == "middleclick":
        return 0x04
    elif string.lower() == "sidebutton1":
        return 0x05
    elif string.lower() == "sidebutton2":
        return 0x06
    else:
        try:
            is_pressed(string)
        except:
            print(f"Please change {key} to an existing key.")
            while True:
                pass
        return string
    

def is_roblox_focused():
    try:
        return "Roblox" in getActiveWindow().title
    except:
        return False
    
def key_tostring(key):
    if key == 0x01:
        return "LeftClick"
    elif key == 0x02:
        return "RightClick"
    elif key == 0x04:
        return "MiddleClick"
    elif key == 0x05:
        return "SideButton1"
    elif key == 0x06:
        return "SideButton2"
    else:
        return str(key)
    
try:
    config = ConfigParser()
    config.optionxform = str
    config.read(path.join(path.dirname(path.dirname(__file__)), "config.ini"))
    global AIM_KEY, SWITCH_MODE_KEY, AIM_FOV, TRIGGERBOT_DELAY, AIM_OFFSET_Y, AIM_OFFSET_X, AIM_SPEED_X, AIM_SPEED_Y, COLOR, lower, upper, colorname
    
    AIM_KEY = string_tokey(config.get("Config", "AIM_KEY"), "AIM_KEY")
    SWITCH_MODE_KEY = string_tokey(config.get("Config", "SWITCH_MODE_KEY"), "SWITCH_MODE_KEY")
    AIM_FOV = int(config.get("Config", "AIM_FOV"))
    TRIGGERBOT_DELAY = float(config.get("Config", "TRIGGERBOT_DELAY"))
    AIM_SPEED_X = float(config.get("Config", "AIM_SPEED_X"))
    AIM_SPEED_Y = float(config.get("Config", "AIM_SPEED_Y"))
    AIM_OFFSET_Y = int(config.get("Config", "AIM_OFFSET_Y"))
    AIM_OFFSET_X = int(config.get("Config", "AIM_OFFSET_X"))
    COLOR = str(config.get("Config", "COLOR"))

    if COLOR.lower() == "blue":
        colorname = Fore.BLUE
        upper = array((123, 255, 217), dtype="uint8")
        lower = array((113, 206, 189), dtype="uint8")
    elif COLOR.lower() == "pink" or COLOR.lower() == "purple":
        colorname = Fore.MAGENTA
        upper = array((150, 255, 201), dtype="uint8")
        lower = array((150, 255, 200), dtype="uint8")
    elif COLOR.lower() == "green":
        colorname = Fore.GREEN
        upper = array((60, 255, 201), dtype="uint8")
        lower = array((60, 255, 201), dtype="uint8")
    elif COLOR.lower() == "cyan":
        colorname = Fore.CYAN
        upper = array((90, 255, 201), dtype="uint8")
        lower = array((90, 255, 201), dtype="uint8")
    else:
        colorname = Fore.YELLOW
        upper = array((38, 255, 203), dtype="uint8")
        lower = array((30, 255, 201), dtype="uint8")
except Exception as e:
    print("Error occurred while loading settings:", e)

sct = mss()

center = AIM_FOV / 2

screenshot = sct.monitors[1]
screenshot["left"] = int((screenshot["width"] / 2) - center)
screenshot["top"] = int((screenshot["height"] / 2) - center)
screenshot["width"] = AIM_FOV
screenshot["height"] = AIM_FOV

ones_uint = ones((3, 3), uint8)
sct_grab = sct.grab
m_event = user32.mouse_event

class colorbot:
    def __init__(self):
        self.aimtoggled = False
        self.switchmode = 0
        self.__clicks = 0
        self.__shooting = False

    def __stop(self):
        oldclicks = self.__clicks
        sleep(.05)
        if self.__clicks == oldclicks:
            m_event(0x0004)

    def __delayedaim(self):
        self.__shooting = True
        sleep(TRIGGERBOT_DELAY)
        m_event(0x0002)
        self.__clicks += 1
        Thread(target = self.__stop).start()
        self.__shooting = False

    def process(self):
        if is_roblox_focused():
            (contours, hierarchy) = findContours(threshold(dilate(inRange(cvtColor(array(sct_grab(screenshot)), COLOR_BGR2HSV), lower, upper), ones_uint, iterations=5), 60, 255, THRESH_BINARY)[1], RETR_EXTERNAL, CHAIN_APPROX_NONE)
            if len(contours) != 0:
                contour = max(contours, key=contourArea)
                topmost = tuple(contour[contour[:, :, 1].argmin()][0])
                x = topmost[0] - center + AIM_OFFSET_X
                y = topmost[1] - center + AIM_OFFSET_Y
                distance = sqrt(x*x + y*y)
                if distance <= AIM_FOV:
                    m_event(0x0001, int(x * AIM_SPEED_X), int(y * AIM_SPEED_Y), 0, 0)
                if distance <= 9:
                    if TRIGGERBOT_DELAY != 0:
                        if self.__shooting == False:
                            Thread(target = self.__delayedaim).start()
                    else:
                        m_event(0x0002)
                        self.__clicks += 1
                        Thread(target = self.__stop).start()
                elif distance<=50:
                    for index in range(len(contour)):
                        topmost = tuple(contour[index][0])
                        x = topmost[0] - center + AIM_OFFSET_X
                        y = topmost[1] - center + AIM_OFFSET_Y
                        distance = sqrt(x*x + y*y)
                        if distance <= 8:
                            if TRIGGERBOT_DELAY != 0:
                                if self.__shooting == False:
                                    Thread(target = self.__delayedaim).start()
                            else:
                                m_event(0x0002)
                                self.__clicks += 1
                                Thread(target = self.__stop).start()
                            break

    def aimtoggle(self):
        self.aimtoggled = not self.aimtoggled
        sleep(.08)

    def modeswitch(self):
        if self.switchmode == 0:
            self.switchmode = 1
        elif self.switchmode == 1:
            self.switchmode = 0
        sleep(.08)

def print_banner(bot):
    system("cls")
    print(Style.BRIGHT + Fore.CYAN + "Colorbot for Arsenal!" + Fore.RED + " Credits to @andrewdarkyy. and @seconb" + resetall)
    print(Style.BRIGHT + Fore.GREEN + "Join our discord server for updates https://discord.gg/hH62fKGJnv" + resetall)
    print(Style.BRIGHT + Fore.MAGENTA + "Make sure you fullscreen your Roblox window and are in the web version!" + resetall)
    print(Style.BRIGHT + Fore.YELLOW + "====== Controls ======" + resetall)
    print("Aimbot Keybind    :", Fore.YELLOW + key_tostring(AIM_KEY) + resetall)
    print("Change Mode       :", Fore.YELLOW + key_tostring(SWITCH_MODE_KEY) + resetall)
    print(Style.BRIGHT + Fore.YELLOW + "==== Information =====" + resetall)
    print("Aimbot Mode       :", Fore.CYAN + switchmodes[bot.switchmode] + resetall)
    print("Aimbot FOV        :", Fore.CYAN + str(AIM_FOV) + resetall)
    print("Shoot Delay       :", Fore.CYAN + str(TRIGGERBOT_DELAY) + resetall)
    print("Sensitivity       :", Fore.CYAN + "X: " + str(AIM_SPEED_X) + " Y: " + str(AIM_SPEED_Y) + resetall)
    print("Offset            :", Fore.CYAN + "X: " + str(AIM_OFFSET_X) + " Y: " + str(AIM_OFFSET_Y) + resetall)
    print("Aiming            :", (Fore.GREEN if bot.aimtoggled else Fore.RED) + str(bot.aimtoggled) + resetall)
    print("Enemy Color       :", Fore.CYAN + str(Style.NORMAL + colorname + COLOR))

open("https://discord.gg/hH62fKGJnv")

if __name__ == "__main__":
    bot = colorbot()
    del colorbot
    del urlopen
    del mss
    del open
    del ConfigParser
    del string_tokey
    print_banner(bot)
    while True:
        if SWITCH_MODE_KEY == 0x01 or SWITCH_MODE_KEY == 0x02 or SWITCH_MODE_KEY == 0x04:
            if GetAsyncKeyState(SWITCH_MODE_KEY) < 0:
                bot.modeswitch()
                print_banner(bot)
        elif SWITCH_MODE_KEY == 0x05 or SWITCH_MODE_KEY == 0x06:
            if bool(user32.GetKeyState(SWITCH_MODE_KEY) & 0x80):
                bot.modeswitch()
                print_banner(bot)
        elif is_pressed(SWITCH_MODE_KEY):
            bot.modeswitch()
            print_banner(bot)
        
        sleep(0.1)

        if AIM_KEY == 0x02 or AIM_KEY == 0x01 or AIM_KEY == 0x04:
            if GetAsyncKeyState(AIM_KEY) < 0:
                if bot.switchmode == 0:
                    while GetAsyncKeyState(AIM_KEY) < 0:
                        if not bot.aimtoggled:
                            bot.aimtoggle()
                            print_banner(bot)
                            while bot.aimtoggled: 
                                bot.process()
                                if not GetAsyncKeyState(AIM_KEY) < 0:
                                    bot.aimtoggle()
                                    print_banner(bot)
                else:
                    bot.aimtoggle()
                    print_banner(bot)
                    while bot.aimtoggled:
                        bot.process()
                        if GetAsyncKeyState(AIM_KEY) < 0:
                            bot.aimtoggle()
                            print_banner(bot)
        elif AIM_KEY == 0x05 or AIM_KEY == 0x06:
            if bool(user32.GetKeyState(AIM_KEY) & 0x80):
                if bot.switchmode == 0:
                    while bool(user32.GetKeyState(AIM_KEY) & 0x80):
                        if not bot.aimtoggled:
                            bot.aimtoggle()
                            print_banner(bot)
                            while bot.aimtoggled: 
                                bot.process()
                                if not bool(user32.GetKeyState(AIM_KEY) & 0x80):
                                    bot.aimtoggle()
                                    print_banner(bot)
                else:
                    bot.aimtoggle()
                    print_banner(bot)
                    while bot.aimtoggled:
                        bot.process()
                        if bool(user32.GetKeyState(AIM_KEY) & 0x80):
                            bot.aimtoggle()
                            print_banner(bot)
        elif is_pressed(AIM_KEY):
            if bot.switchmode == 0:
                while is_pressed(AIM_KEY):
                    if not bot.aimtoggled:
                        bot.aimtoggle()
                        print_banner(bot)
                        while bot.aimtoggled:
                            bot.process()
                            if not is_pressed(AIM_KEY):
                                bot.aimtoggle()
                                print_banner(bot)
            else: 
                bot.aimtoggle()
                print_banner(bot)
                while bot.aimtoggled:
                    bot.process()
                    if is_pressed(AIM_KEY):
                        bot.aimtoggle()
                        print_banner(bot)
