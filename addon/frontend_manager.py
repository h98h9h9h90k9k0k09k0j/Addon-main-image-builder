from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

class FrontendManager:
    def __init__(self, distribution_manager):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self.distribution_manager = distribution_manager
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/start_stream', methods=['POST'])
        def start_stream():
            logging.info("Received request to start stream")
            try:
                data = request.get_json()
                client_id = data['client_id']
                task_id = self.distribution_manager.start_task('video_stream', client_id)
                logging.info(f"Stream started with task_id: {task_id} for client_id: {client_id}")
                return jsonify({'message': 'Stream started', 'task_id': task_id}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/stop_stream', methods=['POST'])
        def stop_stream():
            logging.info("Received request to stop stream")
            try:
                data = request.get_json()
                task_id = data['task_id']
                self.distribution_manager.stop_task(task_id)
                logging.info(f"Stream stopped for task_id: {task_id}")
                return jsonify({'message': 'Stream stopped'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/update_settings', methods=['POST'])
        def update_settings():
            logging.info("Received request to update settings")
            try:
                data = request.get_json()
                task_id = data['task_id']
                settings = data['settings']
                self.distribution_manager.update_task_settings(task_id, settings)
                logging.info(f"Settings updated for task_id: {task_id} with settings: {settings}")
                return jsonify({'message': 'Settings updated'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/add_client', methods=['POST'])
        def add_client():
            logging.info("Received request to add client")
            try:
                data = request.get_json()
                client_id = data['client_id']
                address = data['address']
                self.distribution_manager.add_client(client_id, address)
                logging.info(f"Client added with client_id: {client_id}, address: {address}")
                return jsonify({'message': 'Client added'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/remove_client', methods=['POST'])
        def remove_client():
            logging.info("Received request to remove client")
            try:
                data = request.get_json()
                client_id = data['client_id']
                self.distribution_manager.remove_client(client_id)
                logging.info(f"Client removed with client_id: {client_id}")
                return jsonify({'message': 'Client removed'}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/list_clients', methods=['GET'])
        def list_clients():
            logging.info("Received request to list clients")
            try:
                clients = self.distribution_manager.list_clients()
                logging.info(f"Listing clients: {clients}")
                return jsonify({'clients': clients}), 200
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/alerts', methods=['GET'])
        def get_alerts():
            logging.info("Received request to get alerts")
            try:
                alerts = self.distribution_manager.get_alerts()
                logging.info(f"Retrieved alerts: {alerts}")
                return jsonify({'alerts': alerts}), 200
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/clear_alerts', methods=['POST'])
        def clear_alerts():
            logging.info("Received request to clear alerts")
            try:
                self.distribution_manager.clear_alerts()
                logging.info("All alerts cleared")
                return jsonify({'message': 'Alerts cleared'}), 200
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

        @self.app.route('/retrieve_frames', methods=['POST'])
        def retrieve_frames():
            logging.info("Received request to retrieve frames")
            try:
                data = request.get_json()
                client_id = data['client_id']
                frames = self.distribution_manager.retrieve_saved_frames(client_id)
                framecount = len(frames)
                logging.info(f"Retrieved frames for client_id: {client_id}")
                return jsonify({'frames': framecount}), 200
            except KeyError as e:
                logging.error(f"KeyError: {e}")
                return jsonify({'error': f'Missing key: {e}'}), 400
            except Exception as e:
                logging.error(f"Exception: {e}")
                return jsonify({'error': 'Internal Server Error'}), 500

    def run(self):
        self.app.run(host='0.0.0.0', port=5000)
