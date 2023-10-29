import winsound # Beep noises (temp disabled)
import os
import cv2 # Reads through screenshot
import win32con
import numpy as np # Works with CV2
from mss import mss # Takes screenshot
from keyboard import is_pressed # Library that relates to reading and writing keyboard inputs
from configparser import ConfigParser
from win32api import GetAsyncKeyState # Windows API that I just use for mouse button keybinds and mouse movement to an enemy
from colorama import Fore, Style # Makes the colorful text in the console
from ctypes import windll # Also Windows API to move the mouse
from time import sleep # Allows for specific time delays and such
from threading import Thread
#importing all the modules we need to run the code.

# im no python dev tho im a lua dev so code may be weird
# and obv its just a modded code original is !!!!!colorb!!!!!
# so basically colorb with added ragebot and removed unused shit and better anti shakeness (thanks to bolts for the config)

switchmodes = ["hold", "toggle"] #this is a array of [0, 1] where hold is 0, toggle is 1.

os.system("title Seconb for Arsenal") # add a title

sdir = os.path.dirname(os.path.abspath(__file__)) #Finding current directory where the script is being run in
config_file_path = os.path.join(sdir, "config.ini") # Searching for the file called config.ini to read settings

try:
    config = ConfigParser() #this is separating all the config options you set.
    config.optionxform = str
    config.read(config_file_path)
except Exception as e: #every try: ... except Exception as e: ... is a form of general error catching, the basics.
    print("Error reading configuration:", e)


def loadsettings(): #loading the settings, duh.
    global A1M_KEY, SWITCH_MODE_KEY
    global FOV_KEY_UP, FOV_KEY_DOWN, CAM_FOV
    global A1M_OFFSET_Y, A1M_OFFSET_X, A1M_SPEED_X, A1M_SPEED_Y
    global upper, lower, A1M_FOV, BINDMODE
    #these are essential variables that show the settings of the application.
    try:
        BINDMODE = config.get("Config", "BINDMODE")
        if (
            BINDMODE.lower() == "win32"
            or BINDMODE.lower() == "win32api"
            or BINDMODE.lower() == "win"
        ):
            A1M_KEY_STRING = config.get("Config", "A1M_KEY")
            if "win32con" in A1M_KEY_STRING:
                A1M_KEY = eval(A1M_KEY_STRING, {"win32con": win32con})
            else:
                A1M_KEY = str(A1M_KEY_STRING)
        if (
            BINDMODE.lower() == "keyboard"
            or BINDMODE.lower() == "k"
            or BINDMODE.lower() == "key"
        ):
            A1M_KEY = config.get("Config", "A1M_KEY")
        SWITCH_MODE_KEY = config.get("Config", "SWITCH_MODE_KEY")
        FOV_KEY_UP = config.get("Config", "FOV_KEY_UP")
        FOV_KEY_DOWN = config.get("Config", "FOV_KEY_DOWN")
        CAM_FOV = int(config.get("Config", "CAM_FOV"))
        A1M_FOV = int(config.get("Config", "A1M_FOV"))
        A1M_OFFSET_Y = int(config.get("Config", "A1M_OFFSET_Y"))
        A1M_OFFSET_X = int(config.get("Config", "A1M_OFFSET_X"))
        A1M_SPEED_X = float(config.get("Config", "A1M_SPEED_X"))
        A1M_SPEED_Y = float(config.get("Config", "A1M_SPEED_Y"))
        upper = np.array([38, 255, 203], dtype="uint8") # The upper and lower ranges defined are the colors that the aimbot will detect and shoot at
        lower = np.array([30, 255, 201], dtype="uint8") # It's basically a group of a VERY specific shade of yellow (in this case) that it will shoot at and nothing else. The format is HSV, which differs from RGB.
        # For more experienced users, to change the upper and lower, then use this tool: https://github.com/hariangr/HsvRangeTool 
        # Take a screenshot of an enemy with the highlight color you want and get the range and add that here in place of the current upper and lower
    
    except Exception as e:
        print("Error loading settings:", e)


sct = mss()

try:
    loadsettings() #try to catch any errors with the settings maybe a typo or something.
except Exception as e:
    print("Error loading settings:", e)

screenshot = sct.monitors[1] #this is the settings for the screen capture, the program screenshots your first monitor and continues to look for enemies.
screenshot["left"] = int((screenshot["width"] / 2) - (CAM_FOV / 2))
screenshot["top"] = int((screenshot["height"] / 2) - (CAM_FOV / 2))
screenshot["width"] = CAM_FOV
screenshot["height"] = CAM_FOV
center = CAM_FOV / 2

audiodir = os.path.join(sdir, "audios") # this is use all our audio files with the code.

try:
    def audio(wavname):
        audiopath = os.path.join(audiodir, wavname)
        winsound.PlaySound(audiopath, winsound.SND_FILENAME | winsound.SND_ASYNC) #this is how we play audio files. (temp disabled)
except Exception as e:
    print("Error setting up audio:", e)


def lclc():
    try:
        return GetAsyncKeyState(A1M_KEY) < 0 #checking if the aim key is pressed (mouse buttons)
    except Exception as e:
        print("Error checking key state:", e)


class trb0t:
    def __init__(self): #initialize the code, first set the variables for default settings.
        self.a1mtoggled = False
        self.clicks = 0
        self.switchmode = 0 #as i said earlier, the array is 0-1, 0 being hold, 1 being toggle. the default is HOLD as you can see.

    def stop(self):
        oldclicks=self.clicks
        sleep(.05)
        if self.clicks==oldclicks:
            windll.user32.mouse_event(0x0004)

    def process(self): #process all images we're capturing
        try: 
            img = np.array(sct.grab(screenshot))
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #grab hsv color format from the screenshot
            mask = cv2.inRange(hsv, lower, upper) # create a mask of only the enemy colors
            dilated = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=5) # dilation makes objects appear larger for the aimbot
            thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1] # threshold
            (contours, hcry) = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE # find contours
            )
            if len(contours) != 0: # if enemies are on screen: (or if there are contours of enemies on screen)
                contour = max(contours, key=cv2.contourArea)
                topmost = tuple(contour[contour[:, :, 1].argmin()][0]) #finds the highest contour vertically (highest point of the enemy, their head)
                x = topmost[0] - center + A1M_OFFSET_X # calculating the perfect center of the enemy's head by offsetting it a set amount of pixels
                y = topmost[1] - center + A1M_OFFSET_Y
                distance = np.sqrt(x**2 + y**2) # basic distance in a 2d plane. calculated using pythagorean theorem.
                if distance <= A1M_FOV:
                    windll.user32.mouse_event(0x0001, int(x * A1M_SPEED_X), int(y * A1M_SPEED_Y), 0, 0) #move the mouse towards, usually should feel like aimassist.
                    if (distance <= 13):
                        windll.user32.mouse_event(0x0002)
                        self.clicks +=1
                        Thread(target=self.stop).start()
        except Exception as e:
            print("Error in processing:", e)

    def a1mtoggle(self):
        try:
            self.a1mtoggled = not self.a1mtoggled
            sleep(.05) # very short cooldown to stop it from thinking we're rapid toggling.
        except Exception as e:
            print("Error toggling A1M:", e)

    def modeswitch(self): #switch the modes from again, the array, from 0 to 1, 0 being hold, 1 being toggle.
        try:
            if self.switchmode == 0:
                self.switchmode = 1 # adding so that it looks for 1, which is toggle.
                audio("toggle.wav") # using the audio function we looked at earlier, which allows us to play a file from the audio dir.
            elif self.switchmode == 1:
                self.switchmode = 0
                audio("hold.wav")
        except Exception as e:
            print("Error switching modes:", e)


def print_banner(b0t: trb0t): #Printing the information
    try:
        os.system("cls") # First clearing the terminal, to then re-print with the new information. Note the colorama formatting with styling and colors!
        print(
            Style.BRIGHT
            + Fore.CYAN
            + """ Seconb Color Aim for Arsenal! """ # code modified by taylor
            + Style.RESET_ALL
        )
        print("====== Controls ======")
        print("Activate a1mb0t      :", Fore.YELLOW + str(A1M_KEY) + Style.RESET_ALL)
        print("Switch toggle/hold   :", Fore.YELLOW + SWITCH_MODE_KEY + Style.RESET_ALL)
        print(
            "Change FOV           :",
            Fore.YELLOW + FOV_KEY_UP + "/" + FOV_KEY_DOWN + Style.RESET_ALL,
        )
        print("==== Information =====")
        print(
            "Toggle/Hold Mode     :",
            Fore.CYAN + switchmodes[b0t.switchmode] + Style.RESET_ALL,
        )
        print("A1m FOV              :", Fore.CYAN + str(A1M_FOV) + Style.RESET_ALL)
        print("Cam FOV              :", Fore.CYAN + str(CAM_FOV) + Style.RESET_ALL)
        print(
            "A1m Speed            :",
            Fore.CYAN
            + "X: "
            + str(A1M_SPEED_X)
            + " Y: "
            + str(A1M_SPEED_Y)
            + Style.RESET_ALL,
        )
        print(
            "A1m Offset           :",
            Fore.CYAN
            + "X: "
            + str(A1M_OFFSET_X)
            + " Y: "
            + str(A1M_OFFSET_Y)
            + Style.RESET_ALL,
        )
        print(
            "A1m Activated        :",
            (Fore.GREEN if b0t.a1mtoggled else Fore.RED)
            + str(b0t.a1mtoggled)
            + Style.RESET_ALL,
        )
    except Exception as e:
        print("Error printing banner:", e)


if __name__ == "__main__":
    b0t = trb0t() #the main class we made earlier
    try:
        print_banner(b0t) #to update information or print initial info.
        while True:
            # under each if statement, we first check if the key is set to disabled (if it is disabled, then it will not function. this allows the user to disable keys they don't wish to use.
            if SWITCH_MODE_KEY != "disabled" and is_pressed(SWITCH_MODE_KEY):
                b0t.modeswitch() #switching the mode if the user presses the switch mode key AND its not disabled.
                print_banner(b0t) #updating the information
            if FOV_KEY_UP != "disabled" and is_pressed(FOV_KEY_UP):
                A1M_FOV += 5 #same thing as before, just adding 5 increments to the fov.
                audio("fovup.wav")
                print_banner(b0t)
            if FOV_KEY_DOWN != "disabled" and is_pressed(FOV_KEY_DOWN):
                A1M_FOV -= 5 #same thing as before just removing 5 increments
                audio("fovdown.wav")
                print_banner(b0t)

            sleep(0.1) #.1s cooldown as a way of preventing lag and mispresses

            if (
                BINDMODE.lower() == "win32"
                or BINDMODE.lower() == "win32api"
                or BINDMODE.lower() == "win" #make all strings lowercase just in case if someone in config typed it out as WIN32API, which the code wouldn't recognize.
            ): # this is mostly for the mouse buttons.
                if lclc(): #if user is holding down on the key or a key.
                    if b0t.switchmode == 0: #if mode is on [**0**, 1] (means if 0) which is hold.
                        while lclc(): #while the user is holding the key.
                            if not b0t.a1mtoggled: 
                                b0t.a1mtoggle() #and if the aim isn't already activated, activate it.
                                print_banner(b0t) #update info
                                while b0t.a1mtoggled: 
                                    b0t.process() #while it is on/activated THEN process all screen capture, note that it doesn't process information unless activated.
                                    if not lclc(): 
                                        b0t.a1mtoggle() #if user stops holding the key, it'll turn off the colorbot.
                                        print_banner(b0t) #update info.
                    if b0t.switchmode == 1: #if mode is on [0, **1**] (means if toggled)
                        b0t.a1mtoggle() # activate it forever until user presses again.
                        print_banner(b0t)
                        #winsound.Beep(200, 200) removing beep as its causing crashes, temp fix.
                        while b0t.a1mtoggled: #while it is toggled
                            b0t.process() # process the images.
                            if lclc():
                                b0t.a1mtoggle() # if user presses the button, then deactivate
                                #winsound.Beep(200, 200) removing beep as its causing crashes, temp fix.
                                print_banner(b0t) #update info
            else:
                if is_pressed(A1M_KEY): #else if the user uses keyboard config, then look for keyboard buttons instead.
                    if b0t.switchmode == 0:
                        while is_pressed(A1M_KEY): # SAME EXACT PROCESS AS THE MOUSE KEY PRESSES ABOVE, REFER THERE.
                            if not b0t.a1mtoggled:
                                b0t.a1mtoggle()
                                print_banner(b0t)
                                while b0t.a1mtoggled:
                                    b0t.process()
                                    if not is_pressed(A1M_KEY):
                                        b0t.a1mtoggle()
                                        print_banner(b0t)
                    if b0t.switchmode == 1: 
                        b0t.a1mtoggle() # SAME EXACT PROCESS AS THE MOUSE KEY PRESSES ABOVE, REFER THERE.
                        print_banner(b0t)
                        #winsound.Beep(200, 200) removing beep as its causing crashes, temp fix.
                        while b0t.a1mtoggled:
                            b0t.process()
                            if is_pressed(A1M_KEY):
                                b0t.a1mtoggle()
                                #winsound.Beep(200, 200)  removing beep as its causing crashes, temp fix.
                                print_banner(b0t)
    except Exception as e:
        print("An error occurred:", e) #the end, DM befia on discord if you need clarity. Info by, duh, befia or taylor.