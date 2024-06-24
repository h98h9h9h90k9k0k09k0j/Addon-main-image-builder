import logging
import grpc
import workloads_pb2
import workloads_pb2_grpc
from google.protobuf.json_format import MessageToDict

class ExternalDeviceManager:
    logging.basicConfig(level=logging.INFO)
    
    def __init__(self, address):
        self.address = address
        self.channel = None
        self.video_stub = None
        self.task_stub = None
        self.processing_type = "motion_detection"
        self.connect()

    def connect(self):
        try:
            self.channel = grpc.insecure_channel(self.address)
            self.video_stub = workloads_pb2_grpc.VideoStreamerStub(self.channel)
            self.task_stub = workloads_pb2_grpc.TaskManagerStub(self.channel)
            logging.info(f"Connected to gRPC server at {self.address}")
        except Exception as e:
            logging.error(f"Failed to connect to gRPC server: {e}")
            raise

    def reconnect(self):
        logging.info("Reconnecting to gRPC server...")
        self.connect()

    def stream_video(self, task_id, ffmpeg_manager):
        try:
            def generate_video_chunks():
                first_chunk = workloads_pb2.VideoChunk(processing_type=self.processing_type)
                yield first_chunk
                while True:
                    chunk = ffmpeg_manager.get_stream_output(task_id)
                    if not chunk:
                        break
                    yield workloads_pb2.VideoChunk(data=chunk, processing_type=self.processing_type)

            response_iterator = self.video_stub.StreamVideo(generate_video_chunks())
            for response in response_iterator:
                logging.info(f"Response from server: {MessageToDict(response)}")
        except grpc.RpcError as e:
            logging.error(f"gRPC error during video streaming: {e}")
            raise
        except Exception as e:
            logging.error(f"Error during video streaming: {e}")
            raise

    def send_task(self, task_id, task_type, payload=""):
        try:
            request = workloads_pb2.TaskRequest(task_id=task_id, task_type=task_type, payload=payload)
            response = self.task_stub.SendTask(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"gRPC error during sending task: {e}")
            raise
        except Exception as e:
            logging.error(f"Error during sending task: {e}")
            raise

    def retrieve_frames(self):
        logging.info(f"Requesting saved frames from external device at {self.address}")
        try:
            request = workloads_pb2.TaskRequest(task_id="retrieve_frames", task_type="retrieve_frames", payload="")
            response = self.task_stub.RetrieveFrames(request)
            frames = []
            for frame_data in response.frames:
                frames.append({
                    "image": frame_data.image,
                    "timestamp": frame_data.timestamp
                })
            #logging.info(f"Retrieved frames: {frames}")
            return frames
        except grpc.RpcError as e:
            logging.error(f"gRPC error during retrieving frames: {e}")
            raise
        except Exception as e:
            logging.error(f"Error during retrieving frames: {e}")
            raise

    def update_processing_type(self, processing_type):
        logging.info(f"Updating processing type to {processing_type} for external device at {self.address}")
        try:
            self.processing_type = processing_type
            logging.info(f"Successfully updated processing type to {processing_type}")
        except Exception as e:
            logging.error(f"Failed to update processing type: {e}")
            raise