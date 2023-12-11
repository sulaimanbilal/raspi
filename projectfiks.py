import numpy as np
import cv2
import RPi.GPIO as GPIO
from time import sleep
import threading

# Function to read camera in a separate thread
def camera_thread():
    global frame, duty_cycle, exit_thread
    while not exit_thread:
        _, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
        mask = np.ones_like(thresh) * 255
        diff = cv2.absdiff(thresh, mask)

        contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 60 and h > 30:
                cv2.drawContours(frame, [contour], 0, (50, 230, 240), 2)
                center_x1 = x + w // 2
                center_y1 = y + h // 2
                cv2.circle(frame, (center_x1, center_y1), 3, (0, 0, 255), -1)
                #cv2.putText(frame, "Short", (x, y - 10), font, font_scale, font_color, 1)
                duty_cycle = 1
            else:
                cv2.drawContours(frame, [contour], 0, (0, 255, 0), 2)
                center_x2 = x + w // 2
                center_y2 = y + h // 2
                cv2.circle(frame, (center_x2, center_y2), 3, (255, 0, 255), -1)
                #cv2.putText(frame, "Long", (x, y - 10), font, font_scale, font_color, 1)
                duty_cycle = 10

        pwm.ChangeDutyCycle(duty_cycle)
        sleep(0.1)

# Set up camera, GPIO, and PWM as before
cam = cv2.VideoCapture(0)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 50)
pwm.start(0)

# Initialize variables
frame = None
duty_cycle = 0
exit_thread = False

# Define font parameters
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_color = (255, 255, 255)

# Start camera thread
camera_thread = threading.Thread(target=camera_thread)
camera_thread.start()

# Main thread for keyboard input and displaying frame
while True:
    if frame is not None:
        cv2.imshow("frame", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        exit_thread = True
        break

# Cleanup
cam.release()
cv2.destroyAllWindows()
pwm.stop()
GPIO.cleanup()