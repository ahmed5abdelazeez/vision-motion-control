import cv2
import mediapipe as mp
import numpy as np
import serial
import time

# ---------------- SERIAL SETTINGS ----------------
COM_PORT = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0"
BAUD = 115200
COOLDOWN_SEC = 1.5  # seconds between commands

# ---------------- MEDIAPIPE SETTINGS ----------------
MIN_DET = 0.6
MIN_TRK = 0.6

# ---------------- OPEN/CLOSE LOGIC ----------------
def hand_open_closed(hand_landmarks, handedness_label="Right"):
    """
    Returns: (label, fingers_up)
    label: "OPEN", "CLOSED", or "PARTIAL"
    fingers_up: 0..5
    """
    lm = hand_landmarks.landmark

    # Landmark indices
    TIP = [4, 8, 12, 16, 20]
    PIP = [2, 6, 10, 14, 18]  # thumb uses 2 as reference, others are PIP joints

    fingers_up = 0

    # Thumb: compare x (depends on Left/Right)
    if handedness_label == "Right":
        if lm[TIP[0]].x > lm[PIP[0]].x:
            fingers_up += 1
    else:  # Left
        if lm[TIP[0]].x < lm[PIP[0]].x:
            fingers_up += 1

    # Other 4 fingers: tip higher than PIP (smaller y = higher in image)
    for tip, pip in zip(TIP[1:], PIP[1:]):
        if lm[tip].y < lm[pip].y:
            fingers_up += 1

    if fingers_up >= 4:
        return "OPEN", fingers_up
    elif fingers_up <= 1:
        return "CLOSED", fingers_up
    else:
        return "PARTIAL", fingers_up


# ---------------- SERIAL COMMANDS ----------------
def send_on(ser):
    ser.write(b"1\n")  # newline helps Arduino readLine if you use it
    print("ARDUINO -> LED ON")


def send_off(ser):
    ser.write(b"0\n")
    print("ARDUINO -> LED OFF")


# ---------------- MAIN ----------------
def main():
    # Open Serial
    ser = serial.Serial(COM_PORT, BAUD, timeout=1)
    time.sleep(2)  # give Arduino time to reset

    # MediaPipe init
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=MIN_DET,
        min_tracking_confidence=MIN_TRK
    )

    # State
    led_state = "OFF"
    last_cmd_time = 0.0

    # Camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1580)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1000)

    cv2.namedWindow("Hand Control (Open/Close)", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Hand Control (Open/Close)", 1580, 1000)
    print("Working | q = QUIT")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = hands.process(rgb)

            hand_label = "NO HAND"
            fingers_up = 0

            if res.multi_hand_landmarks:
                hand = res.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                # handedness (Left/Right)
                handedness_label = "Right"
                if res.multi_handedness:
                    handedness_label = res.multi_handedness[0].classification[0].label

                hand_label, fingers_up = hand_open_closed(hand, handedness_label)

                now = time.time()

                # State machine: OPEN -> LED ON, CLOSED -> LED OFF
                if hand_label == "OPEN" and led_state == "OFF" and (now - last_cmd_time) > COOLDOWN_SEC:
                    send_on(ser)
                    led_state = "ON"
                    last_cmd_time = now

                elif hand_label == "CLOSED" and led_state == "ON" and (now - last_cmd_time) > COOLDOWN_SEC:
                    send_off(ser)
                    led_state = "OFF"
                    last_cmd_time = now

            # Display
            text = f"LED: {led_state} | HAND: {hand_label} | UP: {fingers_up}"
            cv2.putText(frame, text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            DISPLAY_W, DISPLAY_H = 1580, 1000
            frame_show = cv2.resize(frame, (DISPLAY_W, DISPLAY_H))
            cv2.imshow("Hand Control (Open/Close)", frame_show)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        ser.close()


if __name__ == "__main__":
    main()
