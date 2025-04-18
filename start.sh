#!/bin/bash

echo "Starting FastAPI application..."
uvicorn app:app --host 0.0.0.0 --port 8080 --reload &

sleep 5

echo "Running the prediction pipeline..."
python pipeline.py --sport NBA
python pipeline.py --sport MLB

wait
