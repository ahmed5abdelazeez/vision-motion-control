# Usage Guide This document explains how to run the Vision–Motion–Control system and connect the software with the hardware. --- 
## Step 1: Hardware Setup 
1. Connect the Arduino (or other supported microcontroller) to your laptop using a USB cable.
2. Open the Arduino IDE. 3.
3. Upload the Arduino sketch located in:
4. Make sure the upload completes successfully.
5. Identify the serial port used by the board: - Windows: COM3, COM4, etc. - Linux: /dev/ttyUSB0 or /dev/ttyACM0 - macOS: /dev/tty.usbmodemXXXX ---

## Step 2: Open the Software Project 
1. Navigate to the software directory:
2. Open the Tracking_hand.py Python file:
## Step 3: Configure Serial Communication 
1. Inside Tracking.py, locate the serial communication settings.
2. Update the serial port and baud rate according to your system:
python
SERIAL_PORT = "COM3"   # Change to your Arduino serial port
BAUD_RATE = 115200       # Must match the Arduino baud rate

## Step 4: Configure Camera Index

In main.py, locate the camera configuration section.

Set the camera index used by OpenCV:

CAMERA_INDEX = 0  # 0 = default camera, 1 = external camera

## Step 5: Install Required Python Libraries

Ensure Python 3 is installed on your system.

Install the required Python libraries using pip:

pip install opencv-python mediapipe pyserial


(Optional) Use a virtual environment to manage dependencies.

## Step 6: Run the Program

Open a terminal inside the software/ directory.

Run the Python application:

python main.py
