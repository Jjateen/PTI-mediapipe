from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import math
import pyfirmata

app = Flask(__name__)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Initialize pyFirmata to communicate with the Arduino
board = pyfirmata.Arduino('/dev/ttyACM0')  # Replace with your Arduino port

# Define servo and LED pins
servo_pin = 9  # Change this to the appropriate pin on your Arduino
led_pins = [13, 12, 11, 10]  # Define the pins for your LEDs

# Initialize the servo
servo = board.get_pin(f'd:{servo_pin}:s')

# Initialize the LEDs
leds = [board.get_pin(f'd:{pin}:o') for pin in led_pins]

# Set the screen resolution to 1920x1080
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Width
cap.set(4, 1080)  # Height

# Define finger tip IDs and LED count
tipIds = [8, 12, 16, 20]  # Finger tip landmarks
led_count = 0

# Set the hand distinction threshold
threshold = 0.2  # Adjust as needed

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Increase the size of the output window
        frame = cv2.resize(frame, (1080, 720))  # Adjust the size as needed

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Hands
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                if landmarks.landmark[8].x < landmarks.landmark[20].x - threshold:
                    for i, led in enumerate(leds):
                        led.write(0)
                    
                    middle_finger_landmarks = [landmarks.landmark[i] for i in range(12, 17)]
                    base_x, base_y = middle_finger_landmarks[0].x, middle_finger_landmarks[0].y
                    tip_x, tip_y = middle_finger_landmarks[4].x, middle_finger_landmarks[4].y
                    angle = math.degrees(math.atan2(tip_y - base_y, tip_x - base_x))
                    servo_angle = max(0, min(180, int(90 + angle)))
                    servo.write(servo_angle)

                    mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                    angle_text = f'Middle Finger Angle: {angle:.2f}'
                    text_size, _ = cv2.getTextSize(angle_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                    text_x = frame.shape[1] - text_size[0] - 10
                    cv2.putText(frame, angle_text, (text_x, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    fingers = []
                    for id in tipIds:
                        if landmarks.landmark[id - 1].y < landmarks.landmark[id - 2].y:
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    led_count = fingers.count(1)

                    cv2.putText(frame, f'LED Count: {led_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    for i, led in enumerate(leds):
                        if i < led_count:
                            led.write(1)
                        else:
                            led.write(0)

                    mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
