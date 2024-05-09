# Capture the video stream directly from the camera or through homeassistant api
# Will send video to client for processing

import base64
import json
from concurrent.futures import ThreadPoolExecutor
import logging
import cv2
import asyncio

    
capture_task = None
frame_rate = 20
resolution = (640, 480)
cap = None

class VideoHandler:
    @staticmethod
    async def capture_video(websocket):
        # Open the video device
        global cap
        cap = cv2.VideoCapture('/dev/video0')
        if not cap.isOpened():
            logging.error("Error: Camera could not be accessed.")
            return
        if capture_task is not None and not capture_task.done():
            logging.info("Video capture is already running")
            return
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            global capture_task
            capture_task = asyncio.ensure_future(asyncio.get_event_loop().run_in_executor(executor, read_frames))
            await capture_task
        except Exception as e:
            logging.error(f"Error in capture_video: {e}")
        finally:
            if cap is not None:
                cap.release()
                cv2.destroyAllWindows()
            if capture_task is not None and not capture_task.done():
                capture_task.cancel()
                try:
                    await capture_task
                except asyncio.CancelledError:
                    logging.info("Video capture task was cancelled")
            executor.shutdown(wait=True)

        @staticmethod
        async def read_frames():
                running = True
                while running:
                    ret, frame = cap.read()
                    if not ret:
                        logging.error("Error: Can't receive frame.")
                        running = False
                    else:
                        await VideoHandler.send_video_data(frame, websocket)

    # Stop the video capture
    @staticmethod
    async def stop_video_capture():
        if capture_task is not None and not capture_task.done():
            capture_task.cancel()
            try:
                await capture_task
            except asyncio.CancelledError:
                logging.info("Video capture task was cancelled")
        else:
            logging.info("Video capture task is not running")

    # set the frame rate for the video capture
    @staticmethod
    async def set_frame_rate(fps):
        global frame_rate
        frame_rate = fps
        cap.set(cv2.CAP_PROP_FPS, fps)

    # set the resolution for the video capture
    @staticmethod
    async def set_resolution(res):
        global resolution
        resolution = res
        width, height = res.split('x')
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))

    # Encode video data if needed (e.g., base64 encoding for binary data)
    @staticmethod
    async def encode_video_data(video_data):
        return base64.b64encode(video_data.encode()).decode('utf-8')
    
    @staticmethod
    async def send_video_data(frame, websocket):
        response = {"type": "video_frame", "data": frame}
        await websocket.send(json.dumps(response))
        print(f"Sent frame to {websocket.remote_address}")
