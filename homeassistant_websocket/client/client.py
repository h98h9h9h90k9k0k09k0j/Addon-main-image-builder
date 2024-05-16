# main client module
import asyncio
import logging
import json
import websockets
import base64
import cv2
import numpy as np
import psutil
import os
import aiofiles
from datetime import datetime
from .video_processing import VideoProcessor
from concurrent.futures import ThreadPoolExecutor


class Client:
    def __init__(self, client_id: int, uri: str):
        self.uri = uri
        self.client_id = client_id
        self.status = 0
        self.capture_task = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.video_sources = ["tcp://192.168.1.26:8080", "tcp://192.168.1.100:8080"]
        self.current_task = None
        self.video_feed = None

    async def get_cpu_usage(self):
        return psutil.cpu_percent()

    async def update_status(self, websocket):
        self.status = await self.get_cpu_usage()
        if self.status > 80:
            await websocket.send(f"Caution! Client {self.client_id} CPU is working at {self.status}%")

    async def send_frames_to_server(self, websocket):
        self.img_folder = "img_motion_det"
        try:
            for filename in os.listdir(self.img_folder):
                if filename.endswith(".jpg"):
                    image_path = os.path.join(self.img_folder, filename)
                    async with aiofiles.open(image_path, mode="rb") as f:
                        image_data = await f.read()
                    encoded_image = base64.b64encode(image_data).decode("utf-8") # skal måske ikke bruges
                    await websocket.send(encoded_image) # Overvej om det er json.dump vi skal bruge
                    print(f"Sent {filename} to the server.")
                    os.remove(image_path)  # Delete the sent image. Image no longer occupies space. Do we wanna save this?
            print("All frames sent to the server.")
        except Exception as e:
            logging.error(f"Error occurred while sending frames to the server: {e}")

    def delete_frames(self):
        try:
            for filename in os.listdir(self.img_folder):
                if filename.endswith(".jpg"):
                    image_path = os.path.join(self.img_folder, filename)
                    os.remove(image_path)
                    print(f"Deleted {filename}.")
            print("All frames deleted.")
        except Exception as e:
            logging.error(f"Error occurred while deleting frames: {e}")

    async def process(self, websocket):
        try:
            if self.current_task == "motion_detection":
                # Perform motion detection
                logging.info("Performing motion detection")
                VideoProcessor.motion_detection(self.video_feed)
                
            elif self.current_task == "face_detection":
                # Perform emotion recognition
                logging.info("Performing face detection")
                VideoProcessor.face_recognition(self.video_feed)

            else:
                # Default processing
                logging.info("Performing default processing")
                self.capture_video(websocket)

        except Exception as e:
            logging.error(f"Error occurred during processing: {e}")
            return None

    async def start_listening(self, websocket):
        try:
            logging.info(f"Client {self.client_id} is now listening to the server.")
            await self.ping(websocket)
            #await self.update_status(websocket)
            while True:
                response = await websocket.recv()
                message = json.loads(response)
                if "start_video" in message:
                    await self.start_video_capture()
                elif "stop_video" in message:
                    await self.stop_video_capture()
                elif "process" in message:
                    await self.process(websocket)
                elif "motion_detection" in message:
                    self.current_task = "motion_detection"
                    logging.info("Starting motion detection")
                elif "stop_motion_detection" in message:
                    self.current_task = None
                    logging.info("Stopping motion detection")
                elif "face_detection" in message:
                    self.current_task = "face_detection"
                    logging.info("Starting face_detection")
                elif "stop_face_detection" in message:
                    self.current_task = None
                    logging.info("Stopping face_detection")
                else:
                    logging.info(f"Unknown command received: {message}")
        except websockets.exceptions.ConnectionClosedError as e:
            logging.error(f"Connection to server closed unexpectedly: {e}")
        except Exception as e:
            logging.error(f"Error occurred during the communication with server: {e}")

    async def start_video_capture(self):
        for address in self.video_sources:
            logging.info(f"Trying to capture from {address}")
            cap = cv2.VideoCapture(address)
            if cap.isOpened():
                logging.info(f"Successfully started capturing from {address}")
                self.video_feed = cap
            else:
                logging.warning(f"Failed to capture from {address}")
        if self.capture_task is None:
            logging.error("Failed to start video capture from all sources")

    async def stop_video_capture(self):
        if self.capture_task:
            self.capture_task.cancel()
            self.capture_task = None
            self.video_feed.release()
            self.video_feed = None
            logging.info("Video capture stopped")

    async def capture_video(self, websocket):
        try:
            while self.video_feed.isOpened():
                ret, frame = self.video_feed.read()
                if not ret:
                    break
                await websocket.send(json.dumps("frame read succesfully"))
                #_, buffer = cv2.imencode('.jpg', frame)
                #frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
        except Exception as e:
            logging.error(f"Error occurred during video capture: {e}")
        finally:
            self.video_feed.release()


    
    async def connect(self):
        logging.info(f"Client {self.client_id} trying to connect to the server.")
        async with websockets.connect(self.uri) as websocket:
            response = await websocket.recv()
            message = json.loads(response)
            logging.info(f"< Response from server: {message}")  # Pong

            logging.info(f"Client {self.client_id} trying to specify client type to the server.")
            await websocket.send(json.dumps({"client_type":"camera_client"}))
            response = await websocket.recv()
            message = json.loads(response)
            logging.info(f"< Response from server: {message}")  # Pong
            try:
                while True:
                    await self.start_listening(websocket)
            except KeyboardInterrupt as e:
                print(f"Closing Client: {e}")
            finally:
                await websocket.close()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        loop.run_forever()

    async def ping(self, websocket, ping_pong_interval_sec=10):
        try:
            await websocket.send(json.dumps({"message": "ping"}))
            response = await websocket.recv()
            logging.info(f"< Response from the server: {response}")
        except Exception as e:
            logging.error(f"Error occurred during ping-pong: {e}")

    async def get_IoT_ip_address(websocket):
        try:
            remote_ip = websocket.remote_address[0]
            return remote_ip
        except Exception as e:
            logging.error(f"Error occurred while retrieving remote IP address: {e}")
            return None

# Task list: 1) G̶e̶n̶n̶e̶m̶g̶a̶n̶g̶.̶ 2) Logik til framehandling + tags/homegrown "metadata" fra videofeed til server. 3) L̶a̶v̶ e̶n̶ c̶o̶m̶m̶a̶n̶d̶ l̶i̶s̶t̶ + m̶a̶n̶a̶g̶e̶m̶e̶n̶t̶.̶ 4) L̶o̶g̶g̶i̶n̶g̶.

# E̶t̶a̶b̶l̶e̶r̶ p̶i̶n̶g̶ c̶o̶n̶n̶e̶c̶t̶i̶o̶n̶ + d̶e̶t̶e̶c̶t̶ m̶o̶t̶i̶o̶n̶ p̶l̶a̶c̶e̶h̶o̶l̶d̶e̶r̶

# Overvej Executor til at wrap video processoren i en stand alone thread. Threading or await?
# Refactor structure

# Command list: H̶a̶n̶d̶s̶h̶a̶k̶e̶, c̶a̶m̶e̶r̶a̶ s̶e̶t̶t̶i̶n̶g̶s̶, data transfer, request/response, 
# Load balancing, e̶r̶r̶o̶r̶ h̶a̶n̶d̶l̶i̶n̶g̶, p̶i̶n̶g̶/̶p̶o̶n̶g̶, s̶t̶a̶t̶u̶s̶ u̶p̶d̶a̶t̶e̶, program updates, shutdown/restart.

#Client Class indeholder:
"""  O = first edition done  X = need further details before implementation  ? = unsure if needed
- __init__             O            improviser i guess
- publish/subscribe design pattern  se https://github.com/python-websockets/websockets/blob/main/experiments/broadcast/server.py eller https://github.com/python-websockets/websockets/issues/124 4.kommentar
- get_IoT              ?            Link ubrugeligt 
- get_IoT_ip_address   X            se https://websockets.readthedocs.io/en/stable/faq/server.html ctrl+f ip ad
- set_wifi_credentials ?            se https://github.com/search?q=repo%3Ahome-assistant-libs/python-matter-server%20set_wifi_credentials&type=code bøvlet = nødvendigt?
- ping/pong_IoT        O            se https://github.com/alpapago/brushbuddy/blob/57aca96a7a1189337a5d738a21c2998f6fd2a694/IoT/client.py#L2
- logging/diagnostics/error_messages    se https://github.com/iotile/coretools/blob/642f5fefa6018c3e0c8004c90adccec6edb17702/transport_plugins/websocket/iotile_transport_websocket/websocket_implementation.py#L4 ellers https://websockets.readthedocs.io/en/stable/howto/cheatsheet.html
- remove_IoT           ?            bare delete?
- send_message         O            se https://blog.stackademic.com/websockets-in-python-e8f845d52640
- send_command         X            det samme som ^^^^^^ ?
- handle_event         ?            se https://websockets.readthedocs.io/en/stable/intro/tutorial1.html  Minder meget om process(data) = nødvendigt?
- connect              O            se https://websockets.readthedocs.io/en/stable/faq/client.html
- start_listening      O            se https://community.tempest.earth/t/basic-python-websockets-example-to-retrieve-current-tempest-data/9310/2 basically bare .recv()
- disconnect           O            se https://websockets.readthedocs.io/en/stable/faq/client.html
- parse_data           X            se https://pypi.org/project/RPi.GPIO/ pga. https://dataheadhunters.com/academy/how-to-use-python-for-iot-projects-detailed-steps/ ref
"""