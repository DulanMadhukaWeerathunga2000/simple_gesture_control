import cv2
import mediapipe as mp
import pyautogui
import time

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=RunningMode.VIDEO,
    num_hands=1
)

detector = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

last_action_time = 0
cooldown = 0.7

print("🖐️ Gesture Control Running...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp = int(time.time() * 1000)

    results = detector.detect_for_video(mp_image, timestamp)

    if results.hand_landmarks:
        lm = results.hand_landmarks[0]
        h, w, _ = frame.shape

        index_up = lm[8].y < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_up = lm[16].y < lm[14].y
        pinky_up = lm[20].y < lm[18].y

        thumb_up = lm[4].y < lm[3].y and not (index_up or middle_up or ring_up or pinky_up)
        thumb_down = lm[4].y > lm[3].y and not (index_up or middle_up or ring_up or pinky_up)

        now = time.time()

        if now - last_action_time > cooldown:
            if thumb_up:
                pyautogui.press("volumeup")
                print("🔊 Volume Up")
                last_action_time = now

            elif thumb_down:
                pyautogui.press("volumedown")
                print("🔉 Volume Down")
                last_action_time = now

    cv2.imshow("Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()