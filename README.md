# music

Procedurally generated soundtracks for Contraflow Games' city builders. A Python script
synthesizes each track from scratch (oscillators, filters, noise), with no samples, so all
audio is original. Every track is a seamless, game-ready loop.

**Agents making new tracks: start with [AGENTS.md](AGENTS.md).**

## Catalog

| Game | Track | Style | Key | BPM | Length | File |
|---|---|---|---|---|---|---|
| NeCity | Neon Grid | Synthwave, moody, driving | A minor | 100 | 57.6 s | `necity/tracks/neon_grid.ogg` |
| NeCity | Skyline Rising | Synthwave, hopeful | D major | 100 | 57.6 s | `necity/tracks/skyline_rising.ogg` |
| NeCity | Neon Grid (Calm) | Dreamwave, relaxed | A minor | 84 | 68.6 s | `necity/tracks/neon_grid_calm.ogg` |
| Alpha++ | Golden Hour | Ambient electronica | F major | 96 | 60.0 s | `alphapp/tracks/golden_hour.ogg` |
| Alpha++ | Golden Hour (Warm) ×4 | Ambient electronica, warmer; melody voice: bell, vibe, kalimba or flute | F major | 96 | 60.0 s | `alphapp/tracks/golden_hour_warm_*.ogg` |

All tracks: OGG Vorbis q6, 44.1 kHz stereo, -18 LUFS, sample-exact loop length.
Style guides: [necity/README.md](necity/README.md), [alphapp/README.md](alphapp/README.md).

## Rebuild

```bash
pip install -r requirements.txt   # plus ffmpeg with libvorbis
bash tools/build_all.sh           # deterministic: reproduces the committed OGGs
```

WAV masters are written to `build/` (git-ignored).
