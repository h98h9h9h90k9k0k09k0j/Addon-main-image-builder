import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify
from frontend_manager import FrontendManager

class TestFrontendManager(unittest.TestCase):
    def setUp(self):
        self.distribution_manager = MagicMock()
        self.app = FrontendManager(self.distribution_manager).app
        self.client = self.app.test_client()

    def test_start_stream(self):
        response = self.client.post('/start_stream', json={'task_id': 'task1', 'client_id': 'client1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Stream started'})
        self.distribution_manager.start_task.assert_called_once_with('task1', 'video_stream', 'client1')

    def test_start_stream_key_error(self):
        response = self.client.post('/start_stream', json={'client_id': 'client1'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertIn('Missing key', response.json['error'])

    def test_stop_stream(self):
        response = self.client.post('/stop_stream', json={'task_id': 'task1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Stream stopped'})
        self.distribution_manager.stop_task.assert_called_once_with('task1')

    def test_stop_stream_key_error(self):
        response = self.client.post('/stop_stream', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertIn('Missing key', response.json['error'])

    def test_update_settings(self):
        response = self.client.post('/update_settings', json={'task_id': 'task1', 'settings': {'setting1': 'value1'}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Settings updated'})
        self.distribution_manager.update_task_settings.assert_called_once_with('task_id', {'setting1': 'value1'})

    def test_update_settings_key_error(self):
        response = self.client.post('/update_settings', json={'task_id': 'task1'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertIn('Missing key', response.json['error'])

    def test_add_client(self):
        response = self.client.post('/add_client', json={'client_id': 'client1', 'address': 'localhost:50051'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Client added'})
        self.distribution_manager.add_client.assert_called_once_with('client1', 'localhost:50051')

    def test_add_client_key_error(self):
        response = self.client.post('/add_client', json={'client_id': 'client1'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertIn('Missing key', response.json['error'])

    def test_remove_client(self):
        response = self.client.post('/remove_client', json={'client_id': 'client1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Client removed'})
        self.distribution_manager.remove_client.assert_called_once_with('client1')

    def test_remove_client_key_error(self):
        response = self.client.post('/remove_client', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertIn('Missing key', response.json['error'])

    def test_list_clients(self):
        self.distribution_manager.list_clients.return_value = ['client1', 'client2']
        response = self.client.get('/list_clients')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'clients': ['client1', 'client2']})
        self.distribution_manager.list_clients.assert_called_once()

if __name__ == '__main__':
    unittest.main()
