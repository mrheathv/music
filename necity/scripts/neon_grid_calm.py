"""Procedural synthwave track: "Neon Grid (Calm)" - dreamwave variant.

All sounds are synthesized (band-limited oscillators, filters, noise).
Seamless loop: note tails are wrapped to the loop start and every effect runs
on a doubled buffer whose second copy is kept.
"""
import numpy as np
import soundfile as sf
from scipy import signal
from pathlib import Path

BUILD = Path(__file__).resolve().parents[2] / "build"   # repo-level, git-ignored
BUILD.mkdir(exist_ok=True)

SR = 44100
BPM = 84
BEAT = 60 / BPM
STEP = BEAT / 4
BARS = 24
LOOP = BARS * 4 * BEAT
N = int(round(LOOP * SR))
TOTAL = N + 6 * SR
rng = np.random.default_rng(11)


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
    """Add mono (panned, equal power) or stereo signal at time t."""
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)], axis=1) * np.sqrt(2)
    i = int(round(t * SR))
    if i < 0:
        i += N                      # wraps into the loop (tail is folded later)
    end = min(len(buf), i + len(sig))
    buf[i:end] += sig[: end - i]


# --------------------------------------------------------- band-limited osc
def _blep(ph, dt):
    """PolyBLEP residual (removes aliasing at saw discontinuities)."""
    r = np.zeros_like(ph)
    m = ph < dt
    x = ph[m] / dt[m]
    r[m] = x + x - x * x - 1
    m = ph > 1 - dt
    x = (ph[m] - 1) / dt[m]
    r[m] = x * x + x + x + 1
    return r


def saw(freq, n, phase0=0.0):
    """freq: scalar or per-sample array."""
    dt = np.broadcast_to(np.asarray(freq, float) / SR, (n,)).copy()
    ph = (phase0 + np.cumsum(dt)) % 1.0
    return 2 * ph - 1 - _blep(ph, dt)


def pulse(freq, n, width=0.5, phase0=0.0):
    dt = np.broadcast_to(np.asarray(freq, float) / SR, (n,)).copy()
    ph = (phase0 + np.cumsum(dt)) % 1.0
    ph2 = (ph + width) % 1.0
    a = 2 * ph - 1 - _blep(ph, dt)
    b = 2 * ph2 - 1 - _blep(ph2, dt)
    return (a - b) * 0.5


def adsr(n, a, d, s, r, gate):
    t = np.arange(n) / SR
    env = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip(1 - (t - gate) / max(r, 1e-4), 0, 1)
    return env * np.where(t > gate, rel, 1.0)


# ------------------------------------------------------------- instruments
def supersaw_pad(notes, dur):
    """7-voice detuned saw per note, voices spread across stereo."""
    n = int((dur + 1.2) * SR)
    out = np.zeros((n, 2))
    det = np.array([-0.011, -0.0065, -0.003, 0, 0.003, 0.0065, 0.011])
    pans = np.array([-0.9, 0.6, -0.4, 0, 0.4, -0.6, 0.9])
    for m in notes:
        f = mtof(m)
        for d, p in zip(det, pans):
            v = saw(f * (1 + d), n, rng.random()) * 0.14
            a = (p + 1) * np.pi / 4
            out[:, 0] += v * np.cos(a)
            out[:, 1] += v * np.sin(a)
    out = lp(out, 1700, 2)
    return out * adsr(n, 0.9, 1.5, 0.85, 1.2, dur)[:, None]


def bass(m, dur, vel=1.0):
    n = int((dur + 0.08) * SR)
    f = mtof(m)
    x = saw(f, n, 0) * 0.7 + pulse(f * 1.004, n) * 0.4
    env = adsr(n, 0.02, 0.6, 0.7, 0.25, dur)
    fenv = np.exp(-np.arange(n) / SR / 0.07)
    dark, bright = lp(x, 220, 2), lp(x, 700, 2)
    y = dark * (1 - fenv) + bright * fenv     # filter "pluck"
    return np.tanh(1.5 * y) * env * vel


def arp_note(m, vel=1.0):
    n = int(0.35 * SR)
    x = pulse(mtof(m), n, 0.3)
    y = lp(x, 2200, 2) * adsr(n, 0.006, 0.18, 0.0, 0.1, 0.2)
    return y * vel


def lead(m, dur, vel=1.0, prev=None):
    n = int((dur + 0.5) * SR)
    t = np.arange(n) / SR
    f = np.full(n, mtof(m))
    if prev is not None:                      # short glide from previous note
        g = np.exp(-t / 0.035)
        f = mtof(m) * (mtof(prev) / mtof(m)) ** g
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.3) / 0.4, 0, 1)
    x = saw(f * vib, n) * 0.6 + pulse(f * vib * 1.003, n, 0.5) * 0.4
    x = lp(x, 1600, 2)
    return x * adsr(n, 0.06, 0.6, 0.7, 0.6, dur) * vel


def kick(vel=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    click = hp(rng.standard_normal(n), 2000) * np.exp(-t * 400) * 0.3
    return np.tanh(2.0 * (x + click)) * vel


def snare_gated(vel=1.0):  # softer gate in calm mix
    """80s snare: body + noise, plus a dense 'room' that is hard-gated."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.7
    crack = bp(rng.standard_normal(n), 1200, 8000) * np.exp(-t * 22)
    room = lp(rng.standard_normal((n, 2)), 4500) * 0.22
    gate = np.where(t < 0.26, np.exp(-t * 2.5), np.exp(-0.26 * 2.5) * np.exp(-(t - 0.26) * 120))
    room *= gate[:, None] * np.clip(t / 0.008, 0, 1)[:, None]
    dry = (body + crack)[:, None]
    return (dry + room) * vel


def hat(vel=1.0, open_=False):
    n = int((0.4 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 8000, 4) * np.exp(-t * (8 if open_ else 80)) * vel


def tom(f0, vel=1.0):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.5 * np.exp(-t * 18))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    return np.tanh(1.5 * x) * vel


def crash(vel=1.0):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    x = hp(rng.standard_normal((n, 2)), 5000, 2) * np.exp(-t * 2.2)[:, None]
    return x * vel


# ------------------------------------------------------------- composition
CH = {  # bass midi, pad voicing, arp notes
    "Am": (33, [57, 60, 64, 69], [69, 72, 76, 81]),
    "F":  (29, [57, 60, 65, 69], [65, 69, 72, 77]),
    "C":  (36, [55, 60, 64, 67], [67, 72, 76, 79]),
    "G":  (31, [55, 59, 62, 67], [67, 71, 74, 79]),
}
PROG = ["Am", "F", "C", "G", "Am", "F", "G", "G"]

PHRASE_A = [
    [(0, 76, 6), (6, 74, 2), (8, 72, 4), (12, 69, 4)],
    [(0, 72, 6), (6, 69, 2), (8, 69, 8)],
    [(0, 67, 4), (4, 72, 4), (8, 76, 8)],
    [(0, 74, 10), (12, 71, 4)],
    [(0, 72, 4), (4, 76, 4), (8, 81, 8)],
    [(0, 79, 4), (4, 77, 4), (8, 76, 8)],
    [(0, 74, 6), (6, 76, 2), (8, 74, 4), (12, 71, 4)],
    [(0, 71, 4), (4, 74, 12)],
]
PHRASE_B = PHRASE_A[:4] + [
    [(0, 81, 8), (8, 79, 4), (12, 76, 4)],
    [(0, 77, 8), (8, 76, 4), (12, 72, 4)],
    [(0, 74, 8), (8, 79, 8)],
    [(0, 76, 4), (4, 74, 4), (8, 71, 8)],
]

pad = np.zeros((TOTAL, 2))
bas = np.zeros((TOTAL, 2))
arp = np.zeros((TOTAL, 2))
ld = np.zeros((TOTAL, 2))
drm = np.zeros((TOTAL, 2))
kicks = []

for bar in range(BARS):
    sec = bar // 8                        # 0 = intro/groove, 1 = melody, 2 = melody variation
    root, voicing, arpn = CH[PROG[bar % 8]]
    t0 = tb(bar)

    add(pad, supersaw_pad(voicing, 4 * BEAT - 0.05) * (0.8 if sec == 0 else 1.0), t0)
    if sec == 2:
        add(pad, supersaw_pad([voicing[-1] + 12], 4 * BEAT - 0.05) * 0.35, t0)

    add(bas, bass(root, 9.5 * STEP, 1.0), t0)          # long, held bass notes
    add(bas, bass(root + 12 if bar % 2 else root, 5.5 * STEP, 0.7), t0 + 10 * STEP)

    order = [0, 1, 2, 3, 2, 1, 2, 3] * 2  # 16th arp pattern
    for s in range(0, 16, 2):
        v = (0.5 if s % 8 == 0 else 0.38) * (0.8 if sec == 0 else 1.0)
        add(arp, arp_note(arpn[order[s // 2]], v), t0 + s * STEP, pan=0.35 if s % 4 else -0.35)

    if sec >= 1:
        phrase = (PHRASE_A if sec == 1 else PHRASE_B)[bar % 8]
        prev = None
        for s, m, l in phrase:
            add(ld, lead(m, l * STEP * 0.95, 0.42, prev), t0 + s * STEP)
            prev = m

    # drums: half-time and soft
    intro = sec == 0 and bar < 4
    for st in ([0] if intro else [0, 6]):
        add(drm, kick(0.7 if st == 0 else 0.5), t0 + st * STEP)
        kicks.append(t0 + st * STEP)
    if not intro:
        add(drm, snare_gated(0.4), t0 + 2 * BEAT)
    for st in range(0, 16, 2):
        if intro and st % 4:
            continue
        add(drm, hat(0.08 if st % 4 == 2 else 0.05), t0 + st * STEP + rng.normal(0, 0.003), pan=0.3)
    if bar in (0, 8, 16):
        add(drm, crash(0.1), t0)


# --------------------------------------------------------------- loop + FX
def loopify(x):
    y = x[:N].copy()
    y[: len(x) - N] += x[N:]
    return np.concatenate([y, y])


pad, bas, arp, ld, drm = map(loopify, (pad, bas, arp, ld, drm))
kick_idx = [int(round(k * SR)) % N for k in kicks]
kick_idx += [i + N for i in kick_idx]
T2 = 2 * N


def sidechain(depth, release=0.18):
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
        ch = (k + 1) % 2
        out[k * d:, ch] += mono[: T2 - k * d] * fb ** k
    return lp(out, tone)


def reverb(x, secs=3.0, decay=2.4, damp=5000):
    n = int(secs * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    for c in range(2):
        ir = lp(rng.standard_normal(n), damp) * np.exp(-t * decay)
        ir[: int(0.012 * SR)] = 0               # pre-delay
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, c] = signal.fftconvolve(x[:, c], ir)[:T2]
    return out


pad = pad * sidechain(0.2)
bas = bas * sidechain(0.25, 0.12)
arp = arp * sidechain(0.1)

arp_bus = arp + pingpong(arp, 3 * STEP, 0.5, taps=8, tone=2200)          # dotted 8th echo
lead_bus = ld + pingpong(ld, 3 * STEP, 0.3, tone=2800) * 0.8

dry = 0.45 * pad + 0.42 * bas + 0.26 * arp_bus + 0.40 * lead_bus + 0.5 * drm
send = 0.40 * pad + 0.35 * arp_bus + 0.50 * lead_bus + 0.15 * drm
mix = dry + reverb(send, secs=4.5, decay=1.5, damp=3500) * 0.7

# slow stereo chorus-ish width on the whole thing is overkill; just tame & glue
mix = hp(mix, 32, 2)
mix = mix / np.max(np.abs(mix)) * 0.85
mix = np.tanh(1.15 * mix) / np.tanh(1.15)

out = mix[N:].copy()
seam_err = np.max(np.abs(mix[N - 4000:N] - mix[2 * N - 4000:2 * N]))
print(f"seam check: max diff between end of copy 1 and end of copy 2 = {seam_err:.2e}")
out = out / np.max(np.abs(out)) * 0.89
sf.write(BUILD / "neon_grid_calm_raw.wav", out, SR, subtype="PCM_24")
print(f"loop {LOOP:.2f}s, {N} samples")
