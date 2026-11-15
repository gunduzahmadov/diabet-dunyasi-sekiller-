#!/usr/bin/env python3
"""Videoya sakit instrumental fon musiqisi əlavə edir (musiqi kodla sintez olunur, lisenziya tələb etmir).
İstifadə: python3 -I tools/fonmusiqi.py giris.mp4 cixis.mp4 [toxum]
toxum (məs. 20261115) akkord ardıcıllığını və tempi dəyişir ki, hər gün eyni səslənməsin.
Instagram musiqi kataloqu işləməyən hesablar (B, C) üçün nəzərdə tutulub.
"""
import sys, subprocess, tempfile, os, wave
import numpy as np

src, out = sys.argv[1], sys.argv[2]
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
rng = np.random.default_rng(seed)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src],
                           capture_output=True, text=True, check=True).stdout.strip())
SR = 44100
n = int(SR * (dur + 0.5))
t = np.arange(n) / SR
L = np.zeros(n); R = np.zeros(n)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def note(m, start, length, amp, pan):
    i0 = int(start * SR)
    if i0 >= n: return
    k = min(n - i0, int(length * SR))
    tt = np.arange(k) / SR
    f = hz(m)
    w = (np.sin(2*np.pi*f*tt) + .35*np.sin(4*np.pi*f*tt)*np.exp(-tt*3) + .12*np.sin(6*np.pi*f*tt)*np.exp(-tt*5))
    env = np.minimum(1, tt / .015) * np.exp(-tt * 1.6)
    s = w * env * amp
    L[i0:i0+k] += s * (1 - pan); R[i0:i0+k] += s * pan
def pad(ms, start, length, amp):
    i0 = int(start * SR); k = min(n - i0, int(length * SR))
    if k <= 0: return
    tt = np.arange(k) / SR
    env = np.minimum(1, tt / 1.2) * np.minimum(1, (length - tt) / 1.2).clip(0)
    s = sum(np.sin(2*np.pi*hz(m)*tt) + .5*np.sin(2*np.pi*hz(m)*1.003*tt) for m in ms) * env * amp
    L[i0:i0+k] += s; R[i0:i0+k] += s

progs = [[(60, 'M'), (57, 'm'), (53, 'M'), (55, 'M')], [(57, 'm'), (53, 'M'), (60, 'M'), (55, 'M')],
         [(62, 'm'), (55, 'M'), (60, 'M'), (57, 'm')], [(53, 'M'), (55, 'M'), (57, 'm'), (60, 'M')]]
prog = progs[seed % len(progs)]
bar = float(rng.choice([3.2, 3.6, 4.0]))
step = bar / 8
patt = [0, 1, 2, 3, 2, 1, 2, 3]
tm = 0.0; b = 0
while tm < dur:
    root, q = prog[b % 4]
    ch = [root, root + (4 if q == 'M' else 3), root + 7, root + 12]
    pad([root - 12, root - 5], tm, bar + 1.0, .045)
    note(root - 12, tm, bar, .16, .5)
    for j, p in enumerate(patt):
        note(ch[p] + (12 if b % 2 and j == 7 else 0), tm + j * step, step * 4, .11 + .02 * rng.random(), .3 + .4 * (p / 3))
    tm += bar; b += 1
# sadə reverb
for d, g in [(.11, .3), (.23, .2), (.37, .12)]:
    k = int(d * SR); L[k:] += g * R[:-k].copy(); R[k:] += g * L[:-k].copy()
fade = np.minimum(1, t / 1.0) * np.minimum(1, (dur - t) / 2.0).clip(0)
st = np.stack([L * fade, R * fade], 1)
st = st / np.abs(st).max() * 0.5
with tempfile.TemporaryDirectory() as w:
    wav = os.path.join(w, 'm.wav')
    with wave.open(wav, 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((st * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out], check=True)
print('OK', out, f'{dur:.1f}s')
