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
- **Architecture Expansion**: Initiated the design for a dual-track real-time system, planning an audio-to-MIDI transcription pipeline (using `sigmund~`) to convert hummed vocal motifs into synchronized piano notes.

## 9/10
Max Patch Logic Refinement: Optimized the data control flow by introducing a gate module to manage the index data stream, ensuring that scale configurations (coll scale_map) are fully loaded and injected via store messages before hand-gesture coordinate signals are allowed to pass.

Workflow Strategy Evolution: Evaluated the acoustic limitations of real-time audio-rate pitch shifting on the human voice (such as formant smearing and metallic artifacts) and established a forward-looking architectural pivot toward instrument synthesis, pitch tracking, and automated MIDI/five-line staff notation (五线谱) export for future compositional workflows.


## Problems & Solutions
- **Audio Engine / Groove Error**: Experienced severe static/noise artifacts when using `groove~` during recording playback, which was resolved by restarting Max.
- **Sharp Transposed Audio**: Addressed high-frequency distortion and overly sharp pitch-shifted audio by replacing linear scaling with logarithmic frequency ratio calculations (`expr pow(2., $f1 / 12. )`) and symmetric range clipping (`clip -5 5`).
- **Gesture Jitter & Instability**: Eliminated erratic pitch fluctuations caused by minor MediaPipe tracking tremors by inserting a `change` object to filter and stabilize incoming semitone values.
- **Pitch-Shifted Melody Distortion**: Noticed distortion and phase artifacts during large pitch shifts, prompting evaluation of advanced pitch-shifting objects (`gizmo~`) and parameter tuning.
