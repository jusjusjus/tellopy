
import numpy as np
from os.path import join, dirname
import torch
from .models import Darknet
from .models import load_weights
from .utils import non_max_suppression
from .utils import load_classes
from collections import namedtuple
from skimage.transform import resize

Detection = namedtuple('Detection', 'x1 y1 x2 y2 conf cls_conf cls_pred')

class Detector:

    weights_path = join(dirname(__file__), 'weights', 'yolov3.pt')
    config_path = join(dirname(__file__), 'config', 'yolov3.cfg')
    class_path = join(dirname(__file__), 'data', 'coco.names')
    conf_thres = 0.8
    nms_thres = 0.4
    img_size = 416

    def __init__(self):
        self.model = Darknet(self.config_path, img_size=self.img_size)
        self.load_weights()
        self._eval = False

    def load_weights(self):
        # self.model.load_weights(self.weights_path)
        if self.weights_path.endswith('.pt'):  # pytorch format
            checkpoint = torch.load(self.weights_path, map_location='cpu')
            self.model.load_state_dict(checkpoint['model'])
            del checkpoint
        else:  # darknet format
            load_weights(self.model, self.weights_path)

    @property
    def eval(self):
        self.model.eval()
        self._eval = True

    @eval.setter
    def eval(self, b: bool):
        self._eval = b
        if b:
            self.model.eval()
        else:
            self.model.train()

    def cuda(self):
        self.model.cuda()

    def raw_call(self, *args, **kwargs):
        detections = self.model(*args, **kwargs)
        detections = non_max_suppression(detections, self.conf_thres, self.nms_thres)
        return detections

    def __call__(self, *args, **kwargs):
        if self.eval:
            with torch.no_grad():
                return self.raw_call(*args, **kwargs)
        else:
            return self.raw_call(*args, **kwargs)

    def prepare(self, img: np.ndarray):
        h, w, _ = img.shape
        dim_diff = np.abs(h - w)
        # Upper (left) and lower (right) padding
        pad1, pad2 = dim_diff // 2, dim_diff - dim_diff // 2
        # Determine padding
        pad = ((pad1, pad2), (0, 0), (0, 0)) if h <= w else ((0, 0), (pad1, pad2), (0, 0))
        # Add padding
        input_img = np.pad(img, pad, 'constant', constant_values=127.5) / 255.
        # Resize and normalize
        input_img = resize(input_img, (self.img_size, self.img_size, 3), mode='reflect')
        # Channels-first
        input_img = np.transpose(input_img, (2, 0, 1))
        # As pytorch tensor
        input_img = torch.from_numpy(input_img).float()
        return input_img

    def predict(self, img: np.ndarray):
        tensor = self.prepare(img)
        detections = self(tensor[None, ...])
        return detections

    @property
    def classes(self):
        try:
            return self._classes
        except AttributeError:
            self._classes = load_classes(self.class_path)
            return self.classes
