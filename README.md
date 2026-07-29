<div align="center">

# ⋆౨ৎ⋆ Sports Accessibility ⋆౨ৎ⋆

***Tracking a ball in real time and translating its position into physical motion***

<br>

![Python](https://img.shields.io/badge/Python-CV%20pipeline-FFB5C2?style=flat-square&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-image%20processing-C8B6FF?style=flat-square&logo=opencv&logoColor=white)
![YOLO](https://img.shields.io/badge/YOLO-Roboflow-B5D8FF?style=flat-square)
![Arduino](https://img.shields.io/badge/Arduino-stepper%20motor-B8E6D9?style=flat-square&logo=arduino&logoColor=white)
![Score](https://img.shields.io/badge/TIPE-20%2F20%20✧-FFE0B5?style=flat-square)

<br>

*A computer-vision + mechatronics system that follows a ball on a field*
*and moves a physical cursor to match, making live sports more accessible to visually impaired people.*

</div>

---

<div align="center">

### 20/20 at the TIPE- ranked in the top 0-3% of engineering candidates nationwide

*Built as a French* classe préparatoire *research project (TIPE), presented and graded on the competitive-exam scale.*

</div>

---

## What is this?

A system that watches a sports field through a camera, finds the ball in real time, works out where it is on the field, and then drives a small motor to move a physical marker to that spot, so the position of the game can be felt, not just seen. 

It combines:
- **Computer vision** in Python (OpenCV + a YOLO detector) to locate the field and the ball,
- **Mechatronics** on an Arduino (a stepper motor + belt) to turn those coordinates into real movement.

---

## Features

- **Real-time ball tracking** - a YOLO model (trained on a custom football dataset via Roboflow) detects the ball frame by frame
- **Automatic field detection** - the pitch corners are found on the fly and used to build a homography, so pixel positions map to true field coordinates
- **Vision to motion bridge** - ball coordinates are streamed over serial to an Arduino that moves a stepper motor accordingly
- **Camera-placement study** - a helper script generates and visualizes candidate camera positions in 3D to find angles where tracking actually works

---

## How it works

```
   ┌──────────────────────── main.py (vision) ────────────────────────┐
   │                                                                   │
   │  camera frame                                                     │
   │      │                                                            │
   │      ▼                                                            │
   │  ① find the field                    ② find the ball             │
   │     HSV green mask                       YOLO model (Roboflow)    │
   │     → Otsu + morphology                  → bounding box           │
   │     → Canny edges                              │                  │
   │     → contours → convex hull                   │                  │
   │     → Shi–Tomasi corners (×4)                  │                  │
   │           │                                    │                  │
   │           ▼                                    ▼                  │
   │     homography H  ───────────▶  project ball onto field coords    │
   │                                                │                  │
   └────────────────────────────────────────────────┼─────────────────┘
                                                     │  x-coordinate
                                        serial (115200 baud)
                                                     │
                                                     ▼
   ┌──────────────────────── main.ino (motion) ───────────────────────┐
   │  read target x  →  compute speed & step count  →  drive stepper   │
   │  motor + belt to the matching position (returns home if signal    │
   │  drops)                                                           │
   └───────────────────────────────────────────────────────────────────┘
```

**The vision pipeline, step by step:**

1. **Field segmentation** - the frame is converted to HSV and masked to the green of the pitch, then denoised with Otsu thresholding and a morphological close.
2. **Corner detection** - Canny edges → contours → `approxPolyDP` (Ramer–Douglas–Peucker smoothing) → a size filter → convex hull → **Shi–Tomasi** corner detection to pull out the field's four corners.
3. **Homography** - the four corners are sorted and matched to a reference rectangle, giving a transform `H` from image pixels to real field coordinates.
4. **Ball detection** - the YOLO model infers the ball's bounding box; its ground point is projected through `H`.
5. **Send it** - the resulting x-coordinate is written over serial to the Arduino.

**On the Arduino side (`main.ino`):** it reads the incoming coordinate, computes the stepper's rotation speed and step count from the belt/pulley geometry (capped at a max speed), moves the motor, and gracefully returns to its origin if the serial link drops.

**Camera planning (`positions.py`):** converts spherical camera positions to cartesian around the field center and plots them as a 3D surface - a neat way to reason about which viewing angles keep the four-corner detection reliable.

---

## Project structure

```
sports-accessibility/
├── main.py            ⋆ vision pipeline: field homography + ball tracking → serial
├── main.ino           ✧ Arduino: turns coordinates into stepper-motor motion
├── positions.py       · 3D study of candidate camera placements
└── Presentation.pdf   · slides - theory, analysis & experimental results
```

📄 The **[presentation](Presentation.pdf)** covers the theory, the analysis, and the experimental measurements in full.

---

## Running it

**Vision (Python):**

```bash
pip install opencv-python numpy inference pyserial matplotlib
python3 main.py
```

You'll need a webcam, a green playing surface in view, and the Arduino connected on the serial port set in `main.py` (`COM3` by default - change it to match your machine, e.g. `/dev/tty.usbmodem…` on macOS).

**Motion (Arduino):** flash `main.ino` to your board (wired to a stepper motor via pins 8–11), then run the Python script to start streaming coordinates.

**Camera study (optional):**

```bash
python3 positions.py
```

> !!! *Small heads-up:* `main.py` currently has a (now broken) Roboflow API key hard-coded in it. it's worth moving that into an environment variable and rotating the key

---

<div align="center">

*Made by [**natsxki**](https://github.com/natsxki) 

</div>
