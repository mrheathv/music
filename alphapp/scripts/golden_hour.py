"""Procedural ambient-electronica track for Alpha++ (city): "Golden Hour" (test).

FM mallets, soft pads, sine bass, FM bells and light electronic percussion.
Seamless loop: note tails are wrapped to the loop start and all effects run on
a doubled buffer whose second copy is kept.
"""
import numpy as np
import soundfile as sf
from scipy import signal
from pathlib import Path

BUILD = Path(__file__).resolve().parents[2] / "build"   # repo-level, git-ignored
BUILD.mkdir(exist_ok=True)

SR = 44100
BPM = 96
BEAT = 60 / BPM
STEP = BEAT / 4
BARS = 24
LOOP = BARS * 4 * BEAT
N = int(round(LOOP * SR))
TOTAL = N + 8 * SR
rng = np.random.default_rng(23)
OUT = BUILD / "golden_hour_raw.wav"


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tb(bar, step=0):
    return (bar * 16 + step) * STEP


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR * 0.45) / (SR / 2), "low")
    return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x, axis=0)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x, axis=0)


def add(buf, sig, t, pan=0.0):
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)], axis=1) * np.sqrt(2)
    i = int(round(t * SR))
    if i < 0:
        i += N
    end = min(len(buf), i + len(sig))
    buf[i:end] += sig[: end - i]


def tvec(secs):
    return np.arange(int(secs * SR)) / SR


# ------------------------------------------------------------- instruments
def mallet(m, vel=1.0):
    """FM marimba/vibe: 1:4 ratio, fast-decaying index, woody attack."""
    f = mtof(m)
    t = tvec(1.4)
    idx = 2.2 * np.exp(-t * 14) * vel
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * 4 * f * t))
    body = np.sin(2 * np.pi * f * t) * 0.35
    env = np.exp(-t * (3.2 + (m - 60) * 0.06)) * np.clip(t / 0.002, 0, 1)
    return lp((x + body) * env, 6500) * vel


def bell(m, dur, vel=1.0):
    """FM bell: inharmonic 1:3.5 ratio, long ring."""
    f = mtof(m)
    t = tvec(dur + 3.0)
    idx = 2.4 * np.exp(-t * 1.6)
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * 3.5 * f * t))
    x += 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 2.5)
    env = np.exp(-t * 0.9) * np.clip(t / 0.003, 0, 1)
    return lp(x * env, 7000) * vel


def soft_pad(notes, dur):
    """Rounded pad: detuned triangles + a little filtered saw, slow swell."""
    t = tvec(dur + 1.8)
    n = len(t)
    out = np.zeros((n, 2))
    for m in notes:
        f = mtof(m)
        for d, p in ((-0.004, -0.7), (0.0, 0.0), (0.004, 0.7)):
            ph = rng.random()
            tri = 2 * np.abs(2 * ((f * (1 + d) * t + ph) % 1) - 1) - 1
            a = (p + 1) * np.pi / 4
            out[:, 0] += tri * np.cos(a) * 0.12
            out[:, 1] += tri * np.sin(a) * 0.12
    out = lp(out, 1400, 2)
    att, rel = 0.9, 1.6
    env = np.clip(t / att, 0, 1) * np.clip(1 - (t - dur) / rel, 0, 1)
    return out * env[:, None]


def bass(m, dur, vel=1.0):
    f = mtof(m)
    t = tvec(dur + 0.2)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6)
    env = np.clip(t / 0.01, 0, 1) * np.exp(-t * 0.8) * np.clip(1 - (t - dur) / 0.15, 0, 1)
    return np.tanh(1.2 * x) * env * vel


def kick(vel=1.0):
    t = tvec(0.4)
    f = 50 + 70 * np.exp(-t * 35)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    return x * vel


def rim(vel=1.0):
    t = tvec(0.12)
    tone = np.sin(2 * np.pi * 820 * t) * np.exp(-t * 60)
    click = bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 90)
    return (tone * 0.6 + click * 0.5) * vel


def shaker(vel=1.0):
    t = tvec(0.09)
    x = bp(rng.standard_normal(len(t)), 5000, 12000)
    env = np.clip(t / 0.012, 0, 1) * np.exp(-t * 45)
    return x * env * vel


# ------------------------------------------------------------- composition
CH = {  # bass, pad voicing
    "Fmaj9":   (41, [53, 60, 64, 67]),
    "Am7":     (45, [52, 57, 60, 67]),
    "Bbmaj7":  (46, [53, 57, 62, 65]),
    "Csus2":   (36, [55, 60, 62, 67]),
    "Dm7":     (38, [53, 57, 60, 64]),
    "C":       (36, [55, 60, 64, 67]),
}
PROG = ["Fmaj9", "Am7", "Bbmaj7", "Csus2", "Fmaj9", "Dm7", "Bbmaj7", "C"]

MALLET_A = [(0, 0), (2, 1), (4, 2), (7, 3), (10, 1), (12, 2), (14, 0)]   # (step, chord tone)
MALLET_B = [(1, 1), (4, 2), (7, 3), (10, 2), (13, 1)]                   # every 3 16ths

BELLS = [
    [(0, 79, 8), (8, 77, 8)],
    [(0, 76, 12), (12, 72, 4)],
    [(0, 74, 8), (8, 77, 8)],
    [(0, 79, 16)],
    [(0, 81, 8), (8, 79, 4), (12, 77, 4)],
    [(0, 77, 8), (8, 76, 8)],
    [(0, 74, 6), (6, 72, 2), (8, 74, 8)],
    [(0, 72, 16)],
]

pad = np.zeros((TOTAL, 2))
bas = np.zeros((TOTAL, 2))
mal = np.zeros((TOTAL, 2))
bel = np.zeros((TOTAL, 2))
drm = np.zeros((TOTAL, 2))
kicks = []

for bar in range(BARS):
    sec = bar // 8
    root, voicing = CH[PROG[bar % 8]]
    t0 = tb(bar)
    tones = [m + 12 for m in voicing]

    add(pad, soft_pad(voicing, 4 * BEAT - 0.1), t0)

    # bass: root on 1, a soft push on the "and" of 2, fifth/octave pickup
    add(bas, bass(root, 5.5 * STEP, 0.9), t0)
    add(bas, bass(root, 3.5 * STEP, 0.6), t0 + 6 * STEP)
    add(bas, bass(root + (7 if bar % 2 == 0 else 12), 2.5 * STEP, 0.5), t0 + 12 * STEP)

    for s, k in MALLET_A:
        v = (0.55 if s % 4 == 0 else 0.42) * rng.uniform(0.9, 1.0)
        add(mal, mallet(tones[k], v), t0 + s * STEP + rng.normal(0, 0.002), pan=-0.45)
    if sec >= 1 or bar >= 4:
        for s, k in MALLET_B:
            v = 0.32 * rng.uniform(0.85, 1.0)
            add(mal, mallet(tones[k] + 12, v), t0 + s * STEP + rng.normal(0, 0.002), pan=0.5)

    if sec == 2:
        for s, m, l in BELLS[bar % 8]:
            add(bel, bell(m, l * STEP, 0.35), t0 + s * STEP, pan=0.15)

    # percussion
    last = bar == BARS - 1
    for s in range(16):
        accent = 0.12 if s % 4 == 2 else (0.07 if s % 2 == 0 else 0.045)
        add(drm, shaker(accent * rng.uniform(0.8, 1.1)), t0 + s * STEP + rng.normal(0, 0.003), pan=0.35)
    if bar >= 4:
        ks = [0, 8] + ([14] if bar % 2 == 1 else []) + ([10] if sec == 2 else [])
        for s in ks:
            if last and s >= 12:
                continue
            add(drm, kick(0.8 if s in (0, 8) else 0.55), t0 + s * STEP)
            kicks.append(t0 + s * STEP)
    if sec >= 1:
        for s in (4, 12):
            add(drm, rim(0.32), t0 + s * STEP + 0.006, pan=-0.2)


# --------------------------------------------------------------- loop + FX
def loopify(x):
    y = x[:N].copy()
    y[: len(x) - N] += x[N:]
    return np.concatenate([y, y])


pad, bas, mal, bel, drm = map(loopify, (pad, bas, mal, bel, drm))
kick_idx = [int(round(k * SR)) % N for k in kicks]
kick_idx += [i + N for i in kick_idx]
T2 = 2 * N


def sidechain(depth, release=0.2):
    env = np.ones(T2)
    t = np.arange(int(0.4 * SR)) / SR
    shape = 1 - depth * np.exp(-t / release * 3)
    for i in kick_idx:
        e = min(T2, i + len(shape))
        env[i:e] = np.minimum(env[i:e], shape[: e - i])
    return env[:, None]


def pingpong(x, delay, fb=0.4, taps=6, tone=3500):
    out = np.zeros_like(x)
    d = int(delay * SR)
    mono = x.mean(axis=1)
    for k in range(1, taps + 1):
        out[k * d:, (k + 1) % 2] += mono[: T2 - k * d] * fb ** k
    return lp(out, tone)


def reverb(x, secs=3.5, decay=2.0, damp=5000):
    n = int(secs * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    for c in range(2):
        ir = lp(rng.standard_normal(n), damp) * np.exp(-t * decay)
        ir[: int(0.02 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, c] = signal.fftconvolve(x[:, c], ir)[:T2]
    return out


pad = pad * sidechain(0.2)
bas = bas * sidechain(0.3, 0.12)

mal_bus = mal + pingpong(mal, 3 * STEP, 0.3, tone=4000) * 0.7
bel_bus = bel + pingpong(bel, 6 * STEP, 0.35, tone=3500)

dry = 0.50 * pad + 0.45 * bas + 0.40 * mal_bus + 0.40 * bel_bus + 0.55 * drm
send = 0.35 * pad + 0.25 * mal_bus + 0.45 * bel_bus + 0.10 * drm
mix = dry + reverb(send) * 0.6

mix = hp(mix, 30, 2)
mix = mix / np.max(np.abs(mix)) * 0.85
mix = np.tanh(1.1 * mix) / np.tanh(1.1)

out = mix[N:].copy()
seam_err = np.max(np.abs(mix[N - 4000:N] - mix[2 * N - 4000:2 * N]))
print(f"seam check: {seam_err:.2e}")
out = out / np.max(np.abs(out)) * 0.89
sf.write(OUT, out, SR, subtype="PCM_24")
print(f"loop {LOOP:.2f}s, {N} samples")
