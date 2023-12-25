import cv2
import mediapipe as mp
import math
import pandas as pd
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Set the screen resolution to 1920x1080
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Width
cap.set(4, 1080)  # Height

# Define the desired output window size
desired_width = 1080  # Adjust as needed
desired_height = 720   # Adjust as needed

# Define finger tip IDs
tip_ids = [8, 12, 16, 20]  # Finger tip landmarks

# Set the hand distinction threshold
threshold = 0.2  # Adjust as needed

# Initialize variables for angle calculation and error tracking
thumb_angle, index_finger_angle, middle_finger_angle, ring_finger_angle, pinky_finger_angle = 0, 0, 0, 0, 0
data = []

# Create a pandas DataFrame to store the data
columns = ['Timestamp', 'Middle_Finger_Angle', 'Average_Angle', 'Error']

# Additional metrics variables
start_time = time.time()
frame_count = 0
successful_frames = 0
total_latency = 0

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
                base_x, base_y = landmarks.landmark[12].x, landmarks.landmark[12].y
                tip_x, tip_y = landmarks.landmark[16].x, landmarks.landmark[16].y
                angle = math.degrees(math.atan2(tip_y - base_y, tip_x - base_x))
                servo_angle = max(0, min(180, int(90 + angle)))
                # Update finger angles
                thumb_angle = 180 - math.degrees(math.atan2(landmarks.landmark[4].y - base_y, landmarks.landmark[4].x - base_x))
                index_finger_angle =180 - math.degrees(math.atan2(landmarks.landmark[8].y - base_y, landmarks.landmark[8].x - base_x))
                middle_finger_angle = angle
                ring_finger_angle = math.degrees(math.atan2(landmarks.landmark[16].y - base_y, landmarks.landmark[16].x - base_x))
                pinky_finger_angle = math.degrees(math.atan2(landmarks.landmark[20].y - base_y, landmarks.landmark[20].x - base_x))

                # Calculate the average angle of all fingers on the left hand
                angle_avg = (thumb_angle + index_finger_angle + middle_finger_angle + ring_finger_angle + pinky_finger_angle) / 5

                # Calculate the error as the difference between the measured angle and the average angle
                error = abs(angle - angle_avg)/angle_avg

                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
                print(f'Thumb: {thumb_angle:.2f}, Index: {index_finger_angle:.2f}, Middle: {middle_finger_angle:.2f}, Ring: {ring_finger_angle:.2f}, Pinky: {pinky_finger_angle:.2f}')
                # Display the angle, average angle, and error on the rightmost corner of the screen
                angle_text = f'Middle Finger Angle: {angle:.2f}'
                avg_angle_text = f'Average Angle: {angle_avg:.2f}'
                error_text = f'Error: {error:.2f}'
                text_size, _ = cv2.getTextSize(angle_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                text_x = frame.shape[1] - text_size[0] - 10
                cv2.putText(frame, angle_text, (text_x, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, avg_angle_text, (text_x, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, error_text, (text_x, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Calculate and store error in detection
                timestamp = time.time()
                data.append([timestamp, angle, angle_avg, error])

                # Add code to calculate and display recognition accuracy
                recognition_accuracy = 1-error
                accuracy_text = f'Recognition Accuracy: {recognition_accuracy:.2f}%'
                cv2.putText(frame, accuracy_text, (text_x, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Additional metrics
                frame_count += 1
                successful_frames += 1

                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time
                real_time_performance_text = f'Real-time Performance: {fps:.2f} FPS'

                robustness = (successful_frames / frame_count) * 100
                robustness_text = f'Robustness: {robustness:.2f}%'

                latency = time.time() - timestamp
                total_latency += latency
                average_latency = total_latency / frame_count
                latency_text = f'Latency: {average_latency:.4f} seconds'

                # Display additional metrics on the screen
                cv2.putText(frame, real_time_performance_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, robustness_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, latency_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            else:
                # Right Hand (Control LEDs)
                fingers = []
                for id in tip_ids:
                    if landmarks.landmark[id - 1].y < landmarks.landmark[id - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                led_count = fingers.count(1)
                # Display LED count on the left corner of the screen
                cv2.putText(frame, f'LED Count: {led_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Control', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# Convert the data list to a DataFrame
df = pd.DataFrame(data, columns=columns)

# Save DataFrame to a CSV file
df.to_csv('hand_control_data.csv', index=False)

cap.release()
cv2.destroyAllWindows()
