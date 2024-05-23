#!/bin/bash

# Activate the virtual environment
source /opt/venv/bin/activate
echo "activated virtual environment"

# Generate the gRPC code from the protobuf definitions
python -m grpc_tools.protoc -I/app/server --python_out=/app/server --grpc_python_out=/app/server /app/server/workloads.proto
echo "generated protobuf files"

# Start the main application
echo "starting the server"
python /app/server/main.py