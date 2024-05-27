import logging
from ffmpeg_manager import FFmpegManager
from video_processing import VideoProcessor

class DistributionManager:
    def __init__(self):
        self.ffmpeg_manager = FFmpegManager()
        self.external_devices = {}
        self.tasks = {}
        logging.basicConfig(level=logging.INFO)

    def add_client(self, client_id, address):
        try:
            self.external_devices[client_id] = address
            logging.info(f"Client {client_id} added with address {address}")
        except Exception as e:
            logging.error(f"Failed to add client {client_id}: {e}")
            raise

    def remove_client(self, client_id):
        try:
            if client_id in self.external_devices:
                del self.external_devices[client_id]
                logging.info(f"Client {client_id} removed")
            else:
                logging.warning(f"Client {client_id} does not exist")
        except Exception as e:
            logging.error(f"Failed to remove client {client_id}: {e}")
            raise

    def list_clients(self):
        return list(self.external_devices.keys())

    def start_task(self, task_id, task_type):
        try:
            if task_type == 'video_local':
                self.ffmpeg_manager.start_stream(task_id)
                video_processor = VideoProcessor()
                logging.info(f"Starting video local task {task_id}")
                try:
                    for frame in self.ffmpeg_manager.read_frames(task_id):
                        if not video_processor.process_frame(frame):
                            break
                finally:
                    self.ffmpeg_manager.stop_stream(task_id)
                video_processor.process_video(task_id)
                self.tasks[task_id] = {
                    'type': task_type,
                    'processor': video_processor
                }
            logging.info(f"Task {task_id} started")
        except Exception as e:
            logging.error(f"Failed to start task {task_id}: {e}")
            raise

    def stop_task(self, task_id):
        try:
            if task_id in self.tasks:
                task_info = self.tasks[task_id]
                task_type = task_info['type']
                if task_type == 'video_local':
                    self.ffmpeg_manager.stop_stream(task_id)
                del self.tasks[task_id]
                logging.info(f"Stopped task {task_id}")
            else:
                logging.warning(f"Task {task_id} does not exist")
        except Exception as e:
            logging.error(f"Failed to stop task {task_id}: {e}")
            raise

    def update_task_settings(self, task_id, settings):
        try:
            if task_id in self.tasks:
                # Implement settings update logic
                logging.info(f"Updated settings for task {task_id} with settings {settings}")
            else:
                logging.warning(f"Task {task_id} does not exist")
        except Exception as e:
            logging.error(f"Failed to update settings for task {task_id}: {e}")
            raise
