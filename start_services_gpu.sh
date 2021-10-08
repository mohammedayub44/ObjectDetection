#!/bin/bash

CONTAINER_NAME='crowd_counter_tf_gpu'
TF_MODEL_LOG_FILE='logs/tf_docker.txt'
PYTORCH_MODEL_LOG_FILE='logs/torchserve_docker.txt'
FLASK_SERVER_LOG_FILE='logs/flask_server.txt'
REACT_SERVER_LOG_FILE='logs/react_server.txt'

# Kill services if already running
# UI port
sudo kill -9 $(sudo lsof -t -i:8080)
# Flaskserver port
sudo kill -9 $(sudo lsof -t -i:8081)


# Starting TF-Docker container
if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
        # start existing container
        echo "Starting existing container $CONTAINER_NAME ..."
        docker container start $CONTAINER_NAME
    # Clean-up and start new container
    else 
        echo "Clearing old versions of $CONTAINER_NAME ..."
        docker container stop $CONTAINER_NAME
    	docker container rm $CONTAINER_NAME
    	echo "Starting new container with name $CONTAINER_NAME. Registering logs in file $TF_MODEL_LOG_FILE ..."
    	nvidia-docker run -d --name crowd_counter_tf_gpu -p 8500:8500 --mount type=bind,source=./serving_models/,target=/models/serving_models -t tensorflow/serving:1.15.0-gpu --per_process_gpu_memory_fraction=0.40 --model_config_file=/models/serving_models/models.config > $TF_MODEL_LOG_FILE
    fi
fi

source activate torchserve_gpu

# Start the Torchserve empty server
echo "Starting Pytorch model server and storing log in $PYTORCH_MODEL_LOG_FILE ..."

# export PYTHONPATH=${PYTHONPATH}:/home/ubuntu/mayub/Github/SSDCNet (Not required as Zip file is included in .mar )
torchserve --start --ncs --model-store torchserve_model_store > $PYTORCH_MODEL_LOG_FILE
sleep 5

# Register the SHA Dense model on Torchserve
echo "Registering Dense model on Torchserve port 8444 ..."
curl -k -X POST "http://0.0.0.0:8444/models?model_name=ssdcnet_sha_gpu_2&url=ssdcnet_sha_gpu_batch.mar&batch_size=2&max_batch_delay=100&initial_workers=1&synchronous=true"

# Register the SHB Sparse model on Torchserve
echo "Registering Sparse model on Torchserve port 8444 ..."
curl -k -X POST "http://0.0.0.0:8444/models?model_name=ssdcnet_shb_gpu_2&url=ssdcnet_shb_gpu_batch.mar&batch_size=2&max_batch_delay=100&initial_workers=1&synchronous=true"

# Change envs to tensorflow
echo "Changing conda environments..."
source deactivate
source activate crowd_count_env

# Change to Flask Server Dir
cd ./service

# Start Flask Server
echo "Starting Flask Server on Port 8081... Check log file $FLASK_SERVER_LOG_FILE for more details."
python app.py > ../$FLASK_SERVER_LOG_FILE 2>&1 &
# BACK_PID=$!
# wait $BACK_PID
cd ..
# Start UI

cd ./ui
echo "Starting React UI on Port 8080... Check log file $REACT_SERVER_LOG_FILE for more details. "
npm start > ../$REACT_SERVER_LOG_FILE 2>&1 &
