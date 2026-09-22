import time
import subprocess
import os
import threading
import math
import numpy as np
import cv2
import mido
import wave
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

# -------------------------- Path Configuration --------------------------
OUTPUT_DIR = "/Users/evawang/MusicTech/TestMusic"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WAV_FILE = os.path.join(OUTPUT_DIR, "recorded_melody.wav")
MIDI_FILE = os.path.join(OUTPUT_DIR, "recorded_melody_basic_pitch.mid")

OSC_IP = "127.0.0.1"
OSC_PORT_OUT = 8001  
OSC_PORT_IN = 8002   

WAIT_AFTER_WAV_WRITE = 1.0  

client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT_OUT)

# -------------------------- 24 Keys Definition --------------------------
CIRCLE_OF_FIFTHS = [
    ("C Maj", 0, 60), ("G Maj", 7, 67), ("D Maj", 2, 62), ("A Maj", 9, 69), 
    ("E Maj", 4, 64), ("B Maj", 11, 71), ("F# Maj", 6, 66), ("Db Maj", 1, 61), 
    ("Ab Maj", 8, 68), ("Eb Maj", 3, 63), ("Bb Maj", 10, 70), ("F Maj", 5, 65),
    ("A Min", 9, 57), ("E Min", 4, 64), ("B Min", 11, 59), ("F# Min", 6, 66), 
    ("C# Min", 1, 61), ("G# Min", 8, 68), ("D# Min", 3, 63), ("Bb Min", 10, 58), 
    ("F Min", 5, 65), ("C Min", 0, 60), ("G Min", 7, 67), ("D Min", 2, 62)
]

current_tonic_name = "None"
current_transpose_semitones = 0
current_base_root = 60
selected_key_index = -1  
current_expression = "Happy"  

# 🔒 Lock variable to prevent frequent triggers and race conditions during rendering
is_processing = False

# -------------------------- MediaPipe Initialization --------------------------
MEDIAPIPE_AVAILABLE = False
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    
    hands_detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    face_mesh_detector = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    MEDIAPIPE_AVAILABLE = True
    print("✅ MediaPipe initialized successfully.")
except ImportError:
    print("⚠️ MediaPipe library not detected.")

BASIC_PITCH_ARGS = [
    "basic-pitch",
    "--onset-threshold", "0.2",           
    "--frame-threshold", "0.35",          
    "--minimum-note-length", "120",       
    "--minimum-frequency", "120",         
    "--maximum-frequency", "900",         
    "--save-midi",
    OUTPUT_DIR,
    WAV_FILE
]

def detect_facial_expression(face_landmarks):
    try:
        landmarks = face_landmarks.landmark
        upper_lip = landmarks[13].y
        lower_lip = landmarks[14].y
        left_corner = landmarks[61].y
        right_corner = landmarks[291].y
        corner_avg = (left_corner + right_corner) / 2
        lip_center = (upper_lip + lower_lip) / 2
        
        if corner_avg < lip_center - 0.008:
            return "Happy"
        elif corner_avg > lip_center + 0.008:
            return "Sad"
        else:
            return "Happy"
    except Exception:
        return "Happy"

def synthesize_and_transpose_piano(midi_path, output_wav, transpose_val, key_name, chord_type, base_root_note):
    try:
        mid = mido.MidiFile(midi_path)
        sample_rate = 44100
        
        safe_key_name = key_name.replace(" ", "_")
        safe_chord_suffix = chord_type.replace(" ", "_")
        file_tag = f"{safe_key_name}_{safe_chord_suffix}"
        
        transposed_midi_file = os.path.join(OUTPUT_DIR, f"transposed_midi_{file_tag}.mid")
        rendered_audio_file = os.path.join(OUTPUT_DIR, f"rendered_piano_{file_tag}.wav")
        
        # 1. Export clean transposed MIDI
        transposed_midi = mido.MidiFile(type=1, ticks_per_beat=mid.ticks_per_beat)
        melody_track = mido.MidiTrack()
        for track in mid.tracks:
            for msg in track:
                new_msg = msg.copy()
                if hasattr(new_msg, 'note') and not (hasattr(new_msg, 'is_meta') and new_msg.is_meta):
                    new_msg.note = max(0, min(127, new_msg.note + transpose_val))
                melody_track.append(new_msg)
        transposed_midi.tracks.append(melody_track)
        transposed_midi.save(transposed_midi_file)

        # 2. Extract melody events and record absolute timestamps
        melody_events = []
        ticks_per_beat = mid.ticks_per_beat
        for track in mid.tracks:
            abs_ticks = 0
            for msg in track:
                abs_ticks += msg.time
                new_msg = msg.copy()
                if hasattr(new_msg, 'note') and not (hasattr(new_msg, 'is_meta') and new_msg.is_meta):
                    new_msg.note = max(0, min(127, new_msg.note + transpose_val))
                melody_events.append((abs_ticks, new_msg, False))

        max_melody_ticks = max((ev[0] for ev in melody_events), default=ticks_per_beat * 8)

        # 3. Dynamic root extraction and segmented arpeggio generation
        segment_ticks = ticks_per_beat * 4  
        arpeggio_events = []
        
        global_tonic_pitch = base_root_note + transpose_val
        is_minor_key = ("Min" in key_name) or (chord_type == "Min")

        curr_t = 0
        while curr_t < max_melody_ticks + segment_ticks:
            segment_notes = [ev[1].note for ev in melody_events if curr_t <= ev[0] < curr_t + segment_ticks and ev[1].type == 'note_on' and ev[1].velocity > 0]
            
            if segment_notes:
                segment_root = int(np.median(segment_notes))
                while segment_root > global_tonic_pitch + 6:
                    segment_root -= 12
                while segment_root < global_tonic_pitch - 6:
                    segment_root += 12
            else:
                segment_root = global_tonic_pitch - 12  

            interval_from_tonic = (segment_root - global_tonic_pitch) % 12
            is_segment_minor = is_minor_key or (interval_from_tonic in [2, 4, 9]) 
            third_offset = 3 if is_segment_minor else 4
            fifth_offset = 7

            chord_notes_sequence = [
                segment_root - 12, 
                segment_root, 
                segment_root + third_offset, 
                segment_root + fifth_offset
            ]
            
            step_ticks = int(ticks_per_beat * 0.5)    
            
            for loop_idx in range(2):
                loop_start_t = curr_t + (loop_idx * (segment_ticks // 2))
                for idx, note_val in enumerate(chord_notes_sequence):
                    note_on_time = loop_start_t + (idx * step_ticks)
                    note_off_time = note_on_time + int(ticks_per_beat * 0.4)
                    
                    arpeggio_events.append((note_on_time, mido.Message('note_on', note=note_val, velocity=20), True))
                    arpeggio_events.append((note_off_time, mido.Message('note_off', note=note_val, velocity=0), True))

            curr_t += segment_ticks

        all_events = melody_events + arpeggio_events
        all_events.sort(key=lambda x: (x[0], 0 if x[1].type == 'note_off' else 1))

        # 4. Audio synthesis
        events = []
        for abs_ticks_val, msg, is_chd in all_events:
            events.append((abs_ticks_val, msg, is_chd))
            
        tempo = 500000
        active = {}
        raw_segments = []
        
        for abs_ticks, msg, is_chd in events:
            sec = mido.tick2second(abs_ticks, ticks_per_beat, tempo)
            if msg.type == 'note_on' and msg.velocity > 0:
                active[msg.note] = (sec, msg.velocity, is_chd)
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active:
                    start_sec, vel, is_chd = active.pop(msg.note)
                    duration = max(sec - start_sec, 0.2)
                    freq = 440.0 * (2.0 ** ((msg.note - 69) / 12.0))
                    raw_segments.append((start_sec, duration, freq, vel, is_chd))
                    
        if not raw_segments:
            return None

        max_sec = max(seg[0] + seg[1] for seg in raw_segments) + 1.5
        total_samples = int(max_sec * sample_rate)
        audio_buffer = np.zeros(total_samples, dtype=np.float32)
        
        for start_sec, duration, freq, intensity_val, is_chd in raw_segments:
            start_idx = int(start_sec * sample_rate)
            render_duration = duration + (0.5 if is_chd else 0.5)
            end_idx = min(int((start_sec + render_duration) * sample_rate), total_samples)
            
            t = np.linspace(0, render_duration, end_idx - start_idx, endpoint=False)
            
            if is_chd:
                wave_signal = 0.10 * (
                    0.3 * np.sin(2 * np.pi * freq * t) + 
                    0.08 * np.sin(2 * np.pi * 2 * freq * t)
                )
                wave_signal *= np.exp(-3.0 * t)  
            else:
                normalized_intensity = max(intensity_val / 127.0, 0.4)
                wave_signal = normalized_intensity * (
                    0.45 * np.sin(2 * np.pi * freq * t) + 
                    0.18 * np.sin(2 * np.pi * 2 * freq * t) +
                    0.08 * np.sin(2 * np.pi * 3 * freq * t)
                )
                wave_signal *= np.exp(-1.5 * t)
            
            if end_idx <= total_samples:
                audio_buffer[start_idx:end_idx] += wave_signal
                
        audio_buffer = np.clip(audio_buffer, -0.8, 0.8)
        audio_data = (audio_buffer * 32767).astype(np.int16)
        
        with wave.open(rendered_audio_file, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
            
        print(f"🎹 [Rendering Complete] WAV: {rendered_audio_file}")
        return rendered_audio_file
        
    except Exception as e:
        print(f"❌ Rendering Exception: {e}")
        return None

# OSC Server
def handle_osc_msg(address, args, val):
    global current_transpose_semitones
    current_transpose_semitones = int(val)

def start_osc_server():
    dispatcher = Dispatcher()
    dispatcher.map("/transpose", handle_osc_msg, "transpose")
    server = osc_server.ThreadingOSCUDPServer((OSC_IP, OSC_PORT_IN), dispatcher)
    server.serve_forever()

threading.Thread(target=start_osc_server, daemon=True).start()

def process_latest_recording():
    global current_tonic_name, current_transpose_semitones, current_base_root, selected_key_index, current_expression, is_processing
    
    if selected_key_index == -1:
        print("ℹ️ Please select a key mode using gestures in front of the camera first!")
        return
    
    if not os.path.exists(WAV_FILE):
        return

    # 🔒 If already rendering, skip to prevent conflicts and state mixing
    if is_processing:
        print("⏳ Previous rendering is still in progress, skipping duplicate trigger...")
        return

    is_processing = True
    
    # 📸 Snapshot current state to lock mode and expression during rendering
    target_tonic = current_tonic_name
    target_transpose = current_transpose_semitones
    target_root = current_base_root
    target_expression = current_expression

    try:
        if os.path.exists(MIDI_FILE):
            os.remove(MIDI_FILE)

        print(f"\n🚀 Starting Rendering: Key=[{target_tonic}], Expression/Chord=[{target_expression}] ...")
        result = subprocess.run(BASIC_PITCH_ARGS, capture_output=True, text=True)

        if result.returncode == 0:
            midi_found = False
            for _ in range(20):
                if os.path.exists(MIDI_FILE):
                    midi_found = True
                    break
                time.sleep(0.1)

            if midi_found:
                chord_type = "Min" if target_expression == "Sad" else "Maj"
                chord_display_name = f"{target_tonic} {chord_type} (Dynamic Roots)"
                
                out_wav = synthesize_and_transpose_piano(MIDI_FILE, None, target_transpose, target_tonic, chord_type, target_root)
                
                if out_wav and os.path.exists(out_wav):
                    client.send_message("/play_ready", out_wav)
                    client.send_message("/current_key", target_tonic)
                    client.send_message("/current_chord", chord_display_name)
                    client.send_message("/current_expression", target_expression)
    finally:
        # 🔓 Release rendering lock
        is_processing = False

def main():
    global current_tonic_name, current_transpose_semitones, current_base_root, selected_key_index, current_expression, is_processing
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera")
        return

    last_wav_mtime = 0.0
    hover_start_time = 0
    last_hovered_index = -1
    CONFIRM_DURATION = 1.0  

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        center_x, center_y = int(w * 0.5), int(h * 0.55)
        radius = int(min(h, w) * 0.40)
        BTN_RADIUS = 60

        button_coords = []
        for i, (key_name, semitone, base_root) in enumerate(CIRCLE_OF_FIFTHS):
            angle = i * (2 * math.pi / len(CIRCLE_OF_FIFTHS)) - math.pi / 2
            bx = int(center_x + radius * math.cos(angle))
            by = int(center_y + radius * math.sin(angle))
            button_coords.append((bx, by, key_name, semitone, base_root))

        index_finger_tip = None
        if MEDIAPIPE_AVAILABLE:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 💡 Detect facial expressions in real-time (can be continuously updated for subsequent processing)
            face_results = face_mesh_detector.process(rgb_frame)
            if face_results.multi_face_landmarks:
                current_expression = detect_facial_expression(face_results.multi_face_landmarks[0])

            hands_results = hands_detector.process(rgb_frame)
            if hands_results.multi_hand_landmarks:
                for hand_landmarks in hands_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    tip = hand_landmarks.landmark[8]
                    index_finger_tip = (int(tip.x * w), int(tip.y * h))

        current_hovered = -1
        if index_finger_tip and not is_processing: # Ignore hover selections during rendering to avoid confusion
            for i, (bx, by, _, _, _) in enumerate(button_coords):
                if math.hypot(index_finger_tip[0] - bx, index_finger_tip[1] - by) < BTN_RADIUS:
                    current_hovered = i
                    break

        overlay = frame.copy()
        for i, (bx, by, key_name, _, _) in enumerate(button_coords):
            is_selected = (i == selected_key_index)
            is_hovered = (i == current_hovered)
            glass_bg = (0, 160, 80) if is_selected else ((120, 140, 160) if is_hovered else (70, 70, 70))
            cv2.circle(overlay, (bx, by), BTN_RADIUS, glass_bg, -1)

        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        for i, (bx, by, key_name, _, _) in enumerate(button_coords):
            is_selected = (i == selected_key_index)
            is_hovered = (i == current_hovered)
            border_color = (0, 255, 128) if is_selected else ((255, 220, 0) if is_hovered else (180, 180, 180))
            cv2.circle(frame, (bx, by), BTN_RADIUS, border_color, 3 if is_selected or is_hovered else 2)

            text_size = cv2.getTextSize(key_name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.putText(frame, key_name, (bx - text_size[0] // 2, by + text_size[1] // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if current_hovered != -1 and not is_processing:
            if current_hovered == last_hovered_index:
                elapsed = time.time() - hover_start_time
                progress = min(elapsed / CONFIRM_DURATION, 1.0)
                bx, by, _, _, _ = button_coords[current_hovered]
                cv2.ellipse(frame, (bx, by), (BTN_RADIUS + 8, BTN_RADIUS + 8), 0, -90, int(-90 + progress * 360), (0, 255, 255), 4)
                
                if elapsed >= CONFIRM_DURATION:
                    selected_key_index = current_hovered
                    current_tonic_name = button_coords[current_hovered][2]
                    current_transpose_semitones = button_coords[current_hovered][3]
                    current_base_root = button_coords[current_hovered][4]
                    print(f"\n🎯 Selected Key: [{current_tonic_name}]")
                    process_latest_recording()
                    hover_start_time = time.time()
            else:
                last_hovered_index = current_hovered
                hover_start_time = time.time()
        else:
            last_hovered_index = -1

        if os.path.exists(WAV_FILE) and not is_processing:
            current_mtime = os.path.getmtime(WAV_FILE)
            if current_mtime > last_wav_mtime:
                time.sleep(WAIT_AFTER_WAV_WRITE)
                last_wav_mtime = current_mtime
                process_latest_recording()

        # 📺 HUD Display Panel (with status indicator)
        chord_type_preview = "Min" if current_expression == "Sad" else "Maj"
        hud_overlay = frame.copy()
        cv2.rectangle(hud_overlay, (20, 20), (620, 160), (15, 15, 15), -1)
        cv2.addWeighted(hud_overlay, 0.75, frame, 0.25, 0, frame)
        cv2.rectangle(frame, (20, 20), (620, 160), (0, 255, 255), 2)

        # Status indicator text
        if is_processing:
            status_str = "Status: ⏳ Generating Audio... Please Wait"
            status_color = (0, 165, 255) # Orange for processing
        else:
            status_str = "Status: ✅ Ready (Playing latest)"
            status_color = (0, 255, 128) # Green for ready
        cv2.putText(frame, status_str, (35, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

        key_display_str = f"Active Key: {current_tonic_name}" if selected_key_index != -1 else "Active Key: None (Hover 1s)"
        cv2.putText(frame, key_display_str, (35, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        chord_display_str = f"Chord: Dynamic Roots [{current_expression}]" if selected_key_index != -1 else f"Chord: None [{current_expression}]"
        cv2.putText(frame, chord_display_str, (35, 132), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (0, 255, 255), 2)

        cv2.imshow("Max + MediaPipe 24-Key & Expression Controller", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()