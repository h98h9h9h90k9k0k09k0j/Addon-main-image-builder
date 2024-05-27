import subprocess
import logging

class FFmpegManager:
    def __init__(self):
        #self.processes = {}
        self.process = None

    def start_stream(self, input_device='/dev/video0'):
        try:
            command = [
                'ffmpeg',
                '-i', input_device,
                '-f', 'image2pipe',
                '-vcodec', 'mjpeg',
                '-qscale:v', '2',
                'pipe:1'
            ]
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
            logging.info(f"Started stream with input device {input_device}")
        except Exception as e:
            logging.error(f"Failed to start stream: {e}")
            raise

    def stop_stream(self):
        try:
            self.process.terminate()
            self.process.wait()
            self.process = None
            logging.info(f"Stopped stream ")
        except Exception as e:
            logging.error(f"Failed to stop stream : {e}")
            raise

    def read_frames(self):
        try:
            buffer = b""
            while True:
                chunk = self.process.stdout.read(1024 * 1024)
                if not chunk:
                    break
                buffer += chunk
                start = 0
                while True:
                    start = buffer.find(b'\xff\xd8', start)
                    end = buffer.find(b'\xff\xd9', start)
                    if start != -1 and end != -1:
                        jpg = buffer[start:end+2]
                        buffer = buffer[end+2:]
                        yield jpg
                    else:
                        break
        except Exception as e:
            logging.error(f"Failed to read frames for stream: {e}")
            raise



'''
'-vcodec', 'mjpeg',
            '-qscale:v', '2',
            def start_stream(self, stream_id, input_device = '/dev/video0', codec='libx264', additional_flags=None):
        ffmpeg_base_cmd = [
            'ffmpeg',
            '-f', 'v4l2',       # Input format: Video4Linux2 for USB cameras
            '-i', input_device,  # Input device
            '-c:v', codec,       # Video codec
            '-f', 'image2pipe',    # Output format: raw video
            'pipe:1'             # Output to stdout
        ]
        if additional_flags:
            ffmpeg_base_cmd.extend(additional_flags)

        self.ffmpeg_cmd = ffmpeg_base_cmd
        print(f"Starting FFmpeg with command: {' '.join(self.ffmpeg_cmd)}")
        process = subprocess.Popen(self.ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
        self.processes[stream_id] = process


class FFmpegManager:
    def __init__(self):
        self.process = None
        self.ffmpeg_cmd = None

    def start_ffmpeg(self, input_device, output_url, codec='libx264', protocol='rtsp', additional_flags=None):
        if self.process and self.process.poll() is None:
            print("FFmpeg is already running")
            return

        ffmpeg_base_cmd = [
            'ffmpeg',
            '-f', 'v4l2',       # Input format: Video4Linux2 for USB cameras
            '-i', input_device,  # Input device
            '-c:v', codec,       # Video codec
        ]

        if additional_flags:
            ffmpeg_base_cmd.extend(additional_flags)

        ffmpeg_output_cmd = [
            '-f', protocol,      # Output protocol
            output_url           # Output URL
        ]

        self.ffmpeg_cmd = ffmpeg_base_cmd + ffmpeg_output_cmd
        print(f"Starting FFmpeg with command: {' '.join(self.ffmpeg_cmd)}")
        self.process = subprocess.Popen(self.ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop_ffmpeg(self):
        if self.process and self.process.poll() is None:
            print("Stopping FFmpeg")
            self.process.terminate()
            self.process.wait()
        else:
            print("FFmpeg is not running")

    def restart_ffmpeg(self, input_device, output_url, codec='libx264', protocol='rtsp', additional_flags=None):
        self.stop_ffmpeg()
        self.start_ffmpeg(input_device, output_url, codec, protocol, additional_flags)

    def is_running(self):
        return self.process is not None and self.process.poll() is None
'''

'''
# Usage example:
ffmpeg_manager = FFmpegManager()

# Start FFmpeg with initial configuration
ffmpeg_manager.start_ffmpeg('/dev/video0', 'rtsp://localhost:8554/stream')

# Dynamically change configuration
new_codec = 'libx265'
new_protocol = 'rtmp'
ffmpeg_manager.restart_ffmpeg('/dev/video0', 'rtmp://localhost/live/stream', codec=new_codec, protocol=new_protocol)
'''