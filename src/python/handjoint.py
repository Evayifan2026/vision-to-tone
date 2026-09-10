#!/usr/bin/env python3
import cv2
import mediapipe as mp
from pythonosc import udp_client

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

client = udp_client.SimpleUDPClient("127.0.0.1", 8000)

cap = cv2.VideoCapture(0)

# 标记当前调性状态，防止重复发送大量冗余消息
current_mode = None

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS
            )

            # 获取食指指尖 (Index Finger Tip, Index 8)
            index_finger_tip = hand_landmarks.landmark[8]
            x, y = index_finger_tip.x, index_finger_tip.y

            # 1. 实时发送坐标
            client.send_message("/hand/index", [x, y])

            # 2. 调性判定逻辑 (图像坐标系 Y: 0.0 为顶部, 1.0 为底部)
            # 食指向上 (Y < 0.4) -> C Major (大调)
            # 食指向下 (Y > 0.6) -> C Minor (小调)
            new_mode = None
            if y < 0.4:
                new_mode = "major"
            elif y > 0.6:
                new_mode = "minor"

            # 当调性发生变化时，发送 OSC 消息并在终端打印
            if new_mode and new_mode != current_mode:
                current_mode = new_mode
                client.send_message("/hand/mode", current_mode)
                print(f" Mode Switched: {current_mode.upper()}")

            # 画面UI提示：高亮指尖并显示当前调性
            h, w, _ = frame.shape
            cx, cy = int(x * w), int(y * h)
            color = (0, 255, 0) if current_mode == "major" else (255, 0, 0) if current_mode == "minor" else (255, 255, 255)
            
            cv2.circle(frame, (cx, cy), 12, color, cv2.FILLED)
            if current_mode:
                cv2.putText(frame, f"Mode: C {current_mode.capitalize()}", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    cv2.imshow('Hand Tracking & Mode Control', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)
