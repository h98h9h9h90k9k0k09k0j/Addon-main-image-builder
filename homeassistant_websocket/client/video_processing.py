import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import os
# Does processing on the received video data
# Should respond to the server depending on the type of processing

class VideoProcessor:
    @staticmethod
    async def process_video(message, websocket, clients):
        # Placeholder for video processing logic
        pass

    @staticmethod
    async def camera_adj(video_source)

    @staticmethod
    async def rt_face_recognition(video_source, message, websocket): #real time
        # Make sure to enable camera
       # https://towardsdatascience.com/real-time-face-recognition-an-end-to-end-project-b738bb0f7348

        cam = cv2.VideoCapture(video_source)
        cam.set(3, 640) # set video width
        cam.set(4, 480) # set video height
        face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        # For each person, enter one numeric face id
        face_id = input('\n enter user id end press <return> ==>  ')
        id_str, name = face_id.split()
        id = int(id_str)
        print("\n [INFO] Initializing face capture. Look the camera and wait ...")
        # Initialize individual sampling face count
        count = 0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
                count += 1
                # Save the captured image into the datasets folder
                cv2.imwrite("dataset/User." + str(face_id) + '.' +
                            str(count) + ".jpg", gray[y:y+h,x:x+w])
                cv2.imshow('image', img)
            k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
            if k == 27:
                break
            elif count >= 30: # Take 30 face sample and stop video
                 break
        # Do a bit of cleanup
        print("\n [INFO] Exiting Program and cleanup stuff")
        face_training()
        cam.release()
        cv2.destroyAllWindows()

    async def face_training():
        pass

    @staticmethod
    async def motion_detection(video_source, message, websocket, clients):
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            print("Error: Unable to open video source")
            return
        
        fgbg = cv2.createBackgroundSubtractorMOG2() #fgbg = foreground/background
        while True:
            ret, frame = cap.read()

            if not ret:
                break
            fgmask = fgbg.apply(frame) # apply background subtraction -> foreground mask image
            _, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY[1]) #colors above 200 turns white. [1] = thresholded image
            contours, hierarchy = cv2. findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #RETR_EXTERNAL = external contours, CHAIN... = compress to save memory
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) #rectangle drawn around object if area is big enough
            cv2.imshow('frame', frame) #display frame

            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break #break loop with 'q'
        cap.release()
        cv2.destroyAllWindows()

    @staticmethod
    async def motion_detected(video_source):
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            print("Error: Unable to open video source")
            return
        
        fgbg = cv2.createBackgroundSubtractorMOG2() #fgbg = foreground/background
        while True:
            ret, frame = cap.read()

            if not ret:
                break
            fgmask = fgbg.apply(frame) # apply background subtraction -> foreground mask image
            _, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY[1]) #colors above 200 turns white. [1] = thresholded image
            contours, hierarchy = cv2. findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #RETR_EXTERNAL = external contours, CHAIN... = compress to save memory
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:
                    return True

        cap.release()
        cv2.destroyAllWindows()

        return False #not sure if necessary

    @staticmethod
    async def emotion_recognition(video_source, message):
        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Start capturing video
        cap = cv2.VideoCapture(video_source)

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Convert grayscale frame to RGB format
            rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                # Extract the face ROI (Region of Interest)
                face_roi = rgb_frame[y:y + h, x:x + w]


                # Perform emotion analysis on the face ROI
                result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)

                # Determine the dominant emotion
                emotion = result[0]['dominant_emotion']

                # Draw rectangle around face and label with predicted emotion
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                message = f'Emotion "{emotion}" detected'
                return message
            # Display the resulting frame
            cv2.imshow('Real-time Emotion Detection', frame, emotion)

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the capture and close all windows
        cap.release()
        cv2.destroyAllWindows()

    # Logic to send commands back to server depending on the processing
    @staticmethod
    async def send_command(message, websocket, clients):
        # Placeholder for sending commands back to server
        pass