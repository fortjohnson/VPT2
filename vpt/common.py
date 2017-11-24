import pickle
import os
import re
import warnings

import cv2
import numpy as np
import matplotlib.pyplot as plt

import vpt.settings as s
import vpt.utils.image_processing as ip

def load_hs_model(participant, M, radius, n_samples , refresh, segmentation_model_path, masks="cae_masks"):
    from vpt.hand_detection.rdf_segmentation_model import RDFSegmentationModel
    from vpt.streams.mask_stream import MaskStream

    if os.path.exists(segmentation_model_path) and refresh != True:
        print ("Loading existing hand segmentation model:", segmentation_model_path)
        with open(segmentation_model_path, "r") as f:
            rdf_hs = pickle.load(f)
    else:
        print ("Hand segmentation model doesn't exist: %s.  Loading data and training new model..." % (segmentation_model_path))
        rdf_hs =RDFSegmentationModel(M, radius, n_samples)
        fs = MaskStream(os.path.join("data/rdf", participant, masks, "masks"))
        rdf_hs.train(fs)
        # with open(segmentation_model_path, "w+") as f:
        #     pickle.dump(rdf_hs, f)
    return rdf_hs


def load_depthmap(fpath, ftype="bin", normalize=False):
    ''' Loads and preforms preprocessing steps to a captured image '''

    assert s.sensor != "", ("Error: No Sensor set")

    if fpath[len(fpath)-4:len(fpath)] == ".bin":
        data = np.fromfile(fpath, 'uint16')

    elif fpath[len(fpath)-4:len(fpath)] == ".npy":
        data = np.load(fpath)

    elif fpath[len(fpath)-4:len(fpath)] == ".bmp" or fpath[len(fpath)-4:len(fpath)] == ".jpg":
        data = cv2.imread(fpath)

    else:
        raise Exception('File type not supported:', fpath[len(fpath)-4:len(fpath)])

    #TODO: REFACTOR
    if s.sensor == "kinect":

        if data.shape[0] == 480 * 640:
            data = data.reshape((480, 640))
            # data = cv2.flip(data, 1)
            data = data[80:400, :]
        elif data.shape == (192, 480, 3):
            pass
        else:
            raise Exception("Invalid Data", fpath, data.shape)

    elif s.sensor == "realsense":
        if data.shape[0] == 480 * 640:
            data = data.reshape((480, 640))
            # data = cv2.flip(data, 1)
            data = data[154:346, 80:560]
        elif data.shape == (480, 640, 3):
            # data = cv2.flip(data, 1)
            data = data[154:346, 80:560, :]
        elif data.shape == (192, 480, 3):
            pass
        elif data.shape == (320, 640, 3):
            pass
        else:
            raise Exception("Invalid Data", fpath, data.shape)

    else:
        raise ValueError("Invalid Sensor Type", s.sensor)

    if normalize:
        data = ip.normalize(data)

    return data


def getFileKey(fpath):

    # add because the file structure of p0 is different than rest which affects loading the
    # correct values from the annotations list
    if s.participant == "p0" or s.participant == "p9":
        reg = '.*(error_[\\d]).*(p[\\d][a-z]).*([\\d]{6})'
    else:
        reg = '.*(p[\\d][a-z]).*([\\d]{6})'

    annot_key = ""
    match = re.match(reg, fpath)
    for m in match.groups():
        annot_key = annot_key + "/" + m

    return annot_key


def load_annotations(annotation_file, debug=False, error=False):

    annotations = {}

    def split_line(line):
        data = line.strip("\n").split("\t")
        try:
            annotations[getFileKey(data[0])] = [data[1], data[2] ]
        except ValueError as e:
            if debug:
                print ("Error Loading Annotation:", e)

    with open(annotation_file, "r") as af:
        [split_line(line) for line in af.readlines()]

    return annotations