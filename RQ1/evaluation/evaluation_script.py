import csv
import os
from os.path import join
from collections import Counter

from PIL import Image

from utils import matching_components, save_elements
from sklearn.cluster import MeanShift
from sklearn.metrics import precision_score, recall_score, confusion_matrix

import numpy as np
import datetime

from Csv_writer import write_row
from testing_utils import get_points_of_component, index_component, check_match
from utils import crop_image, composed_cropped, composed_cropped_2
from xml_read import bounds
from Android_class import ViewHierarchy


class object_ui:
    def __init__(self, uiobject, element_path):

        self.bounds = bounds(
            [uiobject.bounding_box.x1, uiobject.bounding_box.y1, uiobject.bounding_box.x2, uiobject.bounding_box.y2])
        self.element_path = element_path
        if uiobject.text != "":
            self.action_value = uiobject.text.encode('utf-8') if uiobject.text != None else uiobject.text
        elif uiobject.content_desc != "":
            self.action_value = uiobject.content_desc.encode(
                'utf-8') if uiobject.content_desc != None else uiobject.content_desc
        elif uiobject.resource_id != "" and uiobject.resource_id != None:
            self.action_value = uiobject.resource_id.split("/")[1].encode('utf-8')
        else:
            self.action_value = ""
        self.text = uiobject.text.encode('utf-8')
        self.content_desc = uiobject.content_desc.encode(
            'utf-8') if uiobject.content_desc != None else uiobject.content_desc
        self.resource_id = uiobject.resource_id.encode(
            'utf-8') if uiobject.resource_id != None else uiobject.resource_id
        self.android_class = uiobject.android_class.encode(
            'utf-8') if uiobject.android_class != None else uiobject.android_class
        self.used = False


class test_object:
    def __init__(self, test):
        lines = test.split(";")
        self.test_id = lines[0]
        self.app = lines[1]
        self.dev_1 = lines[2]
        self.dev_2 = lines[3]
        self.resource_id = lines[4].encode('utf-8')
        self.android_class = lines[5].encode('utf-8')
        self.text = lines[6].encode('utf-8')
        self.content_desc = lines[7].encode('utf-8')
        self.x_center = float(lines[8])
        self.y_center = float(lines[9])


def lines_to_list(path):
    with open(path) as f:
        content = f.readlines()
    content = [x.strip(";") for x in content]
    return content


def getCenter(param):
    return [param[0] + (float(param[2]) - float(param[0])) / 2, param[1] + (float(param[3]) - float(param[1])) / 2]


def center_included(point_of_max, i):
    if i.bounds.x_min < point_of_max[0] < i.bounds.x_max:
        if i.bounds.y_min < point_of_max[1] < i.bounds.y_max:
            return True
    return False


def current_src(src_objects, target):
    for i in src_objects:
        if i.resource_id == target.resource_id and i.text == target.text and i.content_desc == target.content_desc and i.android_class == target.android_class:
            return i
    return None


def get_center(test_data, src):
    for i in test_data:
        if i.resource_id == src.resource_id and i.text == src.text and i.content_desc == src.content_desc and i.android_class == src.android_class:
            return [i.x_center, i.y_center]
    return [None, None]


def eval():
    source_xml_path = ["Screenshot_0dump.txt"]
    dest_xml_path = ["Screenshot_0dump.txt"]
    test_path = "test_file.txt"
    source_device = "Pixel_3_API_25"
    dest_device = "Pixel_3_API_25"
    test_lines = lines_to_list(test_path)
    test_data = [test_object(t) for t in test_lines]

    tp = [0 for i in range(len(source_xml_path))]
    fp = [0 for i in range(len(source_xml_path))]
    gt = [0 for i in range(len(source_xml_path))]

    for i in range(len(source_xml_path)):
        f = open(join(source_xml_path[i]), "rb")
        f2 = open(join(dest_xml_path[i]), "rb")
        view_src = ViewHierarchy(source_device)
        view_src.load_xml(f.read())
        view_dst = ViewHierarchy(dest_device)
        view_dst.load_xml(f2.read())
        ui_objects_src = [object_ui(v.uiobject, v.element_path) for v in view_src.get_leaf_nodes()]
        ui_objects_dst = [object_ui(v.uiobject, v.element_path) for v in view_dst.get_leaf_nodes()]

        for test in test_data:
            gt[i] += 1
            src = current_src(ui_objects_src, test)
            for dst in ui_objects_dst:
                if src.resource_id == dst.resource_id and src.text == dst.text and src.content_desc == dst.content_desc and src.android_class == dst.android_class and src.element_path == dst.element_path:  # controllo path
                    # oggetto trovato
                    center = get_center(test_data, src)

                    if center_included(center, src):
                        if not dst.used:
                            tp[i] += 1
                            dst.used = True
                        else:
                            fp[i] += 1

                    # TP
                    else:
                        # FP
                        fp[i] += 1

        total_tp = sum(tp)
        total_fp = sum(fp)
        total_fn = sum(gt) - sum(tp)
        precision = float(total_tp) / (float(total_tp) + float(total_fp))
        recall = float(total_tp) / (float(total_tp) + float(total_fn))

        print("Main_dev: " + source_device.__str__())
        print("Target_dev: " + dest_device.__str__())
        print("App: " + source_xml_path[i].__str__())
        print("precision: " + precision.__str__())
        print("recall: " + recall.__str__())


if __name__ == "__main__":
    WantedWidget = {}
    eval()
