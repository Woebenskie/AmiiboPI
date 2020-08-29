import time
import os
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import RPi.GPIO as GPIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
#location of controller.py and its parameters
controllerpy = "/opt/AmiiboPI/controller.py PRO_CONTROLLER --nfc "
# Raspberry Pi pin configuration:
RST = None  # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
#draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)
path = "/root/amiibo/"
os.chdir(path)
sw1 = 4
sw2 = 17
sw3 = 27
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(sw1, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(sw2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(sw3, GPIO.IN, GPIO.PUD_UP)
startline = 0

draw_width = disp.width
draw_height = disp.height
drawing_image = Image.new('1', (draw_width, draw_height))
drawing = ImageDraw.Draw(drawing_image)

def draw_image(list,cursor):
    cmd = 'pwd'
    pwd = subprocess.check_output(cmd, shell=True)
    pwd = str(pwd).split('/')
    drawing.rectangle((0, 0, width, height), outline=0, fill=0)
    drawing.text((x, top), str(pwd[-1]).replace("b'", '').replace("\\n'", "").replace('/root', ''), font=font, fill=255)
    drawing.text((x, top + 8), str(list[cursor]).replace("b'", '').replace("\\n'", ""), font=font, fill=255)
    drawing.text((x, top + 16), str(list[0]).replace("b'", '').replace("\\n'", ""), font=font, fill=255)
    drawing.text((x, top + 24), str(list[1]).replace("b'", '').replace("\\n'", ""), font=font, fill=255)
    drawing.text((x, top + 32), str(list[2]).replace("b'", '').replace("\\n'", ""), font=font, fill=255)
    drawing.text((x, top + 40), str(list[3]).replace("b'", '').replace("\\n'", ""), font=font, fill=255)
    drawing.text((x, top + 48), str(list[4]).replace("b'", '').replace("\\n'", ""), font=font, fill=255)
    drawing.text((x, top + 56), str(list[5]).replace("b'", '').replace("\\n'", ""), font=font, fill=255)
    return drawing_image

def list_split(list):
    bufflist = list
    listoflist = []
    templist = []
    while len(list) % 6 != 0:
        bufflist.append("-")
    for item in bufflist:
        if len(templist) > 5:
            listoflist.append(templist)
            templist=[]
        templist.append(item.replace('_',' '))
    listoflist.append(templist)
    return listoflist

lines = 6
cursor = 0
todisp = 0
dirs = []
while True:
    button_state2 = GPIO.input(sw2)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top + 24), str("SW1=UP SW2=OK SW3=DOWN"), font=font, fill=255)
    draw.text((x, top + 40), str("Press ok to continue"), font=font, fill=255)
    disp.image(image)
    disp.display()
    time.sleep(.1)
    if button_state2 == GPIO.LOW:
        break
while True:
    cmd = 'pwd'
    pwd = subprocess.check_output(cmd, shell=True)
    pwd = str(pwd).split('/')
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    dirs = [f for f in os.listdir('.') if os.path.isfile(f) or os.path.isdir(f)]
    dirs.sort()
    line2 = pwd[-2]
    dirs.insert(0,str('To Amiibo dir'))

    button_state1 = GPIO.input(sw1)
    button_state2 = GPIO.input(sw2)
    button_state3 = GPIO.input(sw3)

    listoflist = list_split(dirs)

    ammount = len(dirs)
    ammount_pages = len(listoflist)


    if button_state3 == GPIO.LOW:
        cursor += 1
    if button_state1 == GPIO.LOW:
        cursor -= 1

    cmdt = 'pwd'
    pwdt = subprocess.check_output(cmdt, shell=True)
    pwdt = str(pwdt).replace("b'", '').replace("\\n'", "")

    if cursor == 6:
        cursor = 0
        todisp += 1
    if cursor == -6:
        cursor = 0
        todisp -= 1

    if button_state2 == GPIO.LOW:
        sel = listoflist[todisp]
        sel = sel[cursor].replace(" ","_")
        print(sel)
        if ".bin" not in sel:
            if 'To_Amiibo_dir' in sel:
                sel = path
            todir = os.path.join(pwdt,sel)
            print(todir)
            if os.path.isdir(todir):
                os.chdir(os.path.join(pwdt,sel))
                todisp = 0
                cursor = 0

            print(str(pwdt))
        elif ".bin" in sel:
            os.system("/usr/bin/python3 " + controllerpy + os.path.join(pwdt,sel))


    if todisp >= ammount_pages-1:
        todisp = ammount_pages-1
    if todisp <= 0:
        todisp = 0

    disp.image(draw_image(listoflist[todisp],cursor))
    disp.display()
    time.sleep(.1)
