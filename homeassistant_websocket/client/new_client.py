import asyncio
import websockets
import json
import os
import cv2
import logging
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import numpy as np
from deepface import DeepFace
import socket

logging.basicConfig(level=logging.INFO)

class NewClient:
    def __init__(self, websocket_url, save_dir='detected_faces'):
        self.websocket_url = websocket_url
        self.rtsp_url = None
        self.capture = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.websocket = None
        self.save_dir = save_dir
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.loop = None

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.connect_websocket())
            loop.run_forever()
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)
        finally:
            loop.close()

    def is_network_available(self):
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            return False

    async def connect_websocket(self):
        logging.info("Client trying to connect to the server.")
        if not self.is_network_available():
            logging.error("Network is unreachable. Please check your internet connection.")
            return

        try:
            async with websockets.connect(self.websocket_url) as websocket:
                self.websocket = websocket
                response = await websocket.recv()
                message = json.loads(response)
                logging.info(f"< Response from server: {message}")  # Pong

                logging.info("Client trying to specify client type to the server.")
                await websocket.send(json.dumps({"client_type": "camera_client"}))
                response = await websocket.recv()
                message = json.loads(response)
                logging.info(f"< Response from server: {message}")  # Pong

                try:
                    while True:
                        await self.listen_to_websocket()
                except KeyboardInterrupt as e:
                    logging.info(f"Closing Client: {e}")
                finally:
                    await websocket.close()
        except websockets.exceptions.ConnectionClosedError as e:
            logging.error(f"Connection to the server closed: {e}")
        except websockets.exceptions.WebSocketException as e:
            logging.error(f"WebSocket error occurred: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

    async def listen_to_websocket(self):
        logging.info("Client is now listening to the server.")
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosedError as e:
            logging.error(f"Connection to the server closed: {e}")
        except websockets.exceptions.WebSocketException as e:
            logging.error(f"WebSocket error occurred: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

    async def handle_message(self, message):
        logging.info(f"Received message: {message}")
        try:
            data = json.loads(message)

            if data['action'] == 'start_motion_detection':
                self.stop_processing()
                self.capture = cv2.VideoCapture(self.rtsp_url)
                self.loop.run_in_executor(self.executor, self.motion_detection, self.capture)
            elif data['action'] == 'start_face_recognition':
                self.stop_processing()
                self.capture = cv2.VideoCapture(self.rtsp_url)
                self.loop.run_in_executor(self.executor, self.face_recognition, self.capture)
            elif data['action'] == 'start_emotion_recognition':
                self.stop_processing()
                self.capture = cv2.VideoCapture(self.rtsp_url)
                self.loop.run_in_executor(self.executor, self.emotion_recognition, self.capture)
            elif data['action'] == 'start_motion_detected':
                self.stop_processing()
                self.capture = cv2.VideoCapture(self.rtsp_url)
                self.loop.run_in_executor(self.executor, self.motion_detected, self.capture)
            elif data['action'] == 'stop_processing':
                self.stop_processing()
            elif data['action'] == 'status':
                await self.send_status()
            elif data['action'] == 'get_files':
                await self.send_files_list()
            elif data['action'] == 'get_file':
                await self.send_file(data['filename'])
            elif data['action'] == 'set_video_url':
                self.rtsp_url = data['rtsp_url']
            else:
                logging.error(f"Error: Unknown action: {data['action']}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON message: {e}")
        except KeyError as e:
            logging.error(f"Error accessing key in JSON message: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

    async def send_status(self):
        try:
            status = "processing" if self.capture and self.capture.isOpened() else "stopped"
            await self.websocket.send(json.dumps({'status': status}))
            logging.info(f"Sent status: {status}")
        except Exception as e:
            logging.error(f"An error occurred while sending status: {e}", exc_info=True)

    def stop_processing(self):
        try:
            if self.capture and self.capture.isOpened():
                self.capture.release()
            self.executor.shutdown(wait=False)
            logging.info("Stopped video processing")
        except Exception as e:
            logging.error(f"An error occurred while stopping processing: {e}", exc_info=True)

    async def send_file(self, filename):
        try:
            filepath = os.path.join(self.save_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as file:
                    content = file.read()
                    await self.websocket.send(content)
                logging.info(f"Sent file: {filename}")
            else:
                await self.websocket.send(json.dumps({'error': 'File not found'}))
                logging.info(f"File not found: {filename}")
        except Exception as e:
            logging.error(f"An error occurred while sending file: {e}", exc_info=True)

    async def change_camera_settings(self, width, height, framerate):
        try:
            cam = self.capture
            cam.set(3, int(width))
            cam.set(4, int(height))
            cam.set(cv2.CAP_PROP_FPS, framerate)
        except Exception as e:
            logging.error(f"An error occurred while changing camera settings: {e}", exc_info=True)

    def face_training(self):
        try:
            path = 'dataset'
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

            def getImagesAndLabels(path):
                imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
                faceSamples = []
                ids = []
                for imagePath in imagePaths:
                    PIL_img = Image.open(imagePath).convert('L')
                    img_numpy = np.array(PIL_img, 'uint8')
                    face_id = os.path.split(imagePath)[-1].split(".")[1]
                    id_str = face_id.split()[0]
                    id = int(id_str)
                    faces = detector.detectMultiScale(img_numpy)
                    for (x, y, w, h) in faces:
                        faceSamples.append(img_numpy[y:y + h, x:x + w])
                        ids.append(id)
                return faceSamples, ids

            logging.info("Training faces. This will take a few seconds. Wait...")
            faces, ids = getImagesAndLabels(path)
            recognizer.train(faces, np.array(ids))
            recognizer.write('trainer/trainer.yml')
            logging.info(f"{len(np.unique(ids))} faces trained. Exiting Program.")
        except cv2.error as e:
            logging.error(f"OpenCV error occurred: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

    def face_recognition(self):
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read('trainer/trainer.yml')
            cascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            faceCascade = cv2.CascadeClassifier(cascadePath)
            font = cv2.FONT_HERSHEY_SIMPLEX

            cam = self.capture
            cam.set(3, 640)
            cam.set(4, 480)
            minW = 0.1 * cam.get(3)
            minH = 0.1 * cam.get(4)

            while True:
                ret, img = cam.read()
                if not ret:
                    logging.error("Failed to capture image from camera")
                    break

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(int(minW), int(minH)))

                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                    confidence = round(100 - confidence)
                    if confidence > 20:
                        id = str(id)
                    else:
                        id = "unknown"
                    cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                    cv2.putText(img, f"confidence: {confidence}", (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

                cv2.imshow('camera', img)
                k = cv2.waitKey(10) & 0xff
                if k == 27:
                    break

            logging.info("Exiting Program and cleanup.")
            cam.release()
            cv2.destroyAllWindows()
        except cv2.error as e:
            logging.error(f"OpenCV error occurred: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

    async def rt_face_recognition(self):
        try:
            cam = self.capture
            cam.set(3, 640)
            cam.set(4, 480)
            face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            face_id = input('\n enter user id end press <return> ==>  ')
            id_str, name = face_id.split()
            id = int(id_str)
            logging.info("Initializing face capture. Look at the camera and wait...")

            count = 0
            while True:
                ret, img = cam.read()
                if not ret:
                    logging.error("Failed to capture image from camera")
                    break

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_detector.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    count += 1
                    cv2.imwrite("dataset/User." + str(id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])
                    cv2.imshow('image', img)

                k = cv2.waitKey(100) & 0xff
                if k == 27 or count >= 30:
                    break

            logging.info("Exiting Program and cleanup.")
            cam.release()
            cv2.destroyAllWindows()
        except cv2.error as e:
            logging.error(f"OpenCV error occurred: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

    async def motion_detected(self):
        try:
            cap = self.capture
            if not cap.isOpened():
                logging.error("Error: Unable to open video source")
                return False

            fgbg = cv2.createBackgroundSubtractorMOG2()
            while True:
                ret, frame = cap.read()
                if not ret:
                    logging.error("Failed to read frame from video source")
                    break

                fgmask = fgbg.apply(frame)
                _, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:
                        return True

            cap.release()
            cv2.destroyAllWindows()
        except cv2.error as e:
            logging.error(f"OpenCV error occurred: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

        return False

    async def emotion_recognition(self):
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            cap = self.capture

            while True:
                ret, frame = cap.read()
                if not ret:
                    logging.error("Failed to capture image from camera")
                    break

                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)
                faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in faces:
                    face_roi = rgb_frame[y:y + h, x:x + w]
                    result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                    emotion = result[0]['dominant_emotion']
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    logging.info(f'Emotion "{emotion}" detected')

                cv2.imshow('Real-time Emotion Detection', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
        except cv2.error as e:
            logging.error(f"OpenCV error occurred: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)
