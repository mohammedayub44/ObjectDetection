import onnx
from onnx_tf.backend import prepare
model_onnx = onnx.load('./model_simple.onnx')
prepare(model_onnx, device='CPU')