# Alpha++: ambient electronica style guide

**Games:** Alpha++ (a modern city builder for Mac, Early Access 2027) and its family:
**Airports**, **Ports** and **Rail Yards**.

**Visual context:** realistic and grounded rather than neon: golden-hour skylines, suburban
streets at night, airports at dusk, container yards. The same scenes are shown at day, dusk
and night.

**Direction:** modern ambient electronica, sometimes called "systems music". It should feel
calm and modern, like everything is running smoothly, and never retro or flashy. Interlocking
patterns that phase against each other evoke traffic, conveyors and schedules.

## Sound palette

| Part | Instrument function | Notes |
|---|---|---|
| Mallets | `mallet` | FM 1:4 marimba/vibe. Part A: a 7-hit 16th figure panned left. Part B: every 3 16ths, an octave up, panned right (polyrhythmic phasing) |
| Pads | `soft_pad` | Detuned triangles, LP 1100–1400 Hz, slow swell. The warm version adds a sine an octave below |
| Bass | `bass` | Sine plus a decaying 2nd harmonic, soft tanh. Root, a push on the "and" of 2, a fifth or octave pickup |
| Melody | `bell` / `vibe` / `kalimba` / `flute` | Enters in the third section only. Choose with `MELODY=` |
| Percussion | `shaker`, `kick`, `rim` | Shaker throughout, soft kick from bar 5, rimclick on 2 and 4 from section 2. **No snare** |

## Tracks

| Track | Script | Key / progression | BPM | Status |
|---|---|---|---|---|
| Golden Hour | `scripts/golden_hour.py` | F major: Fmaj9 Am7 B♭maj7 Csus2, Fmaj9 Dm7 B♭maj7 C | 96 | First test; asked to be "a little warmer" |
| Golden Hour (Warm) | `scripts/golden_hour_warm.py` | same | 96 | Warmer mix (1–4 kHz about -3 dB). Four melody voices: `golden_hour_warm_{bell,vibe,kalimba,flute}.ogg` |

Feedback so far: the FM bells were "just OK, not great", so vibe, kalimba and flute
alternatives were made, and a final choice is pending. All four share an identical backing
track, so they can rotate in-game as variations.

Render one voice with `MELODY=vibe python3 alphapp/scripts/golden_hour_warm.py`.

## Planned: one family, a different flavour per game

Share the palette above across all four games so they feel like one series:

- **Alpha++ (city):** warm and optimistic: plucks, mallets, a soft beat (Golden Hour).
- **Airports:** airy and spacious, with wide pads and gentle chime-like tones, like a calm terminal.
- **Ports:** deeper and slower, with low drones, open-water space and a subtle sea-wash noise texture.
- **Rail Yards:** the most rhythmic, with chugging pulses and interlocking mechanical patterns.

Consider day and night versions of each to match the game's lighting cycle.
