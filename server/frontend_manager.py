from flask import Flask, request, jsonify
from google.protobuf.json_format import MessageToDict

class FrontendManager:
    def __init__(self, distribution_manager):
        self.app = Flask(__name__)
        self.distribution_manager = distribution_manager
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/start_stream', methods=['POST'])
        def start_stream():
            data = request.get_json()
            task_id = data['task_id']
            client_id = data['client_id']
            self.distribution_manager.start_task(task_id, 'video_stream', client_id)
            return jsonify({'message': 'Stream started'}), 200

        @self.app.route('/stop_stream', methods=['POST'])
        def stop_stream():
            data = request.get_json()
            task_id = data['task_id']
            self.distribution_manager.stop_task(task_id)
            return jsonify({'message': 'Stream stopped'}), 200

        @self.app.route('/update_settings', methods=['POST'])
        def update_settings():
            data = request.get_json()
            task_id = data['task_id']
            settings = data['settings']
            self.distribution_manager.update_task_settings(task_id, settings)
            return jsonify({'message': 'Settings updated'}), 200

        @self.app.route('/add_client', methods=['POST'])
        def add_client():
            data = request.get_json()
            client_id = data['client_id']
            address = data['address']
            self.distribution_manager.add_client(client_id, address)
            return jsonify({'message': 'Client added'}), 200

        @self.app.route('/remove_client', methods=['POST'])
        def remove_client():
            data = request.get_json()
            client_id = data['client_id']
            self.distribution_manager.remove_client(client_id)
            return jsonify({'message': 'Client removed'}), 200

        @self.app.route('/list_clients', methods=['GET'])
        def list_clients():
            clients = self.distribution_manager.list_clients()
            return jsonify({'clients': clients}), 200

    def run(self):
        self.app.run(host='0.0.0.0', port=5000)
