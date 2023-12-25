# Hand Gesture Control with MediaPipe and Arduino

## Overview

This repository contains Python scripts for hand gesture control using MediaPipe for hand tracking and gesture recognition and Arduino for controlling servo motors and LEDs. The system can recognize gestures performed with the left hand to control a servo motor and gestures with the right hand to control LEDs.

## Features

- Real-time hand tracking using MediaPipe Hands.
- Left-hand gesture control to manipulate a servo motor.
- Right-hand gesture control to change the state of LEDs.
- Recognition accuracy and performance metrics displayed on the screen.
- Data logging and analysis for gesture angles.

## Setup

### Hardware Requirements

- Webcam
- Arduino board
- Servo motor
- LEDs

### Software Requirements

- Python 3.x
- OpenCV
- Mediapipe
- Pandas
- Pyfirmata

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/hand-gesture-control.git
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Connect your Arduino board and update the COM port in the script accordingly.

## Usage

### Gesture Control with Servo Motor

Run the following script to test you environment setup:

```bash
python err_test.py
```

### Gesture Control with LEDs, Relay and Servo motor

Run the following script to control LEDs/Relay and Servo motor based on hand gestures:

```bash
python final_test.py
```

## Documentation

Detailed explanations of the code and usage can be found in the [Wiki](https://github.com/your-username/hand-gesture-control/wiki).

## Data Analysis

The hand gesture data is logged and saved to a CSV file (`hand_control_data.csv`). You can analyze this data for further insights and improvements.

## License

This project is licensed under the [Apache 2.0](LICENSE).

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/)
- [Pyfirmata](https://pyfirmata.readthedocs.io/)
- [OpenCV](https://opencv.org/)

## Contributing

Feel free to contribute by opening issues, proposing new features, or submitting pull requests.

```

Make sure to replace the placeholders like `your-username` with your actual GitHub username. Also, consider including a demo GIF or screenshots to showcase the project in action.
