# Data informed Crowd Detection and Management
Analyzing large crowds from video feeds


https://user-images.githubusercontent.com/7122670/136591602-720dd6a5-fca5-42e1-a089-8f75f92f178c.mp4

Front End Created by Fred MacDonald 

## Motivation
Large crowds can present some of the most complex challenges faced by safety officers, code officials, and facility managers. 
Crowd management has been a long-standing life safety concern for both fire-related and non-fire emergencies in an array of venues, including sports facilities, concert halls, clubs, malls, and fairgrounds. 
Crowd dynamics can lead to trampling incidents, crowd crushes, and violence, and when these events combine with insufficient means of egress and ineffective crowd management, injuries and deaths can occur, sometimes in staggering numbers.

But what if crowd managers and authorities having jurisdiction (AHJs) could evaluate crowd dynamics with a real-time, automated crowd monitoring system? 
What if they could use detailed, data-informed situational awareness to identify rapid changes in crowd density, movement, and other behaviors and neutralize potentially dangerous situations?

This data-informed crowd management project aims to solve some of the above concerns.  
The goal of the project is to develop a open-source prototype tool that could be developed and integrated into a real-time situational platform designed to automatically monitor crowds in a specified area and compare the estimated crowd size against requirements specified life safety codes, such as NFPA 101. 
The vision is not intended to replace safety officials; instead, the tool can be used as part of the event planning process, and during live events to support crowd managers as they make timely, informed decisions.

## Methodological Approach

The evolution of Neural Network (NN) architectures in the past couple of years has shown to be very promising in the field of computer vision use cases.
Specifically, variations of Convolutional Netural Networks(CNNs) have been used as State-of-the-art techniques to do Facial Recognition, Image Classification/Labeling and more recently crowd detection techniques.
[More Details](https://www.mitpressjournals.org/doi/full/10.1162/neco_a_00990).

Real time crowd counting can be thought of as estimating the number of people in a series of still images or video frames. 
We take a two step apporaching this calculation.  First, we initially classify the image of the crowd as falling into one or two categorys: a sparse crowd or a dense crowd. We then apply a CNN model to count the number of people, with the specific model used having been fine-tuned to count eithr sparse or dense crowds.
Although the first step in our process is optional, we have found the predicted count is much closer to ground truth when adding in this step. (TODO: Add test results section)

Various Open Source data repositories with labelled crowd images/videos has been used to train, validate and test this application. See [Datasets](docs/Datasets.md) for more details.

For the first classfication step, we use the [VGG16 model](https://arxiv.org/pdf/1409.1556.pdf) as the base and use [Transfer Learning](https://en.wikipedia.org/wiki/Transfer_learning) approaches to fine tune the model on large crowd images. This is done by changing the last softmax layer to match the output categories. [More Details](https://machinelearningmastery.com/how-to-use-transfer-learning-when-developing-convolutional-neural-network-models/). For second step of crowd counting, we pretrained models from teh  [Congested Scene Recognition (CSRNet)](https://arxiv.org/pdf/1802.10062.pdf) family. CSRNet modle are estimation models that aim to generate high-quality density maps by using [dilated convolutions](http://vladlen.info/papers/dilated-convolutions.pdf). They also uses VGG16 as base layers because of its strong transfer learning ability and flexbility to modify the architecture without adding much complexity to training. 

In addition to CSRNet models originally published in 2018, we also used more recent crowd counting model, the [Supervised Spatial Divide and Conquer (SSDCNet) model](https://arxiv.org/pdf/2001.01886.pdf) (May 2020).  Our initial analysis suggests that the SSDCNet models may yield slightly better performance on high density crowd images. 

The prototype application is built using a simple Python backend and ReactJS frontend. We choose these technologies because of model compatibility, fast prototyping and interactive visualizations. For serving the CNN models we use a combination of [Tensorflow Server](https://www.tensorflow.org/tfx/guide/serving) and [TorchServe](https://github.com/pytorch/serve) as Classification/CSRNet models are in Tensorflow format and SSDCNet models are Pytorch format. For more details on modeling see [Training and Serving](docs/Model%20Creation%20and%20Serving.md) models and for backend setup see [Database Details](docs/Database%20and%20Swagger%20Details.md)



## Getting Started

### Option 1: Docker Deployment 

```python 
# Create conda environment for the project
conda create -n crowd_count_env pip python=3.6.9
conda activate crowd_count_env  
```

```python
# Clone the project 
git clone https://github.com/NFPA/Crowd_Detection.git
```

```python
# Install python packages 
cd Crowd_Detection
pip install -r requirements.txt
# Start the docker service
bash start_docker_services.sh
```
The `start_docker_services.sh` scripts downloads all necessary models from an AWS S3 bucket to build the respective model containers. The script also runs the Flask and React application inside a docker container using `docker-compose`.

```python
# To see all running containers 
docker container ps
```

Go to `<PublicIPV4>:8080` to see the Application.

```python
# Stopping docker containers
bash stop_docker_services.sh
```

For backing up all application data, please use below container locations:

Heatmaps location - `/usr/src/app/images/heatmaps`

Snapshots location - `/usr/src/app/images/snapshots`

Application Database location - `/usr/src/app/service/crowd_counter.db` 

See [Database and Swagger Details](docs/Database%20and%20Swagger%20Details.md) for more info. on `crowd_counter.db`

### Option 2: Local Deployment 

#### Clone Project

```python
# Clone the project 
git clone https://github.com/NFPA/Crowd_Detection.git
cd Crowd_Detection
```

#### Create Environments

```python 
# Create Torchserve environment
conda create --name torchserve_gpu --file requirements_torchserve_env.txt
# To avoid package dependency errors, the above requirements file has been created using command:
# `conda list --explicit > requirements_torchserve_env.txt` 

# Create conda environment for the project
conda create -n crowd_count_env pip python=3.6.9
conda activate crowd_count_env  
```

#### Download models

```python
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
```

#### Install and Start services

```python
# Make dir's to store images and heatmaps 
mkdir -p ./images/heatmaps
mkdir -p ./images/snapshots

# Install project packages 
pip install -r requirements.txt

# Start all local services
bash start_services_gpu.sh 
```

This should create database if it does not exists, start the model Inference servers and Flask server. Refer to log files for any errors in startup. 

Go to `<PublicIPV4>:8080` to see the Application.


#### Front-End Review

Pre-Capture Controls

1. To run this application, please submit a URL pointing to a video resource in an open source format (.mp4, .mov). If one is not available we have provided a default video for testing purposes.  Note that future work could straightforwardly extend this prototype to capture streaming videos as well.

2. Once the URL is entered, click 'Load' and your video url will appear in the 'Environment Details' section on the right. 

3. After the URL is loaded, select the 'Occupancy Type' in the drop-down menu below the URL. The 'Occupancy Type' will appear in the 'Environment Details' section to the right. In addition to the Occupancy Type, the Occupancy Load values will appear below the Occupancy Type in the 'Environment Details' Section. 

4. After selecting the 'Occupancy Type', determine the square footage of the given video feed and enter it in the Area section below 'Occupany Type'. Changing the area and occupancy type values will affect the output of the Occupancy Threshold, also in the 'Environment Details' section. Once the area is greater than zero, your video will load and a graph will appear to the right. 

5. Select Metric or Imperial (English) units of measure from the radio button below Area. 

Video Capture Controls

1. Once all of the information above is entered, a user interface for the video player will show up with common controls like Play, Pause and Stop, but also Capture Frame. Capture Frame will capture the current video frame and send it to the back end deep learning models to count the crowd. Once the frame has been processed, a heatmap will appear below the player next to the capture and counts and average count from different models will appear on the graph. 

2. There is another option to 'Auto Capture' which will send captures to the backend models on a user specified (default: 2 seconds) [1 second, 2 second, 5 second, 10 second, 30 second, 60 second] interval. Auto Capture will stop at the conclusion of the video or it can be stopped by clicking the Stop Capture button. 

### Results:

[TODO: Insert heatmaps and Images of various environments/videos]


## Project Specific Members

**Victoria Hutchison** - Research Project Cordinator, Fire Protection Research Foundation, NFPA

**Joe Gochal** - Project Director, Data Analytics, NFPA

**Mohammed Ayub** - Lead Developer, Data Analytics, NFPA

**Frederick MacDonald III** - FrontEnd Developer, Data Analytics, NFPA

## Acknowledgements (Other Panel Members)
National Institute of Standards Technology (NIST) for providing the grant.

## References

1) Yuhong Li, Xiaofan Zhang, and Deming Chen. [CSRNet: Dilated Convolutional Neural Networks for Understanding the Highly Congested Scenes](https://arxiv.org/pdf/1802.10062.pdf). In The IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pages 1091–1100, 2018

2) Haipeng Xiong, Hao Lu, Chengxin Liu, Liang Liu, Chunhua Shen, Zhiguo Cao. [From Open Set to Closed Set: Supervised Spatial Divide-and-Conquer for Object Counting](https://github.com/xhp-hust-2018-2011/SS-DCNet)

3) Xiong, Haipeng and Lu, Hao and Liu, Chengxin and Liang, Liu and Cao, Zhiguo and Shen, Chunhua. [From Open Set to Closed Set: Counting Objects by Spatial Divide-and-Conquer](https://arxiv.org/pdf/2001.01886.pdf) , in Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), pages 8362-8371, 2019

3) UCF-QNRF: H. Idrees, M. Tayyab, K. Athrey, D. Zhang, S. Al-Maddeed, N. Rajpoot, M. Shah, [Composition Loss for Counting, Density Map Estimation and Localization in Dense Crowds](https://www.crcv.ucf.edu/papers/eccv2018/2324.pdf), in Proceedings of IEEE European Conference on Computer Vision (ECCV 2018), Munich, Germany, September 8-14, 2018

4) UCF-CC-50: Haroon Idrees, Imran Saleemi, Cody Seibert, Mubarak Shah, [Multi-Source Multi-Scale Counting in Extremely Dense Crowd Images](https://www.crcv.ucf.edu/papers/cvpr2013/Counting_V3o.pdf), IEEE International Conference on Computer Vision and Pattern Recognition (CVPR), 2013

5) WorldExpo'10: Cong Zhang, Hongsheng Li, Xiaogang Wang, Xiaokang Yang; [Cross-scene Crowd Counting via Deep Convolutional Neural Networks](cv-foundation.org/openaccess/content_cvpr_2015/papers/Zhang_Cross-Scene_Crowd_Counting_2015_CVPR_paper.pdf)Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2015, pp. 833-841

## License
This project is published under the [BSD-3 license](https://github.com/mohammedayub44/ObjectDetection/blob/main/LICENSE).
