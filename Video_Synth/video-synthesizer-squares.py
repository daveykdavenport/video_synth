import pyaudio
import sys
import numpy as np
import aubio
import pygame
import random
from threading import Thread
import queue
import time
import argparse

#Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("-input", required=False, type=int, help="Audio Input Device")
parser.add_argument("-f", action="store_true", help="Run in Fullscreen Mode")
args = parser.parse_args()

if not args.input:
    print("No input device specified. Printing list of input devices now: ")
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print("Device number (%i): %s" % (i, p.get_device_info_by_index(i).get('name')))
    print("Run this program with -input 1, or the number of the input you'd like to use.")
    exit()

#Initialise Pygame
pygame.init()

#Screensize by args
if args.f:
    screenWidth, screenHeight = 1024, 768
    screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

else:
    screenWidth, screenHeight = 800, 800
    screen = pygame.display.set_mode((screenWidth, screenHeight))

#Setting color variables (for random function)
white = (255, 255, 255)
black = (0, 0, 0)

#defining Circle class - position, size, color, speed of shrink
class Rectangle(object):
    def __init__(self, x, y, color, size):
        self.x = x
        self.y = y
        self.color = color
        self.size = size

    def shrink(self):
        self.size -= 5

colors = [(229, 244, 227), (93, 190, 233), (0, 0, 145), (25, 255, 255), (10, 50, 109)]
rectangleList = []

# initialise pyaudio
p = pyaudio.PyAudio()

clock = pygame.time.Clock()

# open stream

buffer_size = 4096 # needed to change this to get undistorted audio
pyaudio_format = pyaudio.paFloat32
n_channels = 1
samplerate = 44100
stream = p.open(format=pyaudio_format,
                channels=n_channels,
                rate=samplerate,
                input=True,
                input_device_index=args.input,
                frames_per_buffer=buffer_size)

time.sleep(1)

# setup onset detector
tolerance = 0.8
win_s = 4096 # fft size
hop_s = buffer_size // 2 # hop size
onset = aubio.onset("default", win_s, hop_s, samplerate)

q = queue.Queue()

def draw_pygame():
    running = True
    while running:
        key = pygame.key.get_pressed()

        if key[pygame.K_q]:
            running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

#if event in queue generate new rectangle and append to rectangleList
        if not q.empty():
            binpyt = q.get()
            newrectangle = Rectangle(random.randint(0, screenWidth), random.randint(0, screenHeight),
                               random.choice(colors), 300)
            rectangleList.append(newrectangle)

        screen.fill(white)
        for place, rectangle in enumerate(rectangleList):
            if rectangle.size < 1:
                rectangleList.pop(place)
            else:
                #pygame.draw.rect(screen, rectangle.color, (rectangle.x, rectangle.y), rectangle.size)
                pygame.draw.rect(screen, rectangle.color, [rectangle.x, rectangle.y, 50, 20])
                #pygame.draw.line(screen, black, [0, 0], [50,30], 5)
                #pygame.draw.rect(screen, black, [150, 10, 50, 20])
            rectangle.shrink()

        pygame.display.flip()
        clock.tick(90)

def get_onsets():
    while True:
        try:
            buffer_size = 2048 # needed to change this to get undistorted audio
            audiobuffer = stream.read(buffer_size, exception_on_overflow=False)
            signal = np.fromstring(audiobuffer, dtype=np.float32)


            if onset(signal):
                q.put(True)

        except KeyboardInterrupt:
            print("*** Ctrl+C pressed, exiting")
            break


t = Thread(target=get_onsets, args=())
t.daemon = True
t.start()

draw_pygame()
stream.stop_stream()
stream.close()
pygame.display.quit()
