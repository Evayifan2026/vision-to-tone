# Iteration Log

## 9/1
- Developed the initial project concept and implementation goals, focusing on capturing hummed vocal motifs via Max/MSP live recording and integrating MediaPipe gesture controls to dynamically transpose the motifs into C Major and C Minor modes.

## 9/2
- Installed MediaPipe, set up the Python environment and Max/MSP software, and established the GitHub repository for version control.

## 9/3
- Installed Visual Studio Code, set up the local project repository, and wrote a Python script to automatically generate the project's directory structure with a single click.

## 9/5-9/7
- Debugged and established successful communication between MediaPipe and Max/MSP, ensuring reliable OSC signal transmission and connection.

## 9/8
- Drafted the initial version of the project README.

## 9/9
- Completed the implementation of real-time vocal loop recording and gesture-driven pitch transposition in Max/MSP, utilizing logarithmic frequency scaling, jitter suppression, and symmetric transposition ranges to stabilize vocal timbre across modes.
- **Pitch Control Fix**: Swapped out direct integer mapping for a logarithmic frequency ratio formula (`expr pow(2., $f1 / 12. )`) connected via `sig~`, converting raw semitone indices into natural pitch ratios and eliminating high-frequency aliasing artifacts.
- **Jitter & Range Stabilization**: Inserted a `change` object to filter out MediaPipe gesture jitter and constrained the pitch transposition range using `clip -5 5` to maintain a natural vocal timbre centered around the root note.

## 9/10
- Max Patch Logic Refinement: Optimized the data control flow by introducing a gate module to manage the index data stream, ensuring that scale configurations are fully loaded before hand-gesture coordinate signals are allowed to pass.
- Workflow Strategy Evolution: Evaluated acoustic limitations of audio-rate pitch shifting and established a forward-looking architectural pivot toward instrument synthesis and automated MIDI export.

## 9/12 - 9/15 (Mid-September Finalization & Polish)
- **OSC Emotional & Key Mapping Expansion**: Extended Python-side MediaPipe gesture classification to stream multi-dimensional OSC control signals (`/current_key`, `/current_chord`, `/current_expression`) over UDP Port 8001.
- **Audio-Visual 3D Stage Synchronization**: Integrated Max/MSP's OpenGL environment (`jit.gl.render` and `erase_color`), dynamically shifting background colors (warm amber for *Happy*, deep indigo for *Sad*) based on real-time emotion state.
- **Expressive Phrasing & Dynamic Envelope**: Added software-side amplitude envelope processing (fade-in and fade-out linear curves) in Python/DSP audio rendering to eliminate mechanical digital clicks and emulate a natural "crescendo/decrescendo" (弱起弱收) human vocal expression.
- **Asset Structure & Environment Setup**: Finalized project repository layout, establishing a dedicated `src/audio_assets/` directory for audio loops and setting up a comprehensive `requirements.txt` containing all Python extension dependencies (`mediapipe`, `opencv-python`, `python-osc`, `numpy`).

---

## Problems & Solutions
- **Audio Engine / Groove Error**: Experienced severe static/noise artifacts when using `groove~` during recording playback, which was resolved by restarting Max and migrating to robust sample playback paths.
- **Sharp Transposed Audio**: Addressed high-frequency distortion by replacing linear scaling with logarithmic frequency ratio calculations and symmetric range clipping.
- **Mechanical Sound & Sudden Cuts**: Eliminated abrupt audio file clipping and robotic attack/release by implementing linear amplitude envelope buffers (fade-in/fade-out) during audio generation.
- **Asset Location & Loading Mismatch**: Standardized the `src/audio_assets/` folder tree structure so that Max/MSP (`sfplay~`) and Python scripts locate audio sample paths consistently across local environments.