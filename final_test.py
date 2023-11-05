import cv2
import mediapipe as mp
import math
import pyfirmata

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Initialize pyFirmata to communicate with the Arduino
board = pyfirmata.Arduino('COM7')  # Replace with your Arduino port

# Define servo and LED pins
servo_pin = 11  # Change this to the appropriate pin on your Arduino
led_pins = [13, 12, 10, 9]  # Define the pins for your LEDs

# Initialize the servo
servo = board.get_pin(f'd:{servo_pin}:s')

# Initialize the LEDs
leds = [board.get_pin(f'd:{pin}:o') for pin in led_pins]

# Set the screen resolution to 1920x1080
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Width
cap.set(4, 1080)  # Height

# Define the desired output window size
desired_width = 1080  # Adjust as needed
desired_height = 720   # Adjust as needed

# Define finger tip IDs and LED count
tipIds = [8, 12, 16, 20]  # Finger tip landmarks
led_count = 0

# Set the hand distinction threshold
threshold = 0.2  # Adjust as needed

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    # Increase the size of the output window
    frame = cv2.resize(frame, (desired_width, desired_height))

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Check for left and right hands
            if landmarks.landmark[8].x < landmarks.landmark[20].x - threshold:
                # Left Hand (Control Servo)
                for i, led in enumerate(leds):
                    led.write(0)
                
                # Extract the landmarks for the middle finger (Landmarks 12-16)
                middle_finger_landmarks = [landmarks.landmark[i] for i in range(12, 17)]

                # Calculate the angle between the middle finger and the positive x-axis
                base_x, base_y = middle_finger_landmarks[0].x, middle_finger_landmarks[0].y
                tip_x, tip_y = middle_finger_landmarks[4].x, middle_finger_landmarks[4].y
                angle = math.degrees(math.atan2(tip_y - base_y, tip_x - base_x))

                # Map the angle to the servo's range (0 to 180 degrees)
                servo_angle = max(0, min(180, int(90 + angle)))

                # Control the servo motor
                servo.write(servo_angle)

                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Display the angle on the rightmost corner of the screen
                angle_text = f'Middle Finger Angle: {angle:.2f}'
                text_size, _ = cv2.getTextSize(angle_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                text_x = frame.shape[1] - text_size[0] - 10
                cv2.putText(frame, angle_text, (text_x, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # Right Hand (Control LEDs)
                # Calculate the LED count based on finger gestures
                fingers = []
                for id in tipIds:
                    if landmarks.landmark[id - 1].y < landmarks.landmark[id - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                led_count = fingers.count(1)

                # Display LED count on the left corner of the screen
                cv2.putText(frame, f'LED Count: {led_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if led_count == 0:
                    leds[0].write(0)
                    leds[1].write(0)
                    leds[2].write(0)
                    leds[3].write(0)
                elif led_count == 1:
                    leds[0].write(1)
                    leds[1].write(0)
                    leds[2].write(0)
                    leds[3].write(0)
                elif led_count == 2:
                    leds[0].write(1)
                    leds[1].write(1)
                    leds[2].write(0)
                    leds[3].write(0)
                elif led_count == 3:
                    leds[0].write(1)
                    leds[1].write(1)
                    leds[2].write(1)
                    leds[3].write(0)
                elif led_count == 4:
                    leds[0].write(1)
                    leds[1].write(1)
                    leds[2].write(1)
                    leds[3].write(1)

                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Control', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
board.exit()