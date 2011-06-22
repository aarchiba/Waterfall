#!/usr/bin/env python
import sys

import pygame
import pygame.surfarray as surfarray
from pygame import Surface, Rect
from pygame.transform import smoothscale
import numpy as np
import pyaudio

inp = None
fft_size = 8192
periodsize = 128
step_periods = 8

def setup_audio():
    global inp
    inp = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=48000,
            input=True,
            frames_per_buffer=periodsize,
            )

def get_more_audio():
    data = np.fromstring(inp.read(periodsize), dtype=np.int16)
    return data

def get_fft():
    l = []
    while True:
        while len(l)<fft_size/periodsize:
            l.append(get_more_audio())
        ts = np.concatenate(l)
        # Hamming window
        f = np.fft.rfft(ts*
                (0.54-0.46*np.cos(2*np.pi*np.arange(len(ts))/len(ts))))
        yield f
        l = l[step_periods:]

class Waterfall:
    def __init__(self, size, top_freq=1000., markers=[], sample_rate=44100.):
        self.size = size
        self.surface = Surface(size)
        w, h = size
        self.markers = markers
        self.top_freq = top_freq
        self.sample_rate=sample_rate

    def add_spectrum(self, f):
        self.surface.scroll(dx=-1)
        draw_area = Surface((1,len(f)),depth=24)
        d = surfarray.pixels3d(draw_area)
        a = (255*f/np.amax(f)).astype(np.uint8)
        d[0,:,:] = a[::-1,np.newaxis]
        for m in self.markers:
            im = int((2*m/self.sample_rate)*len(f))
            d[0,-im,0] = 255
        del d
        it = int((2*self.top_freq/self.sample_rate)*len(f))
        self.surface.blit(smoothscale(draw_area.subsurface((0,len(f)-it-1,1,it)), (1,self.size[1])),(self.size[0]-1,0))




if __name__=='__main__':
    setup_audio()
    pygame.init()
    screen = pygame.display.set_mode((768,512), pygame.RESIZABLE)
    markers = [175., 220.]
    top_freq = 1375.
    W = Waterfall((768,512), markers=markers, top_freq=top_freq)
    pygame.display.set_caption("spectroscope")
    clock = pygame.time.Clock()
    for f in get_fft():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
                W = Waterfall((event.w, event.h), markers=markers, top_freq=top_freq)
        screen.fill((0,0,0))
        fa = np.abs(f)

        W.add_spectrum(fa)
        screen.blit(W.surface,(0,0))
        pygame.display.flip()
