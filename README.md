
# 🚗 Driver Drowsiness Detection System

An AI-powered Python application that monitors a driver's eyes through a webcam and detects possible drowsiness using computer vision. The system displays a warning when prolonged eye closure is detected and is designed to play an audio alert to help draw attention to potential fatigue.

## 📌 Project Overview

Driver fatigue and drowsiness can reduce attention and reaction time while driving. This project uses OpenCV and MediaPipe Face Landmarker to analyze facial landmarks and estimate eye closure in real time.

When the estimated eye closure continues beyond a configurable time threshold, the application displays a drowsiness warning. Audio alerts and event logging are included in the project.

> **Note:** This is an educational prototype, not a certified vehicle safety system. It cannot guarantee that accidents will be prevented.

## ✨ Key Features

- 🎥 Real-time webcam monitoring
- 👁️ Facial landmark detection using MediaPipe
- 📐 Eye Aspect Ratio (EAR) calculation
- 😴 Detection of prolonged eye closure
- ⚠️ On-screen drowsiness warning
- 🔊 Audio alarm functionality
- 📝 CSV-based event logging
- 📊 Streamlit dashboard for monitoring and event review
- 📁 Downloadable monitoring logs

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| OpenCV | Webcam access and image processing |
| MediaPipe | Face landmark detection |
| NumPy | Numerical calculations, if used by the implementation |
| Streamlit | Monitoring dashboard |
| CSV | Event log storage |
| winsound | Windows audio alert |

## 📂 Project Structure

```text
Driver-Drowsiness-Detection/
│
├── main.py
├── dashboard.py
├── face_landmarker.task
├── requirements.txt
└── README.md
```

**File descriptions:**

- `main.py` — Runs webcam monitoring, calculates eye metrics, detects prolonged eye closure, and handles alerts.
- `dashboard.py` — Provides the Streamlit monitoring dashboard.
- `face_landmarker.task` — MediaPipe Face Landmarker model file.
- `requirements.txt` — Lists the Python dependencies.
- `README.md` — Project documentation.

The CSV event log is generated when the application records events.

## 💻 System Requirements

- Windows 10 or Windows 11
- Python 3.10 or another version supported by the installed MediaPipe release
- VS Code or another Python editor
- Working webcam
- Speakers or headphones for audio alerts
- Internet connection for initial dependency installation

## ⚙️ Installation and Setup

### 1. Clone the repository

Open Command Prompt or the VS Code terminal:

```bash
git clone https://github.com/annapurnabarnwal2-dot/Driver-Drowsiness-Detection.git
cd Driver-Drowsiness-Detection
```

Alternatively, download the repository as a ZIP file and extract it.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If installation fails, check the Python version and the compatibility of the installed MediaPipe and OpenCV packages.

### 4. Verify project files

Make sure these files exist in the same project folder:

- `main.py`
- `dashboard.py`
- `face_landmarker.task`
- `requirements.txt`

### 5. Run the main application

```bash
python main.py
```

Allow webcam access if Windows asks for permission.

### 6. Run the dashboard

Open a second terminal in the same project folder, activate the virtual environment, and run:

```bash
streamlit run dashboard.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser.

The dashboard may require the main monitoring application to generate the event log before meaningful data appears.

## 🧠 How It Works

1. **Video capture:** OpenCV captures frames from the webcam.
2. **Face landmark detection:** MediaPipe identifies facial landmarks around the eyes.
3. **Eye measurement:** Eye landmark coordinates are used to estimate the Eye Aspect Ratio (EAR).
4. **Drowsiness estimation:** The program checks whether the estimated eye closure persists beyond the configured time threshold.
5. **Warning:** A visual warning is displayed when prolonged eye closure is detected.
6. **Audio alert:** The program attempts to play an alarm when the alert condition is triggered.
7. **Event logging:** Monitoring events can be recorded in a CSV file.
8. **Dashboard:** Streamlit can display available monitoring statistics and event history.

## 📐 Eye Aspect Ratio (EAR)

The Eye Aspect Ratio estimates how open or closed an eye appears based on facial landmark coordinates.

A commonly used formula is:

\[
EAR = \frac{||P_2-P_6||+||P_3-P_5||}{2||P_1-P_4||}
\]

Here, the \(P_1\) to \(P_6\) points represent landmarks around the eye.

- A relatively lower EAR may indicate that the eye is closing.
- A higher EAR generally indicates that the eye is more open.
- The threshold depends on the implementation, camera conditions, and individual facial characteristics.

The EAR value alone is not a medical diagnosis of drowsiness.

## ⚙️ Detection Parameters

The current implementation uses these intended settings:

| Parameter | Value |
|---|---|
| Eye Aspect Ratio threshold | `0.21` |
| Eye-closure duration threshold | `2.0 seconds` |
| Camera input | Default webcam |

These values can be adjusted in `main.py` according to the implementation and testing conditions.

## 📊 Dashboard

The Streamlit dashboard is intended to provide:

- Monitoring status and summary metrics
- EAR measurements or graphs, when available
- Recorded drowsiness events
- CSV log download

The dashboard's displayed information depends on the data generated by the monitoring script.

## 🧪 Testing

Test the application under different conditions:

- Normal eye opening and blinking
- Prolonged eye closure
- Different lighting conditions
- Different distances from the webcam
- Temporary loss of face detection
- Audio output and CSV event logging

Record the results and limitations observed during testing. Do not claim a particular accuracy percentage unless it has been measured using a suitable labelled test dataset.

## ⚠️ Limitations

- Webcam quality and lighting can affect detection.
- Glasses, head movement, and face position may affect landmark detection.
- Eye closure is not always caused by drowsiness.
- The system may produce false alarms or miss some events.
- Audio playback depends on operating-system support and audio settings.
- The project has not been established as a certified automotive safety device.

**Safety advice:** If you feel sleepy while driving, stop at a safe location and rest. Do not rely on this prototype as a substitute for safe driving practices.

## 🚀 Future Enhancements

- Yawning detection
- Head-pose estimation
- Personalized EAR calibration
- Improved alert reliability
- Event timestamps and session reports
- Better dashboard visualizations
- Optional mobile or cloud notifications
- Evaluation using a labelled dataset

## 🎓 Project Applications

- Academic mini-projects and major projects
- Learning real-time computer vision
- Exploring facial landmark detection
- Demonstrating basic driver-fatigue monitoring concepts

## 👩‍💻 Author

**Project:** Driver Drowsiness Detection System

**GitHub:** [annapurnabarnwal2-dot](https://github.com/annapurnabarnwal2-dot)

## 📄 License

No license has been specified yet. If you want others to reuse or modify this project, choose and add an appropriate open-source license after reviewing its terms.

---

⭐ If you find this project useful for learning, consider starring the repository.
