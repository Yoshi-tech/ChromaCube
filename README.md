# ChromaCube

**ChromaCube** is a real-time computer vision system for detecting and tracking Rubik’s Cube facelet colors using a live camera feed. It combines OpenCV-based color analysis with a Flask-powered web interface to visualize a stabilized 3×3 grid and color classifications in real time.

The project is designed with a clear separation between **vision processing (Python)** and **visualization (web frontend)**, making it suitable for technical demos, experimentation, and future solver integration.

---

## Features

- Real-time camera capture using OpenCV
- Stabilized region-of-interest (ROI) for consistent cube detection
- Automatic 3×3 grid subdivision
- Per-facelet average color extraction
- Temporal smoothing to reduce jitter and lighting noise
- Center-face color classification
- Live MJPEG video streaming to the browser
- Web-based grid visualization synced with camera input
- Modular, extensible Python architecture

---

## Overview

ChromaCube operates as follows:

1. Captures a live video stream from the system camera
2. Locks onto a fixed, centered ROI sized to a Rubik’s Cube face
3. Divides the ROI into a 3×3 grid
4. Computes average color values per facelet
5. Applies temporal smoothing for stability
6. Streams:
   - Annotated live video
   - Facelet color data to the web frontend

---

## Tech Stack

### Backend
- Python 3
- Flask
- OpenCV
- NumPy

### Frontend
- HTML5
- Embedded CSS
- JavaScript (Fetch API)
