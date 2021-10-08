from tensorflow_serving.apis import prediction_service_pb2_grpc
from keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model as keras_load_model
from tensorflow.core.framework import types_pb2
from tensorflow_serving.apis import predict_pb2
from keras.models import model_from_json
from flask import Flask,jsonify,request,Response
import matplotlib.pyplot as plt
from PIL import Image,ImageFile
from datetime import datetime
from keras import backend as K
from tensorflow import keras
from flask_cors import CORS,cross_origin
from flask import session
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import joblib
import requests
import logging
import random
import string
import grpc
import time
import json
import io
import os
import base64
import config
import pandas as pd
from config import db
from models import Video, Snapshot, Occupancytype

# Get the application instance
connex_app = config.connex_app

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('swagger.yaml')

# (not required) Route specific CORS added for endpoints below
# CORS(connex_app.app)

logging.getLogger('flask_cors').level = logging.DEBUG
logging.basicConfig(level=logging.DEBUG)

def prepare_image(img, im_type=None):
    if im_type=="classify":
        newsize = (224, 224) 
        img = img.resize(newsize) 
    #Function to load,normalize and return image 
    im = np.array(img)
    im = im/255.0
    im[:,:,0]=(im[:,:,0]-0.485)/0.229
    im[:,:,1]=(im[:,:,1]-0.456)/0.224
    im[:,:,2]=(im[:,:,2]-0.406)/0.225
    im = np.expand_dims(im,axis  = 0)
    print(str(im.shape))
    return im

def create_tf_prediction_request():
    channel = grpc.insecure_channel("127.0.0.1:8500")
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    request = predict_pb2.PredictRequest()
    return stub,request


@connex_app.route('/', methods=['GET',"POST","OPTIONS"])
@cross_origin()
def home():
    return '''<h1>Crowd Detection API</h1>
<p>Endpoint /predict with Image parameter returns count and heatmap.</p>'''

@connex_app.route("/predict", methods=["POST","OPTIONS"])
@cross_origin()
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    start = time.time()
    st, req = create_tf_prediction_request()
    data = {"success": False}
    # print(type(request.get_json(force=True)))
    # print(request.get_json(force=True))
    
    # ensure an image was properly uploaded to our endpoint
    if request.method == "POST" or request.method == "OPTIONS":
        if request.get_json(force=True) is not None: #request.files.get("image"):
            # read the image in PIL format
            # image = request.files["image"].read()
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            img_data = request.get_json(force=True)['data']
            v_area = request.get_json(force=True)['metadata']['area']
            v_url = request.get_json(force=True)['metadata']['vidUrl']
            v_units = request.get_json(force=True)['metadata']['units']
            v_occtype = request.get_json(force=True)['metadata']['occType']
            v_duration = request.get_json(force=True)['metadata']['duration']
            v_threshold = request.get_json(force=True)['metadata']['threshold']
            
            if len(img_data) % 4:
                # not a multiple of 4, add padding:
                img_data += '=' * (4 - len(img_data) % 4)
            
            # image_datare.sub('^data:image/.+;base64,', '', data['img']).decode('base64')
            image = Image.open(io.BytesIO(base64.b64decode(img_data)))
            # print("Image:"+ str(image))
            print(os.getcwd())
            # Create video name
            # v_name = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 5))
            # v_name = v_url
            
            # Create Dynamic Path
            img_path = os.path.join(connex_app.app.config['SNAPSHOT_FOLDER'],
                                        ''.join(random.choices(string.ascii_uppercase +string.digits, k = 10)))
            
            print(img_path)
            
            hmap_path = os.path.join(connex_app.app.config['HEATMAP_FOLDER'],
                                        ''.join(random.choices(string.ascii_uppercase +string.digits, k = 10)))
            
            print(hmap_path)
            classify_model_path = os.path.join(connex_app.app.config['CLASSIFY_MODEL_FILE'])
            
            # Save the clicked image
            image.save(img_path+'.png', "PNG")
            
            # session["snapshot_data"] = img_data
            # preprocess the image and prepare it for classification
            c_image = prepare_image(image,im_type="classify")
            
            # Set session for Classify
            # K.set_session(c_session)
            # req.model_spec.name = "classify"
            # req.inputs["input_image"].CopyFrom(tf.make_tensor_proto(c_image, dtype=types_pb2.DT_FLOAT))
            req.model_spec.name = "vgg16_nohead"
            req.inputs["input_1"].CopyFrom(tf.make_tensor_proto(c_image, dtype=types_pb2.DT_FLOAT))
            print("extracting")
            response = st.Predict(req, timeout=60.0)
            feat = tf.make_ndarray(response.outputs['block5_pool'])
            features = feat.reshape((feat.shape[0], 7 * 7 * 512))
            # predictions = tf.make_ndarray(response.outputs['dense_11/Softmax:0'])
            
            # Classify the Image
            # predictions = classify_model.predict(c_image)
            # predicted_classes = np.argmax(predictions,axis=1)
            print("loading")
            clf = joblib.load(classify_model_path)
            print("classify")
            class_label = clf.predict(features)
            
            # print("Predcited Class (0-dense, 1-sparse): Class "+str(predicted_classes[0]))
            print("Predcited Class (0-dense, 1-sparse): Class "+str(class_label))
            
            temp_img_bytes = io.BytesIO()
            image.save(temp_img_bytes, format='JPEG')
            ssdcnet_img_data = temp_img_bytes.getvalue()
            
            image = prepare_image(image)
            
            print("adding video to db")
            # video = Video(url="fav_mixed_tape.avi")
            # Hardcoding random load id for now. TODO: Change this.
            # load_id = random.randint(1, 37)
            occ_load = Occupancytype.query.filter_by(use=v_occtype).one_or_none()
            print("Occupant Type found: "+ str(occ_load.use)+ " "+ str(occ_load.id) )
            # occ_load = Occupancytype.query.filter_by(id=load_id).one_or_none()
            
            # video = Video(url="MNTFJ.avi",vid_load_ref=occ_load)
            video = Video.query.filter_by(url=v_url,area=v_area,vid_load_ref=occ_load).one_or_none()
            print(type(video))
            print("old:" + str(video))
            # Workaround to check for uniqueness in Video table
            if video:
                video.last_updated = datetime.utcnow()
            else:  
                video = Video(url=v_url, area=v_area, units=v_units, threshold=v_threshold, duration=v_duration,vid_load_ref=occ_load)
                print("current:" + str(video))
                db.session.add(video)
            db.session.commit()
            # insert_command = Video.__table__.insert( 
            #     prefixes=['OR IGNORE'],
            #     values=dict(url='fav_mixed_tape.avi')
            #     )
            # db.session.execute(insert_command)
            # st2, req2 = create_tf_prediction_request()
            
            # Important to del the input dict from the previous request if you need to reuse 
            # the same request multiple times. Otherwise it appends another inputs field which gives
            # input shape mismatch error. 
            del req.inputs['input_1']
            
            if class_label == '1':
                # classify the input image and then initialize the list
                # of predictions to return to the client
                req.model_spec.name = "sparse_crowd"
                req.inputs["input_image"].CopyFrom(tf.make_tensor_proto(image, dtype=types_pb2.DT_FLOAT))
                p_stime = time.time()
                # K.set_session(session)
                # p_hmap = loaded_model.predict(image)
                response = st.Predict(req, timeout=60.0)
                p_etime = time.time()
                
                ssdcnet_sparse_url = 'http://0.0.0.0:8443/predictions/ssdcnet_shb_gpu_2'
                
                # Run SSDCNet model
                p_stime_ts = time.time()
                ssdcnet_res = requests.post(ssdcnet_sparse_url,data=ssdcnet_img_data)
                p_etime_ts = time.time()
                ssdcnet_count = ssdcnet_res.text
                ssd = int(float(ssdcnet_count))
                
                # ssdcnet_count = '50' # Fix batching in Torchserve
                
                p_hmap = tf.make_ndarray(response.outputs['y_out/Relu:0'])
                
                data["predict_time_ms"] = str(round((p_etime - p_stime)*1000))
                data["predict_time_ts_ms"] = str(round((p_etime_ts - p_stime_ts)*1000))
                count = int(np.sum(p_hmap))
                
                average = (ssd + count) / 2 
                
                
                print(p_hmap.shape)
                
                p_hmap = p_hmap.reshape(p_hmap.shape[1],p_hmap.shape[2])
                print(p_hmap.shape)
                fig = plt.figure(frameon=False)
                # fig.set_size_inches(p_hmap.shape[0],p_hmap.shape[1])
                ax = plt.Axes(fig, [0., 0., 1., 1.])
                ax.set_axis_off()
                fig.add_axes(ax)
                ax.imshow(p_hmap, aspect='auto')
                ib = io.BytesIO()
                fig.savefig(ib,bbox_inches='tight', pad_inches=0)
                fig.savefig(hmap_path+'.png', format='png', bbox_inches='tight', pad_inches=0)
                ib.seek(0)
                new_image_string = base64.b64encode(ib.getvalue()).decode("utf-8")
                print(str(len(new_image_string)))
                
                snapshot = Snapshot(snap=img_path+".png",
                                    heatmap=hmap_path+".png", 
                                    pred_class = "sparse", 
                                    pred_count = count, 
                                    pred_count_ssdcnet=ssdcnet_count,
                                    video_id_ref=video)
                db.session.add(snapshot)
                
                r = {"class": "Sparse","count": str(int(round(count))), "ssdcnet_count": str(ssdcnet_count), "predicted_heatmap": str(new_image_string), "average": str(average) }
                data["predictions"] = r
                
                print("Predicted Count: " + str(round(count)))
                print("Predicted SSDCNet Count: " + str(ssdcnet_count))
                
            else:
                
                ssdcnet_dense_url = 'http://0.0.0.0:8443/predictions/ssdcnet_sha_gpu_2'
                req.model_spec.name = "dense_crowd"
                req.inputs["input_image"].CopyFrom(tf.make_tensor_proto(image, dtype=types_pb2.DT_FLOAT))
                
                p_stime = time.time()
                response = st.Predict(req, timeout=60.0)
                p_etime = time.time()
                
                # Run SSDCNet model
                p_stime_ts = time.time()
                ssdcnet_res = requests.post(ssdcnet_dense_url,data=ssdcnet_img_data)
                p_etime_ts = time.time()
                ssdcnet_count = ssdcnet_res.text
                ssd = int(float(ssdcnet_count))
                # ssdcnet_count = '50' # Fix Torchserve batching
                
                p_hmap = tf.make_ndarray(response.outputs['y_out/Relu:0'])
                data["predict_time_ms"] = str(round((p_etime - p_stime)*1000))
                data["predict_time_ts_ms"] = str(round((p_etime_ts - p_stime_ts)*1000))
                count = int(np.sum(p_hmap))
                
                average = (ssd + count) / 2 

                
                print(p_hmap.shape)
                p_hmap = p_hmap.reshape(p_hmap.shape[1],p_hmap.shape[2])
                print(p_hmap.shape)
                fig = plt.figure(frameon=False)
                # fig.set_size_inches(p_hmap.shape[0],p_hmap.shape[1])
                ax = plt.Axes(fig, [0., 0., 1., 1.])
                ax.set_axis_off()
                fig.add_axes(ax)
                ax.imshow(p_hmap, aspect='auto')
                ib = io.BytesIO()
                fig.savefig(ib,bbox_inches='tight', pad_inches=0)
                fig.savefig(hmap_path+'.png', format='png', bbox_inches='tight', pad_inches=0)
                ib.seek(0)
                new_image_string = base64.b64encode(ib.getvalue()).decode("utf-8")
                print(str(len(new_image_string)))
                
                snapshot = Snapshot(snap=img_path+".png",
                                    heatmap=hmap_path+".png", 
                                    pred_class = "dense", 
                                    pred_count = int(count), 
                                    pred_count_ssdcnet=ssdcnet_count,
                                    video_id_ref=video)
                db.session.add(snapshot)
                
                r = {"class": "Dense","count": str(round(count)), "ssdcnet_count": str(ssdcnet_count), "predicted_heatmap": str(new_image_string) , "average": str(average)}
                data["predictions"] = r
                
                print("Predicted Count: " + str(round(count)))
                print("Predicted SSDCNet Count: " + str(ssdcnet_count))
                
            db.session.commit()
        
    data["success"] = True
    end = time.time()
    data["total_time_ms"] = str(round((end - start)*1000))
    resp = Response(json.dumps(data))
    
    return resp


# Create all the necessary DB tables
config.db.create_all()

# Get Row count in Occupancy Table
tot_rows = db.session.query(Occupancytype).count()

# Insert rows from csv into Occupancy table
if tot_rows < 1:
    file_name = '../data/occupantLoadFactor.csv'
    df = pd.read_csv(file_name)
    for _, row in df.iterrows():
      load = Occupancytype(use=row["Use"], load_ft2=row["ft2_person"], load_m2=row["m2_person"])
      db.session.add(load)
    db.session.commit()

if __name__ == "__main__":
    connex_app.run(port=8081)