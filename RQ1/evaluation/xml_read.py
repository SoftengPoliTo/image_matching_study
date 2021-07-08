import csv
import os
from os.path import join
from pathlib import Path

from Android_class import ViewHierarchy

folder_data_global = ""


class test_details_class:
    def __init__(self, app_details, row_readed):
        self.device_name = app_details[1]
        self.app_name = app_details[2]
        self.test_name = app_details[3]
        self.method_name = row_readed[2]
        self.method_step = row_readed[3]


class device:
    def __init__(self, row):
        self.device_name = row[1]
        self.apps = []


class app_class:
    def __init__(self, app_details, row):
        self.app_name = app_details.app_name
        self.test_array = [test_class(app_details, row)]

    def add_test_to_app(self, app_details, row):
        list_test_name = [t.parent_test_name for t in self.test_array]
        if not list_test_name.__contains__(app_details.test_name):
            self.test_array.append(test_class(app_details, row))
        else:
            index = list_test_name.index(app_details.test_name)
            self.test_array[index].add_method(app_details, row)

    def get_name(self):
        return self.app_name


class test_class:
    def __init__(self, app_details, row):
        self.parent_test_name = row[1]
        self.methods = [method_class(app_details, row)]

    def add_method(self, app_details, row):
        list_method_name = [t.method_name for t in self.methods]
        if not list_method_name.__contains__(row[2]):
            self.methods.append(method_class(app_details, row))
        else:
            index = list_method_name.index(app_details.method_name)
            self.methods[index].add_method_step(app_details, row)


class method_class:
    def __init__(self, app_details, row):
        self.method_name = row[2]
        self.method_steps = [method_step_class(app_details, row)]

    def add_method_step(self, app_details, row):
        self.method_steps.append(method_step_class(app_details, row))


class method_step_class:
    global folder_data_global

    def __init__(self, app_details, row):

        self.parent_test = row[1]
        self.method = row[2]
        self.method_step = row[3]
        self.action_type = row[6]
        self.device = app_details.device_name

        self.not_found = False
        if row[4] == "-" or row[4] == "." or row[4] == "" or row[4] == '-':
            self.action_value = row[5]
        else:
            self.action_value = row[4]

        print(self.method_step)
        self.screenshot_path = join(
            folder_data_global, app_details.device_name,
            app_details.app_name, app_details.test_name, self.method, self.method_step + ".png")
        self.xml_path = join(
            folder_data_global, app_details.device_name,
            app_details.app_name, app_details.test_name, self.method,
            self.method_step + ".xml")
        f = open(self.xml_path, "rb")
        view = ViewHierarchy(self.device)
        view.load_xml(f.read())
        node_1 = []
        if row[6] == "match" and row[5] == "1230":
            node_1 = view.get_target_node(self.action_value[0:2])
            # node_2 = view.get_target_node(self.action_value[2:4])[0].uiobject.bounding_box
        else:
            node_1 = view.get_target_node(self.action_value)
        self.ui_objects = [object_ui(v.uiobject) for v in view.get_leaf_nodes()]

        if node_1 != []:
            self.text = node_1[0].uiobject.text
            self.content_desc = node_1[0].uiobject.content_desc
            self.resource_id = node_1[0].uiobject.resource_id

            print(node_1.__str__())
            print(self.action_value)
            self.index_node = get_index(self.ui_objects, node_1[0].uiobject)

            if node_1 != []:
                node_1 = node_1[0].uiobject.bounding_box
                self.bounds = [bounds([node_1.x1, node_1.y1, node_1.x2, node_1.y2])]
        else:
            # passedit -> swipe case
            self.not_found = True
            self.bounds = []
            self.index_node = None


class bounds:

    def __init__(self, row):
        self.x_min = float(row[0])
        self.y_min = float(row[1])
        self.x_max = float(row[2])
        self.y_max = float(row[3])

    def compare(self, component_target_bounds):
        if self.x_min == component_target_bounds.x_min \
                and self.x_max == component_target_bounds.x_max \
                and self.y_min == component_target_bounds.y_min \
                and self.y_max == component_target_bounds.y_max:

            return True
        else:
            return False

    def get_string(self):
        return self.x_min.__str__()+";"+self.y_min.__str__()+";"+self.x_max.__str__()+";"+self.y_max.__str__()

class object_ui:
    def __init__(self, uiobject,element_path):

        self.bounds = bounds(
            [uiobject.bounding_box.x1, uiobject.bounding_box.y1, uiobject.bounding_box.x2, uiobject.bounding_box.y2])

        self.element_path=element_path

        if uiobject.text != "":
            self.action_value = uiobject.text.encode('utf-8')if uiobject.text!= None else  uiobject.text
        elif uiobject.content_desc != "":
            self.action_value = uiobject.content_desc.encode('utf-8')if uiobject.content_desc!= None else  uiobject.content_desc
        elif uiobject.resource_id != "" and uiobject.resource_id != None:
            self.action_value = uiobject.resource_id.split("/")[1].encode('utf-8')
        else:
            self.action_value = ""
        self.text = uiobject.text.encode('utf-8')
        self.content_desc = uiobject.content_desc.encode('utf-8') if uiobject.content_desc!= None else  uiobject.content_desc
        self.resource_id = uiobject.resource_id.encode('utf-8')if uiobject.resource_id!= None else  uiobject.resource_id
        self.android_class=uiobject.android_class.encode('utf-8')if uiobject.android_class!= None else  uiobject.android_class



def get_index(ui_object, node_1):
    for i in ui_object:
        try:
            target = object_ui(node_1)
            if i.action_value == target.action_value or i.action_value == target.text or i.action_value == target.content_desc:
                if i.bounds.compare(object_ui(node_1).bounds):
                    return ui_object.index(i)
        except:
            print(i.__str__())

    return None


class create_device():
    def __init__(self, device_name):
        self.device_name = device_name
        self.app_array = []

    def add_test_iteration(self, app_details, row):
        if app_details.app_name not in [a.get_name() for a in self.app_array]:
            app = app_class(app_details, row)
            self.app_array.append(app_class(app_details, row))
        else:
            index = [f.app_name for f in self.app_array].index(app_details.app_name)
            self.app_array[index].add_test_to_app(app_details, row)


class screenshot():
    def __init__(self, string):
        self.xml_path = string
        self.path_image = string.replace("dump.txt", ".png")
        self.device = Path(string).parts[-4]
        self.app = Path(string).parts[-3]

        f = open(join(os.path.curdir, self.xml_path), "rb")
        view = ViewHierarchy(self.device)
        view.load_xml(f.read())
        self.ui_objects = [object_ui(v.uiobject,v.element_path) for v in view.get_leaf_nodes()]
        self.screen_dim_width=view._root.attrib.get('width')
        self.screen_dim_height=view._root.attrib.get('height')

    def get_dimension_string(self):
        return self.screen_dim_width.__str__()+","+self.screen_dim_height.__str__()


def read_xml(tmp_device_name, folder_data, app_for_testing):
    global folder_data_global
    folder_data_global = join(os.path.curdir, folder_data)

    for dp, dn, filenames in os.walk(folder_data):
        print(os.path.basename(dp))

    list_of_interaction_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder_data) for f in filenames if
                                 f == 'Screenshot_0dump.txt' and dp.__contains__(tmp_device_name) and Path(dp).parts[
                                     -2] in app_for_testing]
    device = create_device(tmp_device_name)

    for i in list_of_interaction_files:
        device.app_array.append(screenshot(i))

    return device
