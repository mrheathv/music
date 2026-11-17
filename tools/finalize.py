#!/usr/bin/env python3
"""Finalize a rendered loop for the game, or compare tracks.

Finalize (raw render -> game-ready OGG, plus a 16-bit WAV master in build/):
    python tools/finalize.py build/neon_grid_raw.wav necity/tracks/neon_grid.ogg

Compare tonal balance / loudness of finished tracks (use this to keep a set consistent):
    python tools/finalize.py --compare necity/tracks/*.ogg

What finalize does, and checks:
  * gains the track to TARGET_LUFS (-18 LUFS integrated, the house standard)
  * refuses tracks whose true peak would exceed -1 dBTP
  * encodes OGG Vorbis q6 and verifies the OGG has exactly the same sample count
    as the raw render (the loop point is the file boundary, so this must match)
  * prints the frequency-band balance so you can compare against the reference table
Requires ffmpeg (with libvorbis) on PATH, plus numpy and soundfile.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

TARGET_LUFS = -18.0
MAX_TRUE_PEAK = -1.0
OGG_QUALITY = 6
BANDS = [(20, 60), (60, 250), (250, 1000), (1000, 4000), (4000, 8000), (8000, 20000)]
REPO = Path(__file__).resolve().parents[1]


def loudness(path):
    """Return (integrated LUFS, true peak dBFS) via ffmpeg's EBU R128 meter."""
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, check=True)
    summary = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1))
    p = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary).group(1))
    return i, p


def bands(path):
    x, sr = sf.read(str(path))
    m = x.mean(axis=1) if x.ndim > 1 else x
    spec = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1 / sr)
    tot = spec.sum()
    return [10 * np.log10(spec[(f >= lo) & (f < hi)].sum() / tot) for lo, hi in BANDS]


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


def finalize(raw, ogg):
    raw, ogg = Path(raw), Path(ogg)
    ogg.parent.mkdir(parents=True, exist_ok=True)
    build = REPO / "build"
    build.mkdir(exist_ok=True)
    wav = build / (ogg.stem + ".wav")

    frames = sf.info(str(raw)).frames
    i, p = loudness(raw)
    gain = TARGET_LUFS - i
    if p + gain > MAX_TRUE_PEAK:
        sys.exit(f"FAIL: true peak would be {p + gain:.1f} dBTP (> {MAX_TRUE_PEAK}); "
                 "tame transients in the script (lower drum levels / more saturation) and re-render.")
    ffmpeg("-i", raw, "-af", f"volume={gain:.2f}dB", "-c:a", "pcm_s16le", wav)
    ffmpeg("-i", wav, "-c:a", "libvorbis", "-q:a", OGG_QUALITY, ogg)

    for f in (wav, ogg):
        n = sf.info(str(f)).frames
        if n != frames:
            sys.exit(f"FAIL: {f.name} has {n} frames, raw render has {frames}; loop length changed.")
    fi, fp = loudness(ogg)
    sr = sf.info(str(ogg)).samplerate
    print(f"OK  {ogg}  {frames} frames ({frames / sr:.2f}s)  {fi:.1f} LUFS  peak {fp:.1f} dBFS")
    print(f"    master: {wav}")
    print_bands([ogg])


def print_bands(paths):
    rows = [(Path(p).stem, bands(p)) for p in paths]
    w = max(12, *(len(n) for n, _ in rows))
    print("    " + "band (Hz)".ljust(13) + "".join(n[:w].rjust(w + 2) for n, _ in rows))
    for k, (lo, hi) in enumerate(BANDS):
        print("    " + f"{lo}-{hi}".ljust(13) + "".join(f"{b[k]:>{w + 2}.1f}" for _, b in rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--compare", action="store_true", help="print loudness + band balance of finished tracks")
    a = ap.parse_args()
    if a.compare:
        for f in a.files:
            i, p = loudness(f)
            print(f"{Path(f).name:40s} {i:6.1f} LUFS  peak {p:6.1f} dBFS  {sf.info(f).frames} frames")
        print_bands(a.files)
    else:
        if len(a.files) != 2:
            ap.error("finalize takes: RAW_WAV OUTPUT_OGG")
        finalize(*a.files)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:      # output piped into `head` etc.; the work is already done
        sys.stderr.close()
