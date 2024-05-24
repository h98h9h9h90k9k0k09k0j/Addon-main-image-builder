import subprocess
import unittest
from unittest.mock import patch, MagicMock
from server.ffmpeg_manager import FFmpegManager

class TestFFmpegManager(unittest.TestCase):

    @patch('subprocess.Popen')
    def test_start_stream(self, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        manager = FFmpegManager()
        manager.start_stream('test_stream')

        self.assertIn('test_stream', manager.processes)
        mock_popen.assert_called_once_with([
            'ffmpeg', '-i', '/dev/video0', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-qscale:v', '2', 'pipe:1'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
        mock_process.poll.assert_called_once()

    @patch('subprocess.Popen')
    def test_stop_stream(self, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        manager = FFmpegManager()
        manager.start_stream('test_stream')
        manager.stop_stream('test_stream')

        self.assertNotIn('test_stream', manager.processes)
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()

    @patch('subprocess.Popen')
    def test_get_stream_output(self, mock_popen):
        mock_process = MagicMock()
        mock_process.stdout.read.return_value = b'test_data'
        mock_popen.return_value = mock_process

        manager = FFmpegManager()
        manager.start_stream('test_stream')
        output = manager.get_stream_output('test_stream')

        self.assertEqual(output, b'test_data')
        mock_process.stdout.read.assert_called_once_with(1024 * 1024)

    def test_stop_nonexistent_stream(self):
        manager = FFmpegManager()
        with self.assertLogs(level='ERROR') as log:
            manager.stop_stream('nonexistent_stream')
            self.assertIn('Stream nonexistent_stream does not exist', log.output[0])

    def test_get_stream_output_nonexistent_stream(self):
        manager = FFmpegManager()
        with self.assertLogs(level='ERROR') as log:
            output = manager.get_stream_output('nonexistent_stream')
            self.assertIsNone(output)
            self.assertIn('Stream nonexistent_stream does not exist', log.output[0])

if __name__ == '__main__':
    unittest.main()
