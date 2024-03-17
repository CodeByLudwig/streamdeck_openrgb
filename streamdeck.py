#!/usr/bin/env python3
import os
import time
import threading
from operator import itemgetter
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
from PIL import Image


# motherboard = client.get_devices_by_type(DeviceType.MOTHERBOARD)[0]
profilePath = "C:/Users/ludwi/AppData/Roaming/OpenRGB";
imagePath = "C:/Programmieren/Streamdeck LED/color_circle.png"
newImagePath = "C:/Programmieren/Streamdeck LED/color_circle_new.png"
files = []
fileColors = { "blue": (0, 0, 255, 255), "red": (255, 0, 0, 255), "green": (0, 255, 0, 255), "violet": (169, 23, 255, 255) }
fileRange = 0
fileIndex = 0


def render_key_image(deck):
    icon = Image.open(newImagePath)
    image = PILHelper.create_scaled_image(deck, icon, margins=[10, 10, 10, 10])

    return PILHelper.to_native_format(deck, image)

def change_image_color(outerColor, innerColor):
    with Image.open(imagePath) as img:
        img = img.convert('RGBA')
        width, height = img.size
    
        for x in range(0, width - 1):
            for y in range(0, height - 1):
                pix = img.load()
                current_color = (pix[x, y])
                if current_color == (255, 255, 255,255):
                    img.putpixel( (x,y), outerColor)
                if current_color == (0, 0, 0,255):
                    img.putpixel( (x,y), innerColor)    
                           
        return img
    
def key_change_callback(deck, key, state):
    global fileIndex
    init_openRGB()
    
    if state == True and key == 2:
        nextElement = itemgetter(*[fileIndex])(files)
        color = nextElement.split('.')[0]
        client = OpenRGBClient()
        # update_key_image(deck, key, fileColors[color])
        client.load_profile(color)        
        fileIndex = fileIndex + 1 if (fileRange - 1) > fileIndex else 0
        nextElement1 = itemgetter(*[fileIndex])(files)
        color1 = nextElement1.split('.')[0]
        update_key_image(deck, key, fileColors[color], fileColors[color1])

def update_key_image(deck, key, outerColor, innerColor):
    change_image_color(outerColor, innerColor).save(newImagePath)
    image = render_key_image(deck)
    deck.set_key_image(key, image) 

def init_openRGB():
    global files
    files = []
    
    for file in os.listdir(profilePath):
        if file.endswith(".orp"):
            files.append(file)
    
    global fileRange
    fileRange = len(files)
    
if __name__ == "__main__":  
    streamdecks = DeviceManager().enumerate()
    init_openRGB()
    
    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        if not deck.is_visual():
            continue

        deck.open()
        
        update_key_image(deck, 2, fileColors["violet"], fileColors["violet"])
        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass

        # input("Press Enter to continue...")
    