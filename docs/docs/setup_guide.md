# Vision-to-Tone: Setup & Execution Guide

This guide outlines the system requirements and step-by-step instructions to run the real-time gesture-controlled music interaction project.

---

## 1. System Requirements & Environment
- **Python Environment**: Python 3.8+ with dependencies such as `mediapipe`, `opencv-python`, and `python-osc`.
- **Audio Environment**: Max/MSP (version 8.0 or higher).
- **Hardware**: Built-in or external webcam and microphone.

---

## 2. Execution Steps

### Step 1: Run the Vision Processing Module
1. Open your terminal in the project root directory.
2. Execute the `MajorC1.py` script located in the `src/python` folder:
   ```bash
   python src/python/MajorC1.py

Behavior:

The webcam stream initializes, capturing video with real-time MediaPipe hand skeleton joint tracking.

As hands move vertically, dynamic text overlays (Major C or Minor C) appear near the fingertips, transmitting OSC control data.

### Step 2: Run the Audio Synthesis Engine
Launch Max/MSP.

Open the patch file located at src/max_msp/record-play-tonechange.maxpat.

Behavior:

Hum or sing a melody into your microphone to record.

Combine this with hand movements tracked by the vision script to experience real-time gesture-driven pitch shifting and audio synthesis.