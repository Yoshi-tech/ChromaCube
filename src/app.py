from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np

app = Flask(__name__)

# -----------------------
# Helper functions
# -----------------------
def get_sticker_colors(face_img):
    size = face_img.shape[0]
    cell_size = size // 3
    colors = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = face_img[i*cell_size:(i+1)*cell_size, j*cell_size:(j+1)*cell_size]
            mean_color = cv2.mean(cell)[:3]
            row.append(tuple(map(int, mean_color)))
        colors.append(row)
    return colors

def get_face(colors):
    return colors[1][1]

def bgr_to_color_name(bgr):
    hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    h, s, v = hsv
    if s < 50 and v > 200:
        return "White"
    elif 0 <= h <= 10 or 170 <= h <= 180:
        return "Red"
    elif 11 <= h <= 25:
        return "Orange"
    elif 26 <= h <= 35:
        return "Yellow"
    elif 36 <= h <= 85:
        return "Green"
    elif 90 <= h <= 130:
        return "Blue"
    else:
        return "Unknown"

# -----------------------
# Initialize capture and global variables
# -----------------------
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
buffer = [[[], [], []], [[], [], []], [[], [], []]]  # smoothing buffer
current_stickers = [[(0,0,0) for _ in range(3)] for _ in range(3)]
current_center_color_name = "Unknown"

roi_size = 200
roi_half = roi_size // 2
cx, cy = frame_width // 2, frame_height // 2

# -----------------------
# Generate frames for streaming
# -----------------------
def generate_frames():
    global current_stickers, current_center_color_name
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_disp = frame.copy()

        # ROI
        x1 = cx - roi_half
        y1 = cy - roi_half
        x2 = cx + roi_half
        y2 = cy + roi_half
        roi = frame[y1:y2, x1:x2]
        cv2.rectangle(frame_disp, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Sticker colors with smoothing
        stickers = get_sticker_colors(roi)
        N = 5  # buffer size
        for i in range(3):
            for j in range(3):
                buffer[i][j].append(stickers[i][j])
                if len(buffer[i][j]) > N:
                    buffer[i][j].pop(0)
                avg_color = np.mean(buffer[i][j], axis=0).astype(int)
                stickers[i][j] = tuple(avg_color)

        # Update global stickers
        current_stickers = stickers
        current_center_color_name = bgr_to_color_name(get_face(stickers))

        # Draw center color text on video
        cv2.putText(frame_disp, f"Center Color: {current_center_color_name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        # Encode frame as JPEG
        ret, buffer_jpg = cv2.imencode('.jpg', frame_disp)
        frame_bytes = buffer_jpg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# -----------------------
# Flask routes
# -----------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current_colors')
def current_colors():
    # Convert BGR tuples to RGB strings for HTML
    stickers_rgb = [[f'rgb({c[2]},{c[1]},{c[0]})' for c in row] for row in current_stickers]
    return jsonify({
        "center_color_name": current_center_color_name,
        "stickers": stickers_rgb
    })

# -----------------------
# Run app
# -----------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
