
import cv2
import mediapipe as mp
import os
import time
import math
import threading
import winsound
import csv
from datetime import datetime


# ==========================================
# 1. FILE PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "face_landmarker.task")
LOG_FILE = os.path.join(BASE_DIR, "drowsiness_log.csv")


# ==========================================
# 2. DETECTION SETTINGS
# ==========================================

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

EAR_THRESHOLD = 0.21
CLOSED_EYE_SECONDS = 2.0

# Siren frequency settings
LOW_FREQUENCY = 1200
HIGH_FREQUENCY = 2200
TONE_DURATION_MS = 300


# ==========================================
# 3. MEDIAPIPE FACE LANDMARKER
# ==========================================

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}\n"
        "Ensure face_landmarker.task is in the project folder."
    )

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.VIDEO,
    num_faces=1
)


# ==========================================
# 4. EYE ASPECT RATIO CALCULATION
# ==========================================

def distance(p1, p2):
    return math.hypot(
        p1[0] - p2[0],
        p1[1] - p2[1]
    )


def calculate_ear(landmarks, eye_indices, width, height):
    points = []

    for index in eye_indices:
        landmark = landmarks[index]

        points.append((
            landmark.x * width,
            landmark.y * height
        ))

    vertical_1 = distance(points[1], points[5])
    vertical_2 = distance(points[2], points[4])
    horizontal = distance(points[0], points[3])

    if horizontal < 1:
        return 0.0

    return (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)


# ==========================================
# 5. CSV LOG INITIALIZATION
# ==========================================

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Date",
            "Time",
            "Event",
            "EAR"
        ])


def log_event(event_name, ear):
    now = datetime.now()

    try:
        with open(LOG_FILE, "a", newline="") as file:
            writer = csv.writer(file)

            writer.writerow([
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                event_name,
                round(ear, 3) if ear is not None else ""
            ])

    except OSError as error:
        print("CSV logging error:", error)


# ==========================================
# 6. CONTINUOUS SIREN ALARM
# ==========================================

alarm_active = threading.Event()



def play_alarm():
    try:
        while alarm_active.is_set():
            winsound.Beep(1800, 500)

            if not alarm_active.is_set():
                break

            winsound.Beep(1000, 500)

    except Exception as error:
        print("Alarm error:", error)

    finally:
        alarm_active.clear()



def start_alarm():
    if not alarm_active.is_set():
        alarm_active.set()

        thread = threading.Thread(
            target=play_alarm,
            daemon=True
        )

        thread.start()


def stop_alarm():
    alarm_active.clear()


# ==========================================
# 7. START WEBCAM
# ==========================================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    cap.release()
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Webcam open nahi hua.")
    raise SystemExit


# ==========================================
# 8. MAIN DETECTION LOOP
# ==========================================

start_time = time.monotonic()
eyes_closed_start = None
event_logged = False

try:
    with FaceLandmarker.create_from_options(options) as landmarker:

        while True:

            success, frame = cap.read()

            if not success:
                print("Webcam frame nahi mila.")
                break

            frame = cv2.flip(frame, 1)

            height, width, _ = frame.shape

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            timestamp_ms = int(
                (time.monotonic() - start_time) * 1000
            )

            result = landmarker.detect_for_video(
                image,
                timestamp_ms
            )

            status = "No Face Detected"
            color = (0, 0, 255)
            ear = None

            # ----------------------------------
            # FACE DETECTED
            # ----------------------------------

            if result.face_landmarks:

                landmarks = result.face_landmarks[0]

                left_ear = calculate_ear(
                    landmarks,
                    LEFT_EYE,
                    width,
                    height
                )

                right_ear = calculate_ear(
                    landmarks,
                    RIGHT_EYE,
                    width,
                    height
                )

                ear = (left_ear + right_ear) / 2.0

                # Draw eye landmark points
                for eye in (LEFT_EYE, RIGHT_EYE):

                    for index in eye:

                        point = landmarks[index]

                        x = int(point.x * width)
                        y = int(point.y * height)

                        cv2.circle(
                            frame,
                            (x, y),
                            3,
                            (0, 255, 0),
                            -1
                        )

                # ----------------------------------
                # EYE CLOSURE DETECTION
                # ----------------------------------

                if ear < EAR_THRESHOLD:

                    if eyes_closed_start is None:
                        eyes_closed_start = time.monotonic()

                    closed_duration = (
                        time.monotonic() - eyes_closed_start
                    )

                    if closed_duration >= CLOSED_EYE_SECONDS:

                        status = "DROWSINESS ALERT! SIREN ON"
                        color = (0, 0, 255)

                        # Start siren
                        start_alarm()

                        # Log only once per closure episode
                        if not event_logged:
                            log_event(
                                "DROWSINESS ALERT",
                                ear
                            )

                            event_logged = True

                    else:

                        status = (
                            f"Eyes Closed: "
                            f"{closed_duration:.1f}s"
                        )

                        color = (0, 165, 255)

                else:

                    # Eyes open: reset detection and siren
                    eyes_closed_start = None
                    stop_alarm()
                    event_logged = False

                    status = "Status: Awake"
                    color = (0, 255, 0)

            # ----------------------------------
            # NO FACE DETECTED
            # ----------------------------------

            else:

                eyes_closed_start = None
                stop_alarm()
                event_logged = False

            # ----------------------------------
            # DISPLAY EAR
            # ----------------------------------

            if ear is not None:

                cv2.putText(
                    frame,
                    f"EAR: {ear:.3f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 0),
                    2
                )

            # ----------------------------------
            # DISPLAY STATUS
            # ----------------------------------

            cv2.putText(
                frame,
                status,
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Driver Drowsiness Detection",
                frame
            )

            # Press Q to exit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:

    # Always stop siren and release resources
    stop_alarm()
    cap.release()
    cv2.destroyAllWindows()

    print("Driver Drowsiness Detection stopped.")
