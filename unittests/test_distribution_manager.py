import unittest
from unittest.mock import patch, MagicMock
from server.distribution_manager import DistributionManager

class TestDistributionManager(unittest.TestCase):

    def setUp(self):
        self.manager = DistributionManager()

    @patch('distribution_manager.ExternalDeviceManager')
    def test_add_client(self, mock_external_device_manager):
        self.manager.add_client('client1', 'localhost:50051')
        self.assertIn('client1', self.manager.external_devices)
        mock_external_device_manager.assert_called_once_with('localhost:50051')

    def test_remove_client(self):
        self.manager.external_devices = {'client1': MagicMock()}
        self.manager.remove_client('client1')
        self.assertNotIn('client1', self.manager.external_devices)

    def test_list_clients(self):
        self.manager.external_devices = {'client1': MagicMock(), 'client2': MagicMock()}
        clients = self.manager.list_clients()
        self.assertEqual(clients, ['client1', 'client2'])

    @patch('distribution_manager.FFmpegManager')
    @patch('distribution_manager.ExternalDeviceManager')
    def test_start_video_stream_task(self, mock_external_device_manager, mock_ffmpeg_manager):
        mock_device = MagicMock()
        mock_external_device_manager.return_value = mock_device
        self.manager.external_devices['client1'] = mock_device

        self.manager.start_task('task1', 'video_stream', 'client1')
        self.assertIn('task1', self.manager.tasks)
        mock_ffmpeg_manager().start_stream.assert_called_once_with('task1')
        mock_device.stream_video.assert_called_once_with('task1', mock_ffmpeg_manager())

    @patch('distribution_manager.FFmpegManager')
    @patch('distribution_manager.ExternalDeviceManager')
    def test_start_non_video_stream_task(self, mock_external_device_manager, mock_ffmpeg_manager):
        mock_device = MagicMock()
        mock_external_device_manager.return_value = mock_device
        self.manager.external_devices['client1'] = mock_device

        self.manager.start_task('task1', 'other_task', 'client1')
        self.assertIn('task1', self.manager.tasks)
        mock_device.send_task.assert_called_once_with('task1', 'other_task')

    @patch('distribution_manager.FFmpegManager')
    def test_stop_task(self, mock_ffmpeg_manager):
        self.manager.tasks = {'task1': {'type': 'video_stream', 'client_id': 'client1'}}
        self.manager.stop_task('task1')
        self.assertNotIn('task1', self.manager.tasks)
        mock_ffmpeg_manager().stop_stream.assert_called_once_with('task1')

    def test_update_task_settings(self):
        self.manager.tasks = {'task1': {'type': 'video_stream', 'client_id': 'client1'}}
        settings = {'setting1': 'value1'}
        with self.assertLogs(level='INFO') as log:
            self.manager.update_task_settings('task1', settings)
            self.assertIn('Updated settings for task task1 with settings', log.output[0])

if __name__ == '__main__':
    unittest.main()
