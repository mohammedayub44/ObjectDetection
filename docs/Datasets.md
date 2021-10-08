# Dataset Descriptions

A copy of all Datasets used is stored in a pubic S3 repository for easy replication of the results and analysis.

## Training

### [UCF-QNRF, 2018](https://www.crcv.ucf.edu/data/ucf-qnrf/) 
Largest Crowd annotated dataset till date, made available for crowd counting and localization techniques by Center for Research in Computer Vision, University of Central Florida.

Details:

| Number of Images| Number of Annotations  | Average Count  | Maximum Count  | Average Resolution | Average Density|
|:---:|:---:|:---:|:---:|:---:|:---:|
|1,535 (Train-1201 Test-334)| 1,251,642  | 815  | 12,865  |  2013 x 2902 |  1.12 x 10-4 |

*The average density, i.e., the number of people per pixel over all images is also the lowest, signifying high-quality large images.

- All images are taken from Flickr,Web and Hajj footage (Research Paper Section 4 - Data Collection) and not from a surveleilance camera streams or simulated crowd scenes. Hence, it is very diverse in terms of prepectivity, image resolution, crowd density and the scenarios which a crowd exist.

- Dataset contains buildings, vegetation, sky and roads as they are present in realistic scenarios captured in the wild. This makes this dataset more realistic as well as difficult.

- Reduce geographical bias images have been taken from various countries. Refer link for geo-tagged map.

### [UCF-CC-50, 2013](https://www.crcv.ucf.edu/data/ucf-cc-50/)

50 High Density Crowd images sourced from Flickr for research purposes by Center for Research in Computer Vision, University of Central Florida.

Details:

| Number of Images| Number of Annotations  | Average Count  | Maximum Count  | Average Resolution | Average Density|
|:---:|:---:|:---:|:---:|:---:|:---:|
|50| 63,974  | 1,279	  | 4633  |  2101 x 2888|  2.02 x 10-4 |



### [ShanghaiTech Dataset, 2016](https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Zhang_Single-Image_Crowd_Counting_CVPR_2016_paper.pdf)

[Part A](Add S3 Link) - Randomly crawled from the web.

[Part B](Add S3 Link) - Taken from busy streets of metropolitan areas in Shanghai.

Details:

| Dataset| Number of Images| Number of Annotations  | Average Count  | Maximum Count  | Average Resolution | Average Density|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|Part A | 482 (1198 Total)| 241,677 (330,000 Total)  | 501.4	  | 3139  |  589 x 868 |  9.33 x 10-4 |
|Part B | 716 (1198 Total)| 88,488 (330,000 Total)  | 123.6  | 578  |  768 × 1024|  much larger |


### [WorldExpo'10 Dataset, 2015](https://www.cv-foundation.org/openaccess/content_cvpr_2015/html/Zhang_Cross-Scene_Crowd_Counting_2015_CVPR_paper.html) 

Details:

| Number of Images| Number of Annotations  | Average Count  | Maximum Count  | Average Resolution | Average Density|
|:---:|:---:|:---:|:---:|:---:|:---:|
|3980| 225,216  | 56  | 334  | 576 x 720|  1.36 x 10-4 |

- It includes 1132 annotated video sequences captured by 108 surveillance cameras, all from Shanghai 2010 WorldExpo (Data shared for research purposes).
- Data was primarily generated to show effective cross-scene counting by using CNN models and density maps. 


## Testing 

[Pedestrian Dynamics Data Archive](https://ped.fz-juelich.de/database/doku.php) 


