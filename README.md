# 🎵 VisionToTone: AI-Powered Gesture-Controlled Vocal Pitch Shifter & Composition Assistant

An interactive music prototyping tool that bridges computer vision, real-time OSC communication, and Digital Signal Processing (DSP) in Max/MSP to assist vocalists and composers in real-time melody sketching and pitch shifting.

## 🚀 Project Overview
VisionToTone allows a composer to use intuitive webcam-based hand gestures (tracked via Google MediaPipe) to control real-time vocal pitch-shifting, chord harmonization, and dynamic expression mapping while humming melodies into Max/MSP via UDP/OSC.

- **Target Application**: Music Technology, Computer Science & Creative Arts (intended for US Top 10 University Admissions portfolio).
- **Developer**: Eva Wang (Grade 9 Student Developer).
- **Project Status**: **Final Version Released (定版)**

---

## 🏗️ System Architecture & Tech Stack

```text
[Webcam Feed] 
      │
      ▼
[Python + MediaPipe + OpenCV] ──(Hand Landmark Detection & Expression Classification)
      │
      ▼ (OSC Protocol over UDP - Port 8001)
[Max / MSP] 
      │
      ├── Audio Input & Dynamic Envelope (Fade-in/Fade-out for Expressive Phrasing)
      ├── OSC Routing (/current_key, /current_chord, /current_expression)
      ├── Real-time 3D Stage Background Color Sync (Happy / Sad Emotional Mapping)
      └── Audio Output & Reverb Processing (Bpatcher bp.Reverb)
```

### Core Technologies
- **Programming Language**: Python 3.10+
- **Computer Vision & Protocols**: MediaPipe, OpenCV (`opencv-python`), `python-osc`, NumPy
- **Audio Engineering Environment**: Max/MSP 8.x (Bpatchers, OSC routing, `sfplay~`, `jit.gl.render`, `jit.gl.graph`)

---

## 📁 Repository & Audio Asset Structure
To ensure Max/MSP's `sfplay~` and Python scripts can successfully locate and play audio files, the project assets are organized under the following directory structure:

```text
vision-to-tone/
├── src/
│   ├── python/                # Python vision tracking & OSC client scripts
│   ├── max_msp/               # Max/MSP patches (.maxpat)
│   └── audio_assets/          # 🎵 Directory for audio samples & generated WAV files
│       ├── C_Major_loop.wav   # Pre-recorded vocal/instrument loops for C Major
│       ├── Ab_Maj_loop.wav    # Pre-recorded loops for Ab Major
│       └── dynamic_sketches/  # Python-generated or exported audio sketches
```

---

## ✨ Key Features Implemented (Final Version)
1. **Real-time Computer Vision & Expression Mapping**: High-fps hand tracking utilizing Google MediaPipe, dynamically classifying gestures into musical keys and emotional states (`Happy` / `Sad`).
2. **Low-Latency OSC Bridge**: Streams continuous control data (key, chord, and expression state) from Python to Max/MSP over UDP (Port 8001).
3. **Audio-Visual Emotional Synchronization**: Automatically shifts the 3D stage background color (`erase_color`) in Max/MSP's OpenGL window based on the user's real-time emotional expression.
4. **Natural Expressive Phrasing (Dynamic Envelope)**: Implemented software-side amplitude envelopes (fade-in / fade-out) in Python audio generation to eliminate mechanical clicks and provide a natural "crescendo/decrescendo" vocal phrasing feel.

---

## ⚙️ Installation & Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/evayifan2026/vision-to-tone.git
cd vision-to-tone
```

### 2. Python Environment Setup & Dependencies
Ensure you have Python 3.10+ installed, then install the required libraries:
```bash
cd python
pip install -r requirements.txt
```

### 3. Running the Project
- **Step 1 (Vision Module)**:
  ```bash
  python src/python/VisonToTone_V1.py
  ```
- **Step 2 (Audio Engine)**:
  Open Max/MSP, load the patch located at `src/max_msp/VisonToTone_V1.maxpat`, verify the UDP port is set to `8001`, ensure your audio samples are correctly referenced from `src/audio_assets/`, turn on Audio DSP, and interact via webcam and audio!

---

## 📈 Future Roadmap & Next Steps
- [ ] **Pitch Tracking & Synth Conversion**: Replace direct audio-rate playback with real-time monophonic pitch tracking to convert hummed vocals into clean software synth notes.
- [ ] **MIDI & Notation Pipeline**: Implement automated recording of note events and export to Standard MIDI Files (SMF) for seamless import into MuseScore or DAWs to generate clean five-line staff notation.
- [ ] **Continuous Gestural Mapping**: Map hand parameters directly to filter cutoffs and reverb depth.

🙏 Acknowledgments & AI Assistance Notice
Parts of the boilerplate code, configuration templates, and debugging scripts in this project were developed with the assistance of AI-powered coding tools (such as Google Gemini), under the direct architectural design, creative direction, and implementation of the author (Eva Wang)