import cv2
import mediapipe as mp
import pyautogui
import time

# MediaPipe Tasks API setup
BaseOptions = mp.tasks.python.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

# Initialize Hand Landmarker using the existing task model
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=RunningMode.VIDEO,
    num_hands=1
)
detector = HandLandmarker.create_from_options(options)

# Open Webcam
cap = cv2.VideoCapture(0)

print("🖐️ Simple Gesture Control Started!")
print("👍 Thumbs Up   -> Volume Up")
print("👎 Thumbs Down -> Volume Down")
print("Press 'q' to quit.")

last_action_time = 0
cooldown = 0.5  # seconds between action triggers

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("❌ Camera feed not found.")
        break

    # Flip frame and convert color to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Process the frame with a timestamp
    timestamp = int(time.time() * 1000)
    results = detector.detect_for_video(mp_image, timestamp)

    if results.hand_landmarks:
        # Get landmarks for the detected hand
        lm = results.hand_landmarks[0]
        h, w, _ = frame.shape
        
        # Draw green circles on the 5 fingertips (Thumb, Index, Middle, Ring, Pinky)
        for idx in [4, 8, 12, 16, 20]:
            cx, cy = int(lm[idx].x * w), int(lm[idx].y * h)
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)
            
        # Check which fingers are raised (y increases downwards in OpenCV)
        index_up = lm[8].y < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_up = lm[16].y < lm[14].y
        pinky_up = lm[20].y < lm[18].y
        
        # Thumbs up: thumb is up, other fingers are down
        thumb_up = lm[4].y < lm[3].y and not (index_up or middle_up or ring_up or pinky_up)
        # Thumbs down: thumb is down, other fingers are down
        thumb_down = lm[4].y > lm[3].y and not (index_up or middle_up or ring_up or pinky_up)
        
        current_time = time.time()
        if current_time - last_action_time > cooldown:
            if thumb_up:
                print("🔊 Volume Up")
                pyautogui.press("volumeup")
                last_action_time = current_time
                cv2.putText(frame, "Volume Up", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif thumb_down:
                print("🔉 Volume Down")
                pyautogui.press("volumedown")
                last_action_time = current_time
                cv2.putText(frame, "Volume Down", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow("Simple Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
detector.close()
