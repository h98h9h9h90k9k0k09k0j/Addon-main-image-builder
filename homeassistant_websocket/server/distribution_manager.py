from ffmpeg_manager import FFmpegManager
from external_device_manager import ExternalDeviceManager

class DistributionManager:
    def __init__(self):
        self.ffmpeg_manager = FFmpegManager()
        self.external_devices = {}
        self.tasks = {}

    def add_client(self, client_id, address):
        self.external_devices[client_id] = ExternalDeviceManager(address)

    def remove_client(self, client_id):
        if client_id in self.external_devices:
            del self.external_devices[client_id]

    def list_clients(self):
        return list(self.external_devices.keys())

    def start_task(self, task_id, task_type, input_url, client_id):
        if task_type == 'video_stream':
            self.ffmpeg_manager.start_stream(task_id, input_url)
            if client_id in self.external_devices:
                self.tasks[task_id] = {
                    'type': task_type,
                    'client_id': client_id
                }
                self.external_devices[client_id].stream_video(task_id, self.ffmpeg_manager)
        else:
            if client_id in self.external_devices:
                self.tasks[task_id] = {
                    'type': task_type,
                    'client_id': client_id
                }
                self.external_devices[client_id].send_task(task_id, task_type, input_url)  # Assuming input_url is used as payload

    def stop_task(self, task_id):
        if task_id in self.tasks:
            task_type = self.tasks[task_id]['type']
            if task_type == 'video_stream':
                self.ffmpeg_manager.stop_stream(task_id)
            del self.tasks[task_id]

    def update_task_settings(self, task_id, settings):
        # Implement settings update logic
        pass
