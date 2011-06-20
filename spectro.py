
import numpy as np
import alsaaudio

inp = None
fft_size = 4096
periodsize = 128
step_periods = 8

def setup_audio():
    card = 'default'
    global inp
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, 0, card)
    inp.setchannels(1)
    inp.setrate(44100)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(periodsize)

def get_more_audio():
    l, data = inp.read()
    data = np.fromstring(data, dtype=np.int16)
    return data

def get_fft():
    l = []
    while True:
        while len(l)<fft_size/periodsize:
            l.append(get_more_audio())
        ts = np.concatenate(l)
        f = np.fft.rfft(ts)
        yield f
        l = l[step_periods:]

if __name__=='__main__':
    setup_audio()
    x, m, a = 0, 0, 0
    for f in get_fft():
        fa = np.abs(f)
        x = max(x, np.amax(fa))
        m = max(m, np.median(fa))
        a = max(a, np.mean(fa))
        print x, m, a
