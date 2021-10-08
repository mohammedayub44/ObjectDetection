#!/bin/bash

CONTAINER_NAME='crowd_counter_tf_gpu'

# Stop the Docker Models (TensorFlow and Torchserve)
echo "Stopping TF Container $CONTAINER_NAME ..."
docker container stop $CONTAINER_NAME
echo "Stopping Torchserve ..."
source activate torchserve_gpu
torchserve --stop
source deactivate

# Stop/kill the services (Flask - 8081 and React - 8080)
echo "Stopping React and Flask running on PORT 8080 and 8081 ..."
sudo kill -9 $(sudo lsof -t -i:8080)
sudo kill -9 $(sudo lsof -t -i:8081)

