# ⚙️ Environment Configuration Guide

## 1. Hardware Requirements
- **Camera**: Standard webcam (supporting 720p/30fps or higher)
- **Audio**: External microphone (dedicated microphone recommended to reduce ambient noise)

## 2. Software Dependencies
| Software / Library Name | Version Requirement | Description |
| :--- | :--- | :--- |
| Python | 3.10+ | Runs MediaPipe, OpenCV, and the OSC client |
| Max/MSP | 8.x | Receives OSC signals and real-time digital signal processing (DSP) |
| MediaPipe | 0.10.9 | Real-time tracking of camera hand joints |
| OpenCV (`opencv-python`) | Latest | Webcam stream capture and frame processing |
| `python-osc` | Latest | UDP communication bridge between Python and Max/MSP |
| NumPy | Latest | Numerical processing and dynamic audio envelope generation |

## 3. Audio & Asset Directory Setup
To ensure proper audio playback via Max/MSP (`sfplay~`):
- Place all source WAV/MP3 audio loops inside the **`src/audio_assets/`** directory.
- When opening the Max patch, make sure the search path includes `src/audio_assets/` so `sfplay~` can resolve file paths dynamically sent via Python's OSC `/play_ready` commands.