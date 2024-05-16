# Capture the video stream directly from the camera or through homeassistant api
# Will send video to client for processing

import base64
import json
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import asyncio

    


class VideoHandler:
    capture_task = None
    frame_rate = 30
    resolution = "640x480"
    cap = None
    
    @staticmethod
    async def capture_video(websocket):
        try:
            VideoHandler.cap = VideoHandler.open_camera()
            if VideoHandler.cap is None or not VideoHandler.cap.isOpened():
                logging.error("Error: Camera could not be accessed.")
                return
            if VideoHandler.capture_task is not None and not VideoHandler.capture_task.done():
                logging.info("Video capture is already running")
                return
            executor = ThreadPoolExecutor(max_workers=1)
            VideoHandler.capture_task = asyncio.ensure_future(
                asyncio.get_event_loop().run_in_executor(executor, VideoHandler.read_frames, websocket))
            await VideoHandler.capture_task
        except Exception as e:
            logging.error(f"Error in capture_video: {e}")
        finally:
            if VideoHandler.cap is not None:
                VideoHandler.cap.release()
            if VideoHandler.capture_task is not None and not VideoHandler.capture_task.done():
                VideoHandler.capture_task.cancel()
                try:
                    await VideoHandler.capture_task
                except asyncio.CancelledError:
                    logging.info("Video capture task was cancelled")
            executor.shutdown(wait=True)


    @staticmethod
    def open_camera():
        # Attempt to open video devices from /dev/video0 to /dev/video31
        for i in range(32):
            try:
                device_path = f"/dev/video{i}"
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    logging.info(f"Successfully opened {device_path}")
                    # Initialization delay to allow the camera to warm up
                    time.sleep(5)  # Delay for 5 seconds
                    return cap
                cap.release()
            except Exception as e:
                logging.error(f"Error trying to open {device_path}: {e}")
        logging.error("No available video devices could be opened.")
        return None

    @staticmethod
    def read_frames(websocket):
        running = True
        while running:
            ret, frame = VideoHandler.cap.read()
            if not ret:
                logging.error("Error: Can't receive frame.")
                running = False
            else:
                # Assuming send_video_data is an async method that handles sending frame data
                asyncio.run_coroutine_threadsafe(VideoHandler.send_video_data(frame, websocket), asyncio.get_event_loop())

    # Stop the video capture
    @staticmethod
    async def stop_video_capture():
        if VideoHandler.capture_task is not None and not VideoHandler.capture_task.done():
            VideoHandler.capture_task.cancel()
            try:
                await VideoHandler.capture_task
            except asyncio.CancelledError:
                logging.info("Video capture task was cancelled")
        else:
            logging.info("Video capture task is not running")

    # set the frame rate for the video capture
    @staticmethod
    async def set_frame_rate(fps):    
        frame_rate = fps
        VideoHandler.cap.set(cv2.CAP_PROP_FPS, fps)

    # set the resolution for the video capture
    @staticmethod
    async def set_resolution(res):
        resolution = res
        width, height = res.split('x')
        VideoHandler.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        VideoHandler.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))

    # Encode video data if needed (e.g., base64 encoding for binary data)
    @staticmethod
    async def encode_video_data(video_data):
        return base64.b64encode(video_data.encode()).decode('utf-8')
    
    @staticmethod
    async def send_video_data(frame, websocket):
        response = {"type": "video_frame", "data": frame}
        await websocket.send(json.dumps(response))
        print(f"Sent frame to {websocket.remote_address}")
