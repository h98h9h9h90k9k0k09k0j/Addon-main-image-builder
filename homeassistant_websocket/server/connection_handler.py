import asyncio
import json
from .video_capture import VideoHandler
import cv2
from concurrent.futures import ThreadPoolExecutor
import logging

# Manages the server connections
# Will handle behaviour between the server, client and frontend


class ConnectionHandler:
    logging.basicConfig(level=logging.INFO)
    
    @staticmethod
    async def register(websocket, clients):
        try:
            await websocket.send(json.dumps({"message": "Connected to server"}))
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                if "client_type" in data:
                    client_type = data["client_type"]
                    if client_type == "frontend":
                        clients[websocket] = {"id": len(clients)+1, "websocket": websocket, "type": "frontend"}
                        await websocket.send(json.dumps({"message": "Registered as frontend client", "id": clients[websocket]["id"]}))
                        break
                    elif client_type == "camera_client":
                        clients[websocket] = {"id": len(clients)+1, "websocket": websocket, "type": "camera_client"}
                        await websocket.send(json.dumps({"message": "Registered as backend client", "id": clients[websocket]["id"]}))
                        break
                    else:
                        await websocket.send(json.dumps({"message": "Invalid client type"}))
            return clients[websocket]["id"]
        except Exception as e:
            logging.error(f"Error in register: {e}")

    @staticmethod
    async def unregister(websocket, clients, client_id):
        try:
            del clients[websocket]
            logging.info(f"Client {client_id} disconnected")
        except Exception as e:
            logging.error(f"Error in unregister: {e}")

    @staticmethod
    async def manage_client(websocket, clients, client_id):
        try:
            if clients[websocket]["type"] == "frontend":
                await ConnectionHandler.frontend_client_handler(websocket, client_id, clients)
            elif clients[websocket]["type"] == "camera_client":
                await ConnectionHandler.camera_client_handler(websocket, client_id, clients)
        except Exception as e:
            logging.error(f"Error in manage_client: {e}")

    @staticmethod
    async def frontend_client_handler(websocket, client_id, clients):
        try:
            async for message in websocket:
                logging.info(f"Received message from {client_id}: {message}")
                if "ping" in message:
                    await websocket.send(json.dumps({"message": "pong"}))
                
                # Show connected clients
                if "show_clients" in message:
                    connected_clients = []
                    for client in clients:
                        connected_clients.append(clients[client]["id"])
                    await websocket.send(json.dumps({"message": "Connected clients", "clients": connected_clients}))

                # Get camera feed from server and send to frontend
                if "get_video_feed" in message:
                    await VideoHandler.stop_video_capture()
                    await VideoHandler.capture_video(websocket)

                # Get performance metrics for the server and clients
                if "get_performance_metrics" in message:
                    # Fecth server performance metrics
                    
                    # Fetch client performance metrics
                    for client in clients:
                        if clients[client]["type"] == "camera_client":
                            await client.send(json.dumps({"message": "get_performance_metrics"}))

                # Get motion or face detection screenshots and timestamps
                if "get_detection_data" in message:
                    for client in clients:
                        if clients[client]["type"] == "camera_client":
                            await client.send(json.dumps({"message": "get_detection_data"}))

                # Set video parameters
                if "set_camera_parameters" in message:
                    # Set video frame rate
                    if "set_frame_rate" in message:
                        frame_rate = message["set_frame_rate"]
                        VideoHandler.set_frame_rate(frame_rate)

                    # Set video resolution
                    if "set_resolution" in message:
                        resolution = message["set_resolution"]
                        VideoHandler.set_resolution(resolution)

                    # Set video processing mode
                    if "set_processing_mode" in message:
                        processing_mode = message["set_processing_mode"]
                        # send message to client to set processing mode
                        for client in clients:
                            if clients[client]["type"] == "camera_client":
                                await client.send(json.dumps({"message": "set_processing_mode", "mode": processing_mode}))

                # Start stream
                if "start_video" in message:
                    for client in clients:
                        if clients[client]["type"] == "camera_client":
                            await client.send(json.dumps({"message": "start_video"}))

                # Stop stream
                if "stop_video" in message:
                    for client in clients:
                        if clients[client]["type"] == "camera_client":
                            await client.send(json.dumps({"message": "stop_video"}))

                # Close all connections
                if "close_clients" in message:
                    for client in clients:
                        await client.send(json.dumps({"message": "close"}))
                        await client.close()
                    
        except Exception as e:
            logging.error(f"Error in frontend_client_handler: {e}")

    @staticmethod
    async def camera_client_handler(websocket, client_id, clients):
        try:
            async for message in websocket:
                logging.info(f"Received message from {client_id}: {message}")
                if "ping" in message:
                    await websocket.send(json.dumps({"message": "pong"}))

                if "start_video" in message:
                    await VideoHandler.capture_video(websocket)

                if "stop_video" in message:
                    await VideoHandler.stop_video_capture()
                
                # Handlle alerts from the camera client
                if "motion_detected" or "face_detected" in message:
                    # alert the frontend client if connected
                    for client in clients:
                        if clients[client]["type"] == "frontend":
                            await client.send(json.dumps({"message": message}))

                # Send detection data to the frontend client
                if "detection_data" in message:
                    for client in clients:
                        if clients[client]["type"] == "frontend":
                            await client.send(json.dumps({"message": message}))

                # Handle camera client performance metrics
                if "performance_metrics" in message:
                    # send performance metrics to the frontend client
                    for client in clients:
                        if clients[client]["type"] == "frontend":
                            await client.send(json.dumps({"message": message}))

        except Exception as e:
            logging.error(f"Error in camera_client_handler: {e}")
