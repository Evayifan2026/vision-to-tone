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

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
current_mode = "minor" # 默认初始模式
last_sent_index = -1   # 用于防抖的记录变量

window_name = 'Hand Tracking & Mode Control'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        cv2.waitKey(10)
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger_tip = hand_landmarks.landmark[8]
            x, y = index_finger_tip.x, index_finger_tip.y

            # 1. 将 y 坐标转换为 0 到 11 的离散整数索引
            index_val = int((1.0 - y) * 12)
            index_val = max(0, min(11, index_val))  # 确保严格限制在 0-11 之间

            # 2. 实时发送单个整型 index（使用简化路径 /index 适配 Max）
            if index_val != last_sent_index:
                client.send_message("/index", index_val)
                last_sent_index = index_val

            # 3. 调性判定 (缩小中间缓冲区，让切换更灵敏)
            if y < 0.45:
                current_mode = "major"
            elif y > 0.55:
                current_mode = "minor"

            # 4. 持续向 Max 发送当前 mode（使用简化路径 /mode 适配 Max）
            client.send_message("/mode", current_mode)

            # 5. 画画面
            h, w, _ = frame.shape
            cx, cy = int(x * w), int(y * h)
            color = (0, 255, 0) if current_mode == "major" else (255, 0, 0)
            
            cv2.circle(frame, (cx, cy), 12, color, cv2.FILLED)
            text = "Major C" if current_mode == "major" else "Minor C"
            cv2.putText(frame, text, (cx + 15, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(frame, text, (cx + 15, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)

    cv2.imshow(window_name, frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
for _ in range(5):
    cv2.waitKey(1)