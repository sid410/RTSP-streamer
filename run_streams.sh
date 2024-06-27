#!/bin/bash

# Function to handle keyboard interrupt and terminate background processes
cleanup() {
    echo "Caught keyboard interrupt. Terminating background processes..."
    pkill -P $$
    wait
    echo "All background processes have been terminated."
    exit 0
}

# Trap the INT signal (Ctrl+C) to run the cleanup function
trap cleanup INT


python3 stream.py --video test_vids/vehicle.mp4 --stream_count 4 --port 8554 &

python3 stream.py --video test_vids/pedestrian.mp4 --stream_count 2 --port 8555 &

wait

echo "All streams have been started."
