#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import time
import Adafruit_SSD1306
import RPi.GPIO as GPIO


from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_press, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

logger = logging.getLogger(__name__)

sw1 = 4
sw2 = 17
sw3 = 27

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(sw1, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(sw2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(sw3, GPIO.IN, GPIO.PUD_UP)

RST = None
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
padding = -2
top = padding
bottom = height - padding
x = 0
font = ImageFont.load_default()

def ask_button(controller_state):
    button_sel = 0
    buttons = list(controller_state.button_state.get_available_buttons())
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    if 'capture' in buttons:
        buttons.remove('capture')
    if 'home' in buttons:
        buttons.remove('home')
    while True:
        button_state1 = GPIO.input(sw1)
        button_state2 = GPIO.input(sw2)
        button_state3 = GPIO.input(sw3)

        if button_state1 == GPIO.LOW:
            button_sel -= 1
        if button_state3 == GPIO.LOW:
            button_sel += 1

        if button_sel >= len(buttons)-1:
            button_sel = len(buttons)-1
        if button_sel <= 0:
            button_sel = 0
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x, top), str("SW1=UP SW2=OK SW3=DOWN"), font=font, fill=255)
        draw.text((x+12, top+8), str("Select NFC Button"), font=font, fill=255)
        draw.text((x + 58, top + 32), str(buttons[button_sel]), font=font, fill=255)
        time.sleep(.1)
        disp.image(image)
        disp.display()
        if button_state2 == GPIO.LOW:
            return buttons[button_sel]


async def run_at_start(controller_state: ControllerState):


    if controller_state.get_controller() != Controller.PRO_CONTROLLER:
        raise ValueError('This script only works with the Pro Controller!')
    await controller_state.connect()
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x + 12, top + 32), str("Switch Connected!"), font=font, fill=255)
    draw.text((x + 6, top + 40), str("Going back to game."), font=font, fill=255)
    disp.image(image)
    disp.display()


    await button_push(controller_state, 'a')
    await asyncio.sleep(1)
    await button_push(controller_state, 'home')
    await asyncio.sleep(1)
    await button_push(controller_state, 'left', sec=2)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(3)

    amiibo_button = ask_button(controller_state)

    #await button_push(controller_state, 'l&&r')
    while True:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x+42,top), str("SW1 = A"),font=font, fill=255)
        draw.text((x+36, top + 8), str("SW2 = L+R"), font=font, fill=255)
        draw.text((x+42, top + 16), str("SW3 = " + amiibo_button), font=font, fill=255)
        draw.text((x+40, top + 32), str("SW1+2 = EXIT"), font=font, fill=255)
        draw.text((x+30, top + 48), str("Waiting on "), font=font, fill=255)
        draw.text((x+24, top + 56), str("button press"), font=font, fill=255)
        disp.image(image)
        disp.display()
        #time.sleep(.1)
        button_state1 = GPIO.input(sw1)
        button_state2 = GPIO.input(sw2)
        button_state3 = GPIO.input(sw3)
        if button_state1 == GPIO.LOW:
            await button_push(controller_state, 'a')
        if button_state2 == GPIO.LOW:
            await button_press(controller_state, 'l')
            await button_press(controller_state, 'r')
            await asyncio.sleep(1.5)
            await button_release(controller_state, 'l')
            await button_release(controller_state, 'r')
        if button_state3 == GPIO.LOW:
            await button_push(controller_state, str(amiibo_button))
            await asyncio.sleep(3)
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            disp.image(image)
            disp.display()
            break
        if button_state1 == GPIO.LOW and button_state2 == GPIO.LOW:
            break

async def _main(args):
    # parse the spi flash
    if args.spi_flash:
        with open(args.spi_flash, 'rb') as spi_flash_file:
            spi_flash = FlashMemory(spi_flash_file.read())
    else:
        # Create memory containing default controller stick calibration
        spi_flash = FlashMemory()

    # Get controller name to emulate from arguments
    controller = Controller.from_arg(args.controller)
    async def nfc(*args):
        if controller_state.get_controller() == Controller.JOYCON_L:
            raise ValueError('NFC content cannot be set for JOYCON_L')
        elif not args:
            raise ValueError('"nfc" command requires file path to an nfc dump as argument!')
        elif args[0] == 'remove':
            controller_state.set_nfc(None)
            print('Removed nfc content.')
        else:
            _loop = asyncio.get_event_loop()
            with open(args[0], 'rb') as nfc_file:
                content = await _loop.run_in_executor(None, nfc_file.read)
                controller_state.set_nfc(content)

    with utils.get_output(path=args.log, default=None) as capture_file:
        # prepare the the emulated controller
        factory = controller_protocol_factory(controller, spi_flash=spi_flash)
        ctl_psm, itr_psm = 17, 19
        draw.text((x, top + 16), str("Waiting for Switch to"), font=font, fill=255)
        draw.text((x + 40, top + 24), str("Connect,"), font=font, fill=255)
        draw.text((x + 18, top + 40), str("Please open the"), font=font, fill=255)
        draw.text((x + 6, top + 48), str("'Change Grip/Order'"), font=font, fill=255)
        draw.text((x + 46, top + 56), str("menu."), font=font, fill=255)

        disp.image(image)
        disp.display()
        transport, protocol = await create_hid_server(factory, reconnect_bt_addr=args.reconnect_bt_addr,
                                                      ctl_psm=ctl_psm,
                                                      itr_psm=itr_psm, capture_file=capture_file,
                                                      device_id=args.device_id)

        controller_state = protocol.get_controller_state()

        # Create command line interface and add some extra commands
        cli = ControllerCLI(controller_state)

        # set default nfc content supplied by argument
        if args.nfc is not None:
            await cli.commands['nfc'](args.nfc)

        # run the cli
        try:
            await nfc(args.nfc)
            await run_at_start(controller_state)
            #await cli.run()


        finally:
            logger.info('Stopping communication...')
            await transport.close()



if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    # setup logging
    log.configure(console_level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('controller', help='JOYCON_R, JOYCON_L or PRO_CONTROLLER')
    parser.add_argument('--nfc', type=str, default=None)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _main(args)
    )
