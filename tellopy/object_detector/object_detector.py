
import numpy as np
import tensorflow as tf
from . import label_map_util
from . import visualization_utils as vis_util
from os.path import join, dirname

class ObjectDetector:

    FIGSIZE = (12, 8)
    PATH_TO_FROZEN_GRAPH = join(dirname(__file__), 'resources', 'frozen_inference_graph.pb')
    PATH_TO_LABELS = join(dirname(__file__), 'resources', 'mscoco_label_map.pbtxt')

    def __init__(self):
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

    @property
    def category_index(self):
        return label_map_util.create_category_index_from_labelmap(
                    self.PATH_TO_LABELS, use_display_name=True)

    def predict(self, image):
        with self.detection_graph.as_default():
            with tf.Session() as sess:
                # Get handles to input and output tensors
                ops = tf.get_default_graph().get_operations()
                all_tensor_names = {output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in ['num_detections', 'detection_boxes', 'detection_scores',
                            'detection_classes', 'detection_masks']:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
                if 'detection_masks' in tensor_dict:
                    # The following processing is only for single image
                    detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                    detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                            detection_masks, detection_boxes, image.shape[0], image.shape[1])
                    detection_masks_reframed = tf.cast(
                            tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    # Follow the convention by adding back the batch dimension
                    tensor_dict['detection_masks'] = tf.expand_dims(detection_masks_reframed, 0)
                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

                # Run inference
                output_dict = sess.run(tensor_dict, feed_dict={image_tensor: np.expand_dims(image, 0)})

                # all outputs are float32 numpy arrays, so convert types as appropriate
                output_dict['num_detections'] = int(output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict[
                        'detection_classes'][0].astype(np.uint8)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                if 'detection_masks' in output_dict:
                    output_dict['detection_masks'] = output_dict['detection_masks'][0]
        return output_dict

    def imshow(self, image, bbox=None, mlab_img_obj=None):
        import matplotlib.pyplot as plt
        bbox = self.predict(image) if bbox is None else bbox

        vis_util.visualize_boxes_and_labels_on_image_array(image,
            bbox['detection_boxes'], bbox['detection_classes'], bbox['detection_scores'],
            self.category_index, instance_masks = bbox.get('detection_masks'),
            use_normalized_coordinates = True, line_thickness = 8)

        if mlab_img_obj is None:
            plt.figure(figsize=self.FIGSIZE)
            ax = plt.subplot(111)
            mlab_img_obj = ax.imshow(image)
            plt.show()
        else:
            mlab_img_obj.set_data(image)
        return mlab_img_obj
