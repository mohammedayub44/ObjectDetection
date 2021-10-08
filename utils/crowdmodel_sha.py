import sys, os
# module_path = os.path.abspath(os.path.join('..'))
# if module_path not in sys.path:
#     sys.path.append(module_path)
# print(module_path)
import torch
import numpy as np
from Network.SSDCNet import SSDCNet_classify

class CrowdCounter(SSDCNet_classify):
    def __init__(self):
        self.max_num = 22
        self.step = 0.5
        self.li = np.arange(self.step,self.max_num+self.step,self.step)
        self.add = np.array([1e-6,0.05,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45])
        self.label_indice = torch.Tensor(np.concatenate((self.add,self.li)))
        self.class_num = len(self.label_indice)+1
        self.div_times = 2
        self.psize, self.pstride = 64, 64
        super(CrowdCounter, self).__init__(self.class_num,label_indice=self.label_indice,div_times=self.div_times,\
                                                frontend_name='VGG16',block_num=5,\
                                                IF_pre_bn=False,IF_freeze_bn=False,load_weights=True,\
                                                psize=self.psize,pstride = self.pstride,parse_method ='maxp')

    def load_state_dict(self, state_dict, strict=True):
        return super(CrowdCounter, self).load_state_dict(state_dict['net_state_dict'], strict)
