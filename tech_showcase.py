import time
import random

import RPi.GPIO as GPIO

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, LCD_FONT

block1 = [0, 0, 7, 7]
block2 = [24, 0, 31, 7]

block3 = [8, 0, 15, 7]
block4 = [16, 0, 23, 7]

def play():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90)
    e_c = [1, 2]
    h_c = [1, 2, 3]
    _t = 0.75
    who = 0
    _p = True
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN)
    GPIO.setup(16, GPIO.IN)
    
    game = []
    for i in range(3):
        game.append(random.choice(e_c))
    
    instructions = "Hello.  The computer will show a pattern for you to repeat.  After every correct repetition the game gets harder.  Good luck..."
    show_message(device, instructions, fill="red", font=proportional(LCD_FONT), scroll_delay=0.035)
    time.sleep(0.5)
    
    while _p:
        if who == 0:
            comp_turn(game, _t, device)
            countdown(_t, device)
            who = 1
        elif who == 1:
            try:
                player_turn(game, _t, device)
            except WrongMove:
                endmsg(game, device)
                while True:
                    with canvas(device) as draw:
                        draw.text((1, -2), "Y", fill="red")
                        draw.text((25, -2), "N", fill="red")
                    if not GPIO.input(12):
                        _t = 0.75
                        game = []
                        for i in range(3):
                            game.append(random.choice(e_c))
                        who = 0
                        time.sleep(1)
                        break
                    elif not GPIO.input(16):
                        _p = False
                        show_message(device, "Goodbye.", fill="red", font=proportional(LCD_FONT), scroll_delay=0.035)
                        break
                continue
            if len(game) >= 8:
                game.append(random.choice(h_c))
            else:
                game.append(random.choice(e_c))
            if len(game) >= 6:
                _t = 0.65
            elif len(game) >= 10:
                _t = 0.55
            elif len(game) >= 12:
                _t = 0.45
            with canvas(device) as draw:
                draw.text((11, -2), "ok", fill="red")
            time.sleep(2*_t)
            who = 0;
        else:
            pass
    
def player_turn(game, _t, device):
    for i in game:
        correct = False
        if i == 1:
            timeout= time.time() + _t + 0.02
            while True:
                if time.time() > timeout:
                    break
                if not GPIO.input(12) and not GPIO.input(16):
                    with canvas(device) as draw:
                        draw.rectangle(block1, fill="red")
                        draw.rectangle(block2, fill="red")
                elif not GPIO.input(12):
                    with canvas(device) as draw:
                        correct = True
                        draw.rectangle(block1, fill="red")
                elif not GPIO.input(16):
                    with canvas(device) as draw:
                        draw.rectangle(block2, fill="red")
                else:
                    with canvas(device) as draw:
                        draw.rectangle(block1, fill="black")
                        draw.rectangle(block2, fill="black")
            if not correct:
                raise WrongMove
        elif i == 2:
            timeout= time.time() + _t + 0.02
            while True:
                if time.time() > timeout:
                    break
                if not GPIO.input(12) and not GPIO.input(16):
                    with canvas(device) as draw:
                        draw.rectangle(block1, fill="red")
                        draw.rectangle(block2, fill="red")
                elif not GPIO.input(12):
                    with canvas(device) as draw:
                        draw.rectangle(block1, fill="red")
                elif not GPIO.input(16):
                    with canvas(device) as draw:
                        correct = True
                        draw.rectangle(block2, fill="red")
                else:
                    with canvas(device) as draw:
                        draw.rectangle(block1, fill="black")
                        draw.rectangle(block2, fill="black")
            if not correct:
                raise WrongMove
        elif i == 3:
            timeout= time.time() + _t + 0.02
            while True:
                if time.time() > timeout:
                    break
                if not GPIO.input(12) and not GPIO.input(16):
                    with canvas(device) as draw:
                        correct = True
                        draw.rectangle(block1, fill="red")
                        draw.rectangle(block2, fill="red")
                elif not GPIO.input(12):
                    with canvas(device) as draw:
                        draw.rectangle(block1, fill="red")
                elif not GPIO.input(16):
                    with canvas(device) as draw:
                        draw.rectangle(block2, fill="red")
                else:
                    with canvas(device) as draw:
                        draw.rectangle(block1, fill="black")
                        draw.rectangle(block2, fill="black")
            if not correct:
                raise WrongMove
        else:
            pass
        
def comp_turn(game, _t, device):
    for i in game:
        if i == 1:
            with canvas(device) as draw:
                draw.text((11, -2), "me", fill="red")
                draw.rectangle(block1, fill="red")
            time.sleep(_t - .04)
            with canvas(device) as draw:
                draw.text((11, -2), "me", fill="red")
                draw.rectangle(block1, fill="black")
            time.sleep(.04)
        elif i == 2:
            with canvas(device) as draw:
                draw.text((11, -2), "me", fill="red")
                draw.rectangle(block2, fill="red")
            time.sleep(_t - .04)
            with canvas(device) as draw:
                draw.text((11, -2), "me", fill="red")
                draw.rectangle(block2, fill="black")
            time.sleep(.04)
        elif i == 3:
            with canvas(device) as draw:
                draw.text((11, -2), "me", fill="red")
                draw.rectangle(block1, fill="red")
                draw.rectangle(block2, fill="red")
            time.sleep(_t - .04)
            with canvas(device) as draw:
                draw.text((11, -2), "me", fill="red")
                draw.rectangle(block1, fill="black")
                draw.rectangle(block2, fill="black")
            time.sleep(.04)
        else:
            pass
        
def countdown(_t, device):
    with canvas(device) as draw:
        draw.text((14, -2), "3", fill="red")
    time.sleep(_t)
    with canvas(device) as draw:
        draw.text((14, -2), "2", fill="red")
    time.sleep(_t)
    with canvas(device) as draw:
        draw.text((14, -2), "1", fill="red")
    time.sleep(_t)
    with canvas(device) as draw:
        draw.text((11, -4), "go", fill="red")
    time.sleep(_t)
    
def endmsg(game, device):
    with canvas(device) as draw:
        draw.text((1, -2), "X", fill="red")
        draw.text((17, -2), "X", fill="red")
        draw.rectangle(block2, fill="red")
        draw.rectangle(block3, fill="red")
    time.sleep(.5)
    with canvas(device) as draw:
        draw.text((9, -2), "X", fill="red")
        draw.text((25, -2), "X", fill="red")
        draw.rectangle(block1, fill="red")
        draw.rectangle(block4, fill="red")
    time.sleep(.5)
    with canvas(device) as draw:
        draw.text((1, -2), "X", fill="red")
        draw.text((17, -2), "X", fill="red")
        draw.rectangle(block2, fill="red")
        draw.rectangle(block3, fill="red")
    time.sleep(.5)
    with canvas(device) as draw:
        draw.text((9, -2), "X", fill="red")
        draw.text((25, -2), "X", fill="red")
        draw.rectangle(block1, fill="red")
        draw.rectangle(block4, fill="red")
    time.sleep(.5)
    msg = "Game over.  Your score was " + str(len(game)) + ".  Play again?"
    show_message(device, msg, fill="red", font=proportional(LCD_FONT), scroll_delay=0.035)
    
class WrongMove(Exception):
    pass
    
if __name__ == "__main__":
    play()
    