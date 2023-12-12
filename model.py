from keras.models import load_model  
import cv2 
import numpy as np
from gpiozero import Servo
from time import sleep

np.set_printoptions(suppress=True)

model = load_model("round_end_cap_model.h5", compile=False)

class_names = open("labels.txt", "r").readlines()

camera = cv2.VideoCapture(0)

# Initialize servo motor
servo = Servo(12)  

while True:
   
    ret, image = camera.read()

    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

    cv2.imshow("Webcam Image", image)

    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

    image = (image / 127.5) - 1

    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    print("Class:", class_name[2:], end="")
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

    # Control servo based on class
    if "fine" in class_name:
        servo.value = 0.5  # Rotate to 60 degrees
    elif "defect" in class_name:
        servo.value = -0.5  # Rotate to -60 degrees
    else:
        servo.value = 0  # Stop servo

    keyboard_input = cv2.waitKey(1)

    if keyboard_input == 27:
        break

# Cleanup
camera.release()
cv2.destroyAllWindows()
servo.value = 0  # Stop the servo before exiting