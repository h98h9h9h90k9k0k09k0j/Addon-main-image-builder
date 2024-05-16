import subprocess
import signal
import time

class GStreamerPipeline:
    def __init__(self):
        self.process = None

    async def start_pipeline(self):
        try:
            # Start the GStreamer pipeline using subprocess
            self.process = subprocess.Popen(
                ['gst-launch-1.0', 'v4l2src', 'device=/dev/video0', '!', 'image/jpeg,framerate=30/1', '!', 
                 'jpegdec', '!', 'videoconvert', '!', 'video/x-raw,format=I420', '!', 'v4l2h264enc', '!', 'rtph264pay', 'config-interval=1', '!', 
                 'gdppay', '!', 'tcpserversink', 'host=0.0.0.0', 'port=8080'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("GStreamer pipeline started")
        except Exception as e:
            print(f"Failed to start GStreamer pipeline: {e}")

    async def stop_pipeline(self):
        if self.process:
            try:
                # Send SIGINT to the process to terminate it gracefully
                self.process.send_signal(signal.SIGINT)
                self.process.wait()  # Wait for the process to terminate
                print("GStreamer pipeline stopped")
            except Exception as e:
                print(f"Failed to stop GStreamer pipeline: {e}")

    async def restart_pipeline(self):
        self.stop_pipeline()
        self.start_pipeline()



