import subprocess
import os
import signal
import psutil
import yaml

class MediaMTXManager:
    def __init__(self, mediamtx_path, config_path):
        self.mediamtx_path = mediamtx_path
        self.config_path = config_path
        self.process = None

    def start_server(self):
        if not self.is_server_running():
            self.process = subprocess.Popen([self.mediamtx_path, self.config_path])
            print(f"Server started with PID: {self.process.pid}")
        else:
            print("Server is already running")

    def stop_server(self):
        if self.is_server_running():
            self.process.terminate()
            self.process.wait()
            print("Server stopped")
        else:
            print("Server is not running")

    def restart_server(self):
        self.stop_server()
        self.start_server()

    def is_server_running(self):
        if self.process is None:
            return False
        return self.process.poll() is None

    def forward_port(self, internal_port, external_port):
        command = f"iptables -t nat -A PREROUTING -p tcp --dport {external_port} -j REDIRECT --to-port {internal_port}"
        os.system(command)
        print(f"Port {external_port} forwarded to {internal_port}")

    def remove_port_forwarding(self, external_port):
        command = f"iptables -t nat -D PREROUTING -p tcp --dport {external_port} -j REDIRECT"
        os.system(command)
        print(f"Port forwarding for {external_port} removed")

    def update_config(self, new_config):
        with open(self.config_path, 'w') as config_file:
            yaml.dump(new_config, config_file)
        print("Configuration updated")

    def reload_config(self):
        if self.is_server_running():
            self.process.send_signal(signal.SIGHUP)
            print("Configuration reloaded")

    def get_server_status(self):
        if self.is_server_running():
            return f"Server is running with PID: {self.process.pid}"
        return "Server is not running"

# Usage example:
mediamtx_manager = MediaMTXManager('/path/to/mediamtx', '/path/to/config.yml')

# Start the server
mediamtx_manager.start_server()

# Get server status
status = mediamtx_manager.get_server_status()
print(status)

# Update configuration
new_config = {
    'rtsp': {
        'port': 8554
    },
    'paths': {
        'all': {
            'readUser': 'user',
            'readPass': 'pass'
        }
    }
}
mediamtx_manager.update_config(new_config)

# Reload configuration
mediamtx_manager.reload_config()

# Forward port
mediamtx_manager.forward_port(8554, 8555)

# Remove port forwarding
mediamtx_manager.remove_port_forwarding(8555)

# Stop the server
mediamtx_manager.stop_server()
