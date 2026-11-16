# CLAUDE.md

This repo generates the game soundtracks procedurally with Python. Before making or changing
any track, read and follow the full guide:

@AGENTS.md

Key rules in brief:
- Only synth-native styles (synthwave, ambient electronica, FM mallets/bells). Imitating acoustic instruments failed (see "What works and what doesn't").
- Every track: seamless loop at the file boundary, -18 LUFS, finalized with `tools/finalize.py`.
- You can't hear the output: run the seam check, finalize and band comparisons, report the numbers, and ask the person to listen.
- Commit scripts and OGGs only; `build/` and WAVs are git-ignored.
