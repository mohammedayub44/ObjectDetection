import io
import logging
import numpy as np
import os
import zipfile
import torch
from PIL import Image
import torch.nn.functional as F
from torch.autograd import Variable
from torchvision import transforms
import subprocess

logger = logging.getLogger(__name__)


def get_pad(inputs,DIV=64):
        h,w = inputs.size()[-2:]
        ph,pw = (DIV-h%DIV),(DIV-w%DIV)
        # print(ph,pw)
    
        tmp_pad = [0,0,0,0]
        if (ph!=DIV): 
            tmp_pad[2],tmp_pad[3] = 0,ph
        if (pw!=DIV):
            tmp_pad[0],tmp_pad[1] = 0,pw
            
        # print(tmp_pad)
        inputs = F.pad(inputs,tmp_pad)
    
        return inputs

class CrowdCounterHandler(object):
    """
    MNISTDigitClassifier handler class. This handler takes a greyscale image
    and returns the digit in that image.
    """

    def __init__(self):
        self.model = None
        self.mapping = None
        self.device = None
        self.batch_size = None
        self.initialized = False

    def initialize(self, ctx):
        """First try to load torchscript else load eager mode state_dict based model"""

        properties = ctx.system_properties
        self.batch_size = int(properties.get("batch_size"))
        logger.info('Context details: \n {0}\n'.format(str(ctx.system_properties)))
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")
        # self.device = torch.device("cpu")
        model_dir = properties.get("model_dir")
        logger.info('Model Dir: '+str(model_dir))
        # modelpath = os.path.join(model_dir,"Network/crowdmodel_sha")
        for file in os.listdir(model_dir):
            if zipfile.is_zipfile(file): 
                logger.info('UnZipping File: '+str(file))
                with zipfile.ZipFile(file) as item:
                   item.extractall()  # extract it in the working directory
        
        # To Check if zip extracted correctly
        # cmd = ['ls', model_dir]
        # proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # o, e = proc.communicate()
        
        # logger.info('Output: ' + o.decode('ascii'))
        # logger.info('Error: '  + e.decode('ascii'))

        from crowdmodel_sha import CrowdCounter
        
        # Read model serialize/pt file
        model_pt_path = os.path.join(model_dir, "ssdcnet_sha_best_epoch.pth")
        # Read model definition file
        model_def_path = os.path.join(model_dir, "crowdmodel_sha.py")
        if not os.path.isfile(model_def_path):
            raise RuntimeError("Missing the model definition file")

        state_dict = torch.load(model_pt_path, map_location=self.device)
        self.model = CrowdCounter()
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        logger.info('Model file {0} loaded successfully'.format(model_pt_path))
        self.initialized = True

    def preprocess(self, request):
        """
         Converts, pads, and normalizes a PIL image for CrowdCounting model,
         returns an Numpy array
        """
        logger.info("Inside Preprocessing: ")
        image_tensor = None
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        rgb_avg = [0.40954337, 0.36924595, 0.3595245]
        rgb_avg = np.array(rgb_avg).reshape(1,1,3)
        # rgb = mat['rgbMean'].reshape(1, 1, 3)
        
        for idx, data in enumerate(request):
            image = data.get("data")
            if image is None:
                image = data.get("body")
                
            # logger.info("Data: "+ str(data))
            logger.info("Datatype: "+ str(type(data)))
            image = Image.open(io.BytesIO(image)).convert('RGB')
            # image = Image.open(data).convert('RGB')
            image = transforms.ToTensor()(image)
            image = image[None,:,:,:]
            logger.info("Before padding: "+ str(image.shape))
            image = get_pad(image,DIV=64)
            logger.info("After padding: "+str(image.shape))
            image = image - torch.Tensor(rgb_avg).view(3,1,1)
            if image.shape is not None:
                if image_tensor is None:
                    image_tensor = image
                    print("inside if")
                else:
                    image_tensor = torch.cat((image_tensor, image), 0)
                    print("inside else")
        print("final images shape:"+str(image_tensor.size()))
        return image_tensor.type(torch.float32).to(self.device)
    
    def inference(self, img):
        ''' Predict the count in the image using a SSDC-Net model.
        '''
        #output_counts = []
        features = self.model.forward(img)
        print("Feature type:"+str(type(features)))
        for key, v in features.items():
            if (isinstance(v, list)):
                print(str(key) + ": " +str(len(v)))
            else:
                print(str(key) + ": " +str(v.size()))
        # print("Features:"+str(features))
        # print("Feature shape:"+str(features.shape))
        # num_rows, num_cols = features.shape
        
        div_res = self.model.resample(features)
        print("Div Res:")
        for key, v in div_res.items():
            if (isinstance(v, list)):
                print(str(key) + ": " +str(len(v)))
            else:
                print(str(key) + ": " +str(v.size()))
                
        merge_res = self.model.parse_merge(div_res)
        print("Merge Result:")
        for key, v in merge_res.items():
            if (isinstance(v, list)):
                print(str(key) + ": " +str(len(v)))
            else:
                print(str(key) + ": " +str(v.size()))
        logger.info("before outputs: ")
        
        output_counts = []
        for i in range(merge_res['div'+str(self.model.div_times)].size()[0]):
            logger.info("iter: " + str(i))
            # print(type(merge_res['div2']))
            # print(str(merge_res['div2'].size()))
            # print(type(merge_res['div2'][0]))
            # print(str(merge_res['div2'][0].size()))
            outputs = merge_res['div'+str(self.model.div_times)][i].sum()
            outputs = round(outputs.item())
            # print(type(outputs))
            print(str(outputs))
            output_counts.append(outputs)
        logger.info("before returning: ")
        return output_counts

    # def postprocess(self, inference_output):
    #     return inference_output


_service = CrowdCounterHandler()


def handle(data, context):
    if not _service.initialized:
        _service.initialize(context)

    if data is None:
        return None
    # logger.info("Data: "+ str(data))
    logger.info("Datatype: "+ str(type(data)))
    data = _service.preprocess(data)
    logger.info("Done preprocessin...")
    data = _service.inference(data)
    logger.info("done inference... ")
    torch.cuda.empty_cache()
    # data = _service.postprocess(data)

    return data
