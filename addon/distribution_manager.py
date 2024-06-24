import logging
import uuid
from ffmpeg_manager import FFmpegManager
from external_device_manager import ExternalDeviceManager

class DistributionManager:
    def __init__(self):
        self.ffmpeg_manager = FFmpegManager()
        self.external_devices = {}
        self.tasks = {}
        self.alerts = []

    def add_client(self, client_id, address):
        try:
            self.external_devices[client_id] = ExternalDeviceManager(address)
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

    def start_task(self, task_type, client_id):
        if client_id not in self.external_devices:
            logging.error(f"Invalid client ID: {client_id}")
            return
        task_id = str(uuid.uuid4())
        try:
            if task_type == 'video_stream':
                self.ffmpeg_manager.start_stream(task_id)
                if client_id in self.external_devices:
                    self.tasks[task_id] = {
                        'type': task_type,
                        'client_id': client_id
                    }
                    logging.info(f"Started video stream task {task_id} for client {client_id}")
                    self.external_devices[client_id].stream_video(task_id, self.ffmpeg_manager)
            else:
                if client_id in self.external_devices:
                    self.tasks[task_id] = {
                        'type': task_type,
                        'client_id': client_id
                    }
                    self.external_devices[client_id].send_task(task_id, task_type)
                    logging.info(f"Started task {task_id} of type {task_type} for client {client_id}")
            return task_id
        except Exception as e:
            logging.error(f"Failed to start task {task_id}: {e}")
            raise

    def stop_task(self, task_id):
        if task_id not in self.tasks:
            logging.warning(f"Task {task_id} does not exist")
            return
        try:
            if task_id in self.tasks:
                task_type = self.tasks[task_id]['type']
                if task_type == 'video_stream':
                    self.ffmpeg_manager.stop_stream(task_id)
                #del self.tasks[task_id]
                logging.info(f"Stopped task {task_id}")
            else:
                logging.warning(f"Task {task_id} does not exist")
        except Exception as e:
            logging.error(f"Failed to stop task {task_id}: {e}")
            raise

    def update_task_settings(self, task_id, settings):
        try:
            if task_id in self.tasks:
                client_id = self.tasks[task_id]['client_id']
                if 'processing_type' in settings and client_id in self.external_devices:
                    self.external_devices[client_id].update_processing_type(settings['processing_type'])
                logging.info(f"Updated settings for task {task_id} with settings {settings}")
            else:
                logging.warning(f"Task {task_id} does not exist")
        except Exception as e:
            logging.error(f"Failed to update settings for task {task_id}: {e}")
            raise

    def add_alert(self, alert):
        try:
            self.alerts.append(alert)
            logging.info(f"New alert added: {alert}")
        except Exception as e:
            logging.error(f"Failed to add alert: {e}")
            raise

    def get_alerts(self):
        try:
            return self.alerts
        except Exception as e:
            logging.error(f"Failed to get alerts: {e}")
            raise

    def clear_alerts(self):
        try:
            self.alerts.clear()
            logging.info("All alerts cleared")
        except Exception as e:
            logging.error(f"Failed to clear alerts: {e}")
            raise

    def retrieve_saved_frames(self, client_id):
        try:
            if client_id in self.external_devices:
                return self.external_devices[client_id].retrieve_frames()
            else:
                logging.error(f"Client {client_id} does not exist")
                return None
        except Exception as e:
            logging.error(f"Failed to retrieve saved frames for client {client_id}: {e}")
            raise
