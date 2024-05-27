from flask import Flask, request, jsonify
import logging

class FrontendManager:
    def __init__(self, distribution_manager):
        self.app = Flask(__name__)
        self.distribution_manager = distribution_manager
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/start_stream', methods=['POST'])
        def start_stream():
            try:
                data = request.get_json()
                task_id = data['task_id']
                #processing_mode = data['process']
                self.distribution_manager.start_task(task_id, 'video_local')
                return jsonify({'message': 'Stream started'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/stop_stream', methods=['POST'])
        def stop_stream():
            try:
                data = request.get_json()
                task_id = data['task_id']
                self.distribution_manager.stop_task(task_id)
                return jsonify({'message': 'Stream stopped'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/update_settings', methods=['POST'])
        def update_settings():
            try:
                data = request.get_json()
                task_id = data['task_id']
                settings = data['settings']
                self.distribution_manager.update_task_settings(task_id, settings)
                return jsonify({'message': 'Settings updated'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/add_client', methods=['POST'])
        def add_client():
            try:
                data = request.get_json()
                client_id = data['client_id']
                address = data['address']
                self.distribution_manager.add_client(client_id, address)
                return jsonify({'message': 'Client added'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/remove_client', methods=['POST'])
        def remove_client():
            try:
                data = request.get_json()
                client_id = data['client_id']
                self.distribution_manager.remove_client(client_id)
                return jsonify({'message': 'Client removed'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/list_clients', methods=['GET'])
        def list_clients():
            try:
                clients = self.distribution_manager.list_clients()
                return jsonify({'clients': clients}), 200
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

    def run(self):
        self.app.run(host='0.0.0.0', port=5000)
