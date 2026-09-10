# 🎵 VisionToTone: AI-Powered Gesture-Controlled Vocal Pitch Shifter & Composition Assistant

An interactive music prototyping tool that bridges computer vision, real-time OSC communication, and Digital Signal Processing (DSP) in Max/MSP to assist vocalists and composers in real-time melody sketching and pitch shifting.

🚀 Project Overview
VisionToTone allows a composer to use intuitive webcam-based hand gestures (tracked via Google MediaPipe) to control real-time vocal pitch-shifting and harmonization while humming melodies into Max/MSP via UDP/OSC.

Target Application: Music Technology, Computer Science & Creative Arts (intended for US Top 10 University Admissions portfolio).
Developer:Eva Wang Grade 9 Student Developer.

 System Architecture & Tech Stack

[Webcam Feed] 
      │
      ▼
[Python + MediaPipe] ──(Hand Landmark Detection & Gesture Classification)
      │
      ▼ (OSC Protocol over UDP - Port 8000)
[Max / MSP] 
      │
      ├── Audio Input (Microphone / Live Humming)
      ├── Pre-filtering (Low-pass to remove breath/sibilance artifacts)
      ├── Real-time Pitch Shifting & Harmonization (DSP)
      └── Audio Output / MIDI Export Pipeline

System Architecture & Tech Stack

Programming Language: Python 3.x[cite: 2]
Computer Vision & Protocols: MediaPipe, OpenCV, `python-osc`
Audio Engineering Environment: Max/MSP (`gizmo~`, `lores~`, OSC routing)


✨ Key Features Implemented (Phase 1)
- Real-time Computer Vision: High-fps hand landmark detection utilizing Google MediaPipe.
- Gesture Classification: Distinguishes specific chord and scale intentions, such as C Major versus C Minor hand configurations.
- Low-Latency OSC Bridge: Streams continuous control data from Python to Max/MSP over UDP.
- Vocal Artifact Taming: Integrated pre-filtering and dynamic smoothing in Max/MSP to eliminate harsh high-frequency digital artifacts and sibilance during live pitch shifting.

⚙️ Installation & Usage Guide
1. Clone the Repository
git clone [https://github.com/evayifan2026/vision-to-tone.git](https://github.com/evayifan2026/vision-to-tone.git)
cd vision-to-tone

2. Python Environment Setup
Ensure you have Python installed, then install the required computer vision and OSC dependencies:
cd python
pip install -r requirements.txt
python hand_tracker.py

3. Max/MSP Setup
a. Launch Max/MSP.

b. Open the patch located in max_msp/hum_pitch_shift.maxpat.

c. Ensure the OSC receiver port matches your Python script configuration (default: 8000).

d. Turn on Max Audio DSP, start humming into your microphone, and use your webcam gestures (Press Esc to exit the Python capture window) to alter the pitch in real time!

📈 Future Roadmap & Next Steps
[ ] Audio-to-MIDI Integration: Implement real-time monophonic pitch tracking to convert hummed audio directly into live MIDI scores.

[ ] Continuous Gestural Mapping: Map hand height (Y-axis) to transposition semitones and pinch distance to modulation/reverb depth.

[ ] SMF Export Pipeline: Enable direct export of improvised vocal lines into standard MIDI files (SMF) for DAW integration.