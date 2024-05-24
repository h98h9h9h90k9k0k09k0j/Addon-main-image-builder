import grpc
import workloads_pb2
import workloads_pb2_grpc

class ExternalDeviceManager:
    def __init__(self, address):
        self.address = address
        self.channel = grpc.insecure_channel(address)
        self.video_stub = workloads_pb2_grpc.VideoStreamerStub(self.channel)
        self.task_stub = workloads_pb2_grpc.TaskManagerStub(self.channel)

    def stream_video(self, task_id, processing_type, ffmpeg_manager):
        def generate_video_chunks():
            first_chunk = workloads_pb2.VideoChunk(processing_type=processing_type)
            yield first_chunk
            while True:
                chunk = ffmpeg_manager.get_stream_output(task_id)
                if not chunk:
                    break
                yield workloads_pb2.VideoChunk(data=chunk)

        response_iterator = self.video_stub.StreamVideo(generate_video_chunks())
        for response in response_iterator:
            print(f"Response from server: {response.message}")
        return response

    def send_task(self, task_id, task_type, payload):
        request = workloads_pb2.TaskRequest(task_id=task_id, task_type=task_type, payload=payload)
        response = self.task_stub.SendTask(request)
        return response

    def stream_task(self, task_id, data_chunks):
        def generate_task_chunks():
            for chunk in data_chunks:
                yield workloads_pb2.TaskChunk(data=chunk, task_id=task_id)
        response = self.task_stub.StreamTask(generate_task_chunks())
        return response
