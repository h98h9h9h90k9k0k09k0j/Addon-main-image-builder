import unittest
from unittest.mock import patch, MagicMock, call
import grpc
from server.external_device_manager import ExternalDeviceManager
import workloads_pb2

class TestExternalDeviceManager(unittest.TestCase):

    @patch('workloads_pb2_grpc.VideoStreamerStub')
    @patch('workloads_pb2_grpc.TaskManagerStub')
    @patch('grpc.insecure_channel')
    def setUp(self, mock_channel, mock_video_stub, mock_task_stub):
        self.mock_channel = mock_channel
        self.mock_video_stub = mock_video_stub
        self.mock_task_stub = mock_task_stub
        self.manager = ExternalDeviceManager('localhost:50051')

    @patch('workloads_pb2_grpc.VideoStreamerStub.StreamVideo')
    @patch('workloads_pb2_grpc.VideoStreamerStub.StreamVideo.return_value')
    @patch('external_device_manager.ExternalDeviceManager.stream_video')
    def test_stream_video(self, mock_stream_video, mock_stream_video_return, mock_stream_video_method):
        ffmpeg_manager = MagicMock()
        ffmpeg_manager.get_stream_output.return_value = b'fake_chunk'
        
        self.manager.stream_video('test_task_id', ffmpeg_manager)
        
        calls = [
            call().StreamVideo().__next__(),
            call().StreamVideo().__iter__(),
        ]
        self.mock_video_stub.assert_has_calls(calls)
        mock_stream_video_method.assert_called_with('test_task_id', ffmpeg_manager)
        ffmpeg_manager.get_stream_output.assert_called_with('test_task_id')

    @patch('workloads_pb2_grpc.TaskManagerStub.SendTask')
    def test_send_task(self, mock_send_task):
        mock_send_task.return_value = 'fake_response'
        
        response = self.manager.send_task('test_task_id', 'test_task_type', b'fake_payload')
        
        self.assertEqual(response, 'fake_response')
        mock_send_task.assert_called_once()
        self.assertEqual(mock_send_task.call_args[0][0].task_id, 'test_task_id')
        self.assertEqual(mock_send_task.call_args[0][0].task_type, 'test_task_type')
        self.assertEqual(mock_send_task.call_args[0][0].payload, b'fake_payload')

    @patch('workloads_pb2_grpc.TaskManagerStub.StreamTask')
    def test_stream_task(self, mock_stream_task):
        mock_stream_task.return_value = 'fake_response'
        data_chunks = [b'chunk1', b'chunk2']
        
        response = self.manager.stream_task('test_task_id', data_chunks)
        
        self.assertEqual(response, 'fake_response')
        mock_stream_task.assert_called_once()
        calls = [
            call().StreamTask().__next__(),
            call().StreamTask().__iter__(),
        ]
        self.mock_task_stub.assert_has_calls(calls)

    @patch('workloads_pb2_grpc.VideoStreamerStub.StreamVideo', side_effect=grpc.RpcError)
    def test_stream_video_grpc_error(self, mock_stream_video):
        ffmpeg_manager = MagicMock()
        with self.assertRaises(grpc.RpcError):
            self.manager.stream_video('test_task_id', ffmpeg_manager)

    @patch('workloads_pb2_grpc.TaskManagerStub.SendTask', side_effect=grpc.RpcError)
    def test_send_task_grpc_error(self, mock_send_task):
        with self.assertRaises(grpc.RpcError):
            self.manager.send_task('test_task_id', 'test_task_type', b'fake_payload')

    @patch('workloads_pb2_grpc.TaskManagerStub.StreamTask', side_effect=grpc.RpcError)
    def test_stream_task_grpc_error(self, mock_stream_task):
        data_chunks = [b'chunk1', b'chunk2']
        with self.assertRaises(grpc.RpcError):
            self.manager.stream_task('test_task_id', data_chunks)

if __name__ == '__main__':
    unittest.main()
