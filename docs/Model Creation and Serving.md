# Classification

## Finetuning Classifier on Crowd Image Datasets
 - We extract image features from trained VGG16 Model using simple script shown [here](https://www.pyimagesearch.com/2019/05/27/keras-feature-extraction-on-large-datasets-with-deep-learning/)

 ### 1) Build Dataset for Training Classifier
 - Concatenate data from ShanghaiTech and UCF-QNRF2018. Refer [Combining Datasets](https://github.com/NFPA/Crowd_Detection/blob/development/utils/Combine_CrowdDataset.ipynb) notebook for more details.
 - We modify the config, and run `build_dataset.py` from above Pyimagesearch Script. This generates `train`,`test`,`validation` splits with `dense` and `sparse` class label folders in each
 
 ### 2) Extract features for each Image
 - Run `extract_features.py` to extract `25,088` dimention (`7*7*512` flattened) feature vector for each image using Pretrained VGG16 Keras model.
 - We write all extracted features to csv files namely, `test.csv`, `train.csv` and `validate.csv`.

 ### 3) Train Classifier on extracted Image features
 - Modify and run `train.py` to train a simple multi-class logistic regression model on generated features (csv files). 
 - `SMOTE` library is used to handle class imbalance.
 - `GridSearch` is used to train the model with best hyperparameters. 
 - Outputs a serialized pickle model file `classify_model.pkl`. Refer [Combining Datasets](https://github.com/NFPA/Crowd_Detection/blob/development/utils/Combine_CrowdDataset.ipynb) notebook for classification example.
  
Optionally, we could have also used Keras NN model with classification head a shown in [Finetunig VGG16 for Classification](https://github.com/NFPA/Crowd_Detection/blob/development/utils/Finetune-Keras-vgg-mayub.ipynb) ( not used here).

## Serving the Classifier
- [JOBLIB](https://joblib.readthedocs.io/en/latest/) library is used to recontruct the model and run inference.

# Count Prediction

## 1) Convoluted Scene Recognition (CSRNet) Model

### Downloading: 

[CSRNet](https://github.com/Neerajj9/CSRNet-keras) - Tensorflow Implementation with training data and model.
You can download the weights from this [release](https://github.com/ZhengPeng7/CSRNet-Keras/releases) or from our [S3 Bucket](https://crowd-counter-models.s3.us-east-2.amazonaws.com/CSRNet/CSRNet_models.zip).

### Serving: Notebook - [Converting to Tensorflow Serving Format](https://github.com/NFPA/Crowd_Detection/blob/development/utils/Generate_tf_serving_models.ipynb)
 - Shows how to convert CSRNet models (Part A and B) to Tensorflow Serving format.  
 - We need to serve a VGG16 model with no head to extract features as inputs to `classify_model.pkl`
 - Shows how to test a sample image with Tensorflow Server.

Refer [`start_services_gpu.sh`](https://github.com/NFPA/Crowd_Detection/blob/development/start_services_gpu.sh) for steps to start TFServing docker.

All the Tensorflow Serving models can be downloaded from our [S3 Bucket](https://crowd-counter-models.s3.us-east-2.amazonaws.com/Serving/tf_serving_models.zip).

## 2) Supervised Spatial Divide-and-Conquer (SSDCNet) Model

### Downloading:
- Create model folder at project level to store all pytorch models.
- Download model and weights from this [repo](https://github.com/xhp-hust-2018-2011/SS-DCNet) or from our [S3 Bucket](https://crowd-counter-models.s3.us-east-2.amazonaws.com/SSDCNet/SSDCNet_models.zip).

### Serving: [Torchserve Server](https://github.com/pytorch/serve)
- Torchserve require the model to be archived (into .mar file) using [`torch-model-archiver`](https://github.com/pytorch/serve/blob/master/model-archiver/README.md) utility. 
- Archiver utility requires 
    - Model Name - unique name to connect and run inference 
    - Model Architecture - Model file describing the architectural detials 
    - Serialized File - .pt or .pth file containing state_dict
    - Handler - file descrbing inference process to be handled (needs separate tuning for batch mode)
    - Export Path - Output the archived (`.mar`) file. Refer files from [`utils`](https://github.com/NFPA/Crowd_Detection/tree/development/utils/ssdcnet_sha) folder to generate `.mar` file.

```python
torch-model-archiver --model-name ssdcnet_sha_gpu_batch --version 1.0 \
                      --model-file ./serve/examples/crowdcount/ssdcnet_sha/crowdmodel.py \
                      --serialized-file ./serve/examples/crowdcount/ssdcnet_sha/ssdcnet_sha_best_epoch.pth \
                      --export-path torchserve_model_store \
                      --handler ./serve/examples/crowdcount/ssdcnet_sha/crdcnt_handler_gpu.py -f 
```

Refer [`start_services_gpu.sh`](https://github.com/NFPA/Crowd_Detection/blob/development/start_services_gpu.sh) for steps to start torch inference server.

All `.mar` serving models can be downloaded from our [S3 Bucket](https://crowd-counter-models.s3.us-east-2.amazonaws.com/Serving/torchserve_model_store.zip)
