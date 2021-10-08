#!/bin/bash

TF_CONTAINER_NAME='crowd_counter_tf_gpu'
TORCH_CONTAINER_NAME='torch_models'
# Download TF Serving models from S3
mkdir -p serving_models
cd serving_models

# Install AWS CLI from here - https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html
aws s3 cp s3://crowd-counter-models/Serving . --recursive
cd ..

# Download Torchserve models from S3
mkdir -p torchserve_model_store
cd torchserve_model_store
aws s3 cp s3://crowd-counter-models/torchserve_models . --recursive
cd ..

sleep 5

# Build and/or Start Tensorflow Serving Docker Service
echo "Checking existing containers..."
if [ ! "$(docker ps -q -f name=$TF_CONTAINER_NAME)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=$TF_CONTAINER_NAME)" ]; then
        # start existing container
        echo "Starting existing container $TF_CONTAINER_NAME ..."
        docker container start $TF_CONTAINER_NAME
    # Clean-up and start new container
    else 
        echo "Clearing old versions of $TF_CONTAINER_NAME ..."
        docker container stop $TF_CONTAINER_NAME
    	docker container rm $TF_CONTAINER_NAME
    	echo "Starting new container with name $TF_CONTAINER_NAME ..."
    	nvidia-docker run -d --name crowd_counter_tf_gpu -p 8500:8500 --mount type=bind,source=/home/ubuntu/mayub/Github/Crowd_Detection/serving_models/,target=/models/serving_models -t tensorflow/serving:1.15.0-gpu --per_process_gpu_memory_fraction=0.40 --model_config_file=/models/serving_models/models.config
    fi
fi

# Build torchserve docker service
if [ ! "$(docker ps -q -f name=$TORCH_CONTAINER_NAME)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=$TORCH_CONTAINER_NAME)" ]; then
        # start existing container
        echo "Starting existing container $TORCH_CONTAINER_NAME ..."
        docker container start $TORCH_CONTAINER_NAME
    # Clean-up and start new container
    else
        echo "Building torchserve service image... "
        DOCKER_BUILDKIT=1 docker build --file Dockerfile_torchserve --build-arg BASE_IMAGE=nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04 -t torchserve:latest .
        # Run container
        echo "Starting container with name $TORCH_CONTAINER_NAME ... "
        docker run --rm -it -d --name torch_models --gpus all -p 8443:8443 -p 8444:8444 torchserve:latest
        sleep 5
    fi
fi

# Register the SHA Dense model on Torchserve
echo "Registering Dense model on Torchserve port 8444 ..."
curl -k -X POST "http://0.0.0.0:8444/models?model_name=ssdcnet_sha_gpu_2&url=ssdcnet_sha_gpu_batch.mar&batch_size=2&max_batch_delay=100&initial_workers=1&synchronous=true"

# Register the SHB Sparse model on Torchserve
echo "Registering Sparse model on Torchserve port 8444 ..."
curl -k -X POST "http://0.0.0.0:8444/models?model_name=ssdcnet_shb_gpu_2&url=ssdcnet_shb_gpu_batch.mar&batch_size=2&max_batch_delay=100&initial_workers=1&synchronous=true"

echo "Torchserve Status - "
curl "http://0.0.0.0:8443/ping"
echo "Torchserve Models - "
curl "http://0.0.0.0:8444/models"
sleep 2

# back and front end app
echo "Starting Flask Server on Port 8081 and React UI on Port 8080..."
docker-compose up -d
