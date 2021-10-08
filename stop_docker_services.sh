#!/bin/bash

FRONT_END='crowd_detection_frontend_1'
BACK_END='crowd_detection_backend_1'
TORCH_MODELS='torch_models'
TF_MODELS='crowd_counter_tf_gpu'

echo "Stopping flask docker named $FRONT_END ..."
docker container stop $FRONT_END

echo "Stopping React docker named $BACK_END ..."
docker container stop $BACK_END

echo "Stopping TF Serving docker named $TF_MODELS ..."
docker container stop $TF_MODELS

echo "Stopping Torchserve docker named $TORCH_MODELS ..."
docker container stop $TORCH_MODELS