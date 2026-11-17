# NeCity: synthwave style guide

**Soundtrack:** one shared soundtrack for both games below; NeCity gets a few extra tracks of its own later.

**Games:** NeCity Lo-Fi (a gentle city builder about one small town; Mac Winter 2026, iPad
Spring 2027) and NeCity, pronounced "Neon City" (a city builder whose streets light up in neon
as they come alive).

**Visual context:** isometric blocks in magenta, purple and cyan on a glowing neon grid;
night streets full of neon signs. The art is essentially a synthwave album cover.

**Direction (approved):** synthwave at **100 BPM**: driving but not aggressive, minor or
hopeful keys. It sounded "way better" than lofi. A calmer 84 BPM version was "OK", but the
higher tempo was preferred, so keep 100 BPM as the base.

## Sound palette

| Part | Instrument function | Notes |
|---|---|---|
| Pads | `supersaw_pad` | 7 detuned PolyBLEP saws per note, spread across stereo, LP 2600 Hz, ducked by the kick |
| Bass | `bass` | Saw plus a unison pulse with a filter "pluck" (crossfade dark to bright), 8th notes, octave jumps |
| Arpeggio | `arp_note` | 30% pulse, LP 3800, 16ths, dotted-8th ping-pong delay |
| Lead | `lead` | Saw + pulse (Neon Grid) or 25% pulse + saw (Skyline Rising), vibrato, short glides |
| Drums | `kick`, `snare_gated`, `hat`, `tom`, `crash` | 80s drum machine, gated-reverb snare on 2 and 4, tom fill in the last bar |

Mix: `0.40 pad + 0.42 bass + 0.28 arp + 0.42 lead + 0.6 drums`, plus a reverb send, gentle
tanh glue. Bass roots sit around 43–65 Hz; don't add a sub an octave below the root.

## Tracks

| Track | Script | Key / progression | BPM | Length | Status |
|---|---|---|---|---|---|
| Neon Grid | `scripts/neon_grid.py` | A minor: Am F C G, Am F G G | 100 | 57.6 s | Approved direction (building theme 1) |
| Skyline Rising | `scripts/skyline_rising.py` | D major: G A F♯m Bm, G A D D | 100 | 57.6 s | Building theme 2, awaiting feedback |
| Neon Grid (Calm) | `scripts/neon_grid_calm.py` | as Neon Grid | 84 | 68.6 s | Optional: night or menus. Same chords, so it can crossfade |
| Signal Lights | `scripts/signal_lights.py` | E minor: Em C Am B, Em C D B | 100 | 57.6 s | Building theme 3 (mysterious), awaiting feedback |
| Afterglow | `scripts/afterglow.py` | D minor: Dm B♭ F C, Dm B♭ Gm A | 100 | 57.6 s | Night track: calm arrangement (half-time drums, held bass, darker pads) at 100 BPM. Awaiting feedback |
| Neon Horizon | `scripts/neon_horizon.py` | as Neon Grid | 100 | 57.6 s | Menu theme: the Neon Grid melody with almost no drums. Awaiting feedback |

## Planned

- Building track 4 (triumphant).
- A milestone sting, 5–10 seconds, for population tiers.
- Extra tracks for the bigger NeCity game.
- Stem exports for adaptive layering (quiet street to buzzing street).
