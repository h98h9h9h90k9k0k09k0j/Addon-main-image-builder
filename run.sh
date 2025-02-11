#!/bin/bash

# Activate the virtual environment
source /opt/venv/bin/activate
echo "activated virtual environment"

# Generate the gRPC code from the protobuf definitions
python -m grpc_tools.protoc -I/app/addon --python_out=/app/addon --grpc_python_out=/app/addon /app/addon/workloads.proto
echo "generated protobuf files"

# Start the main application
echo "starting the addon"
python /app/addon/main.py