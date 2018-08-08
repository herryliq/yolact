"""
Instead of clustering bbox widths and heights, this script
directly optimizes average IoU across the training set given
the specified number of anchor boxes.

Run this script from the Yolact root directory.
"""

import pickle

import numpy as np
from scipy.optimize import minimize

dump_file = 'weights/bboxes.pkl'


def iou(box1, box2):
	"""
	Computes the iou between each element of box1 and each element of box2.
	Note that this assumes both boxes have the same center point.

	Args:
		- box1: shape [a, 2] an array of (w, h)
		- box2: shape [b, 2] an array of (w, h)
	
	Returns:
		- pairwise ious with shape [a, b]
	"""
	a = box1.shape[0]
	b = box2.shape[0]

	box1 = np.expand_dims(box1, axis=1).repeat(b, axis=1)
	box2 = np.expand_dims(box2, axis=0).repeat(a, axis=0)

	mins = np.fmin(box1, box2)

	area1 = box1[:, :, 0] * box1[:, :, 1]
	area2 = box2[:, :, 0] * box2[:, :, 1]
	intersection = mins[:, :, 0] * mins[:, :, 1]

	union = area1 + area2 - intersection

	return intersection / union


def avg_iou(ars:list, convout_sizes:list = [35, 19, 10, 5, 3, 2], scale:float = 1):
	# Create boxes by first making all the scales and then applying the aspect ratio
	test_boxes = np.array([[[scale / x]*2 for x in convout_sizes]] * len(ars), dtype=np.float32)
	for i in range(len(ars)):
		test_boxes[i, :, 0] *= ars[i]
		test_boxes[i, :, 1] /= ars[i]
	test_boxes = test_boxes.reshape(-1, 2)

	ious = iou(test_boxes, bboxes)

	return np.average(np.max(ious, axis=0))

def to_relative(bboxes):
	return bboxes[:, 2:] / bboxes[:, :2]

if __name__ == '__main__':
	# Load widths and heights from a dump file. Obtain this with
	# python3 scripts/save_bboxes.py
	with open(dump_file, 'rb') as f:
		bboxes = to_relative(np.array(pickle.load(f)))

	res = minimize(lambda x: -avg_iou(x), [0.55789698, 1.31440645, 0.84627934], method='Nelder-Mead')
	print('Optimization Result: %s' % res.x)
	print('Avg IoU: %.4f' % avg_iou(res.x))

# Optimization results (not accounting for image scaling):
# mIoU = 0.5635  [0.91855469]
# mIoU = 0.6416  [1.19613237 0.70644902]
# mIoU = 0.6703  [1.45072431 0.96152597 0.63814035]
# mIoU = 0.6857  [1.13719648 0.83178079 0.59529905 1.68513610]
#
# Optimization results (with scaling that doesn't preserve aspect ratio)
# mIoU = 0.5448  [0.81435547]
# mIoU = 0.6238  [0.62820609 1.07487213]
# mIoU = 0.6569  [0.55789698 1.31440645 0.84627934]
# mIoU = 0.6732  [0.51514639 1.50133034 0.72967736 1.00468417]
# mIoU = 0.6828  [0.66685089 1.7073535  0.87508774 1.16524493 0.49059086]
