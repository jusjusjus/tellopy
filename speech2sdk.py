

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--test', action='store_true', help='Run speech2sdk in test mode')
parser.add_argument('--large', action='store_true', help='Load large object-detection model')
opt = parser.parse_args()


if opt.test:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from tellopy import mock
    print("Starting mock server ..")
    server = mock.Tello()
    server.start()

from tellopy.speech import HotwordDetector  
from tellopy.speech2sdk import Speech2sdk
from tellopy.communications.control import Control

from tellopy.yolo.utils import prepare_tensor_for_imshow
from tellopy.yolo.detector import Detector

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from time import sleep
import socket

if not opt.large:
    Detector.weights_path = "./tellopy/yolo/weights/yolov3-tiny.pt"
    Detector.config_path = "./tellopy/yolo/config/yolov3-tiny.cfg"

detector = Detector()
detector.conf_thres = 0.4
detector.eval = True

speech_control = Speech2sdk()
speech_control.run_hotword_detector()

while True:
    if hasattr(speech_control, 'video') and speech_control.video.frame is not None:
        video = speech_control.video
        break
    sleep(1.0)

plt.ion()
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(111, xticks=[], yticks=[], frameon=False)
plt.show(block=False)
img_obj = None

while True:
    x = video.frame
    t = detector.prepare(x)
    detections = detector(t[None, ...])
    img = prepare_tensor_for_imshow(t)
    # drawing
    if img_obj is None:
        img_obj = ax.imshow(img)
    else:
        img_obj.set_data(img)

    for patch in ax.patches:
        patch.remove()
    for text in ax.texts:
        text.remove()

    for detection in detections:
        if detection is None:
            continue
        for det in detection:
            x1, y1, x2, y2, conf, cls_conf, cls_pred = det.numpy()
            description = "P(%s)=%.2g, P(o)=%.2g"%(detector.classes[int(cls_pred)], conf, cls_conf)
            bbox = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                            edgecolor='k', facecolor='none')
            # Add the bbox to the plot
            ax.add_patch(bbox)
            # Add label
            plt.text(x1, y1, s=description, color='white', fontsize=7,
                    verticalalignment='top', bbox={'color': 'k', 'pad': 0})

    fig.canvas.draw()

if opt.test:
    server.join(timeout=0.5)
    server.close()
    del server
