import csv
import os
from os.path import join, exists


def write_row(filename, mode='a', row=[]):
    with open(filename, mode=mode) as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(row)
        employee_file.close()


def read_all(model):
    vect_tmp = []
    with open(model) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        next(readCSV, None)  # skip the headers
        for i in readCSV:
            vect_tmp.append(i)
    return vect_tmp

def read_dim(file,model):
    with open(file, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')

        for i in spamreader:
            if i[0] == model:
                return int(i[1]),int(i[2])
    return None,None


def read_current_screenshot(model, current_app, current_screenshot):
    vect_main = []
    vect_other = []
    vect_pos = []

    with open(model) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        next(readCSV, None)  # skip the headers
        for i in readCSV:
            if (current_app in i[0]) and (current_screenshot in i[0]):
                vect_pos.append(i[3:7])
                vect_main.append(i[1])
                vect_other.append(i[2])
    return vect_main,vect_other,vect_pos


class Csv_writer:
    @classmethod
    def csv_init_main_annotation(cls, model, filename):
        main_file = model + filename
        summary_file = model + "_summary_" + filename
        index_in_app = 0
        old_screenshot = ""
        if not os.path.exists(main_file):
            print(" --- custom file not present ---")
            if not os.path.exists("/data"):
                print("Data folder not present")
            mobile_devices_folder = os.listdir("data")
            print(" --- csv tmp annotation file creation ---")
            # eleWidth, eleHeight, point.getX(), point.getY(), point.getX() + eleWidth, point.getY() + eleHeight);
            write_row(main_file, 'a',
                      ['Screenshot main model','Screenshot other model','Component_main_device','Component Other device', 'x_min_main', 'y_min_main', 'x_max_main',
                       'y_max_main', 'x_min_other', 'y_min_other', 'x_max_other', 'y_max_other'])
            #write_row(summary_file, 'a', ['App/screenshot', 'Total_element'])
            for i in read_all(join(join(os.path.curdir, join("data", model)), "annotation.csv")):
                print("----- combination of " + i[0] + "----------")
                for j in mobile_devices_folder:
                    if j != model:
                        with open(join("data", j, "annotation.csv")) as csvfile:
                            readCSV = csv.reader(csvfile, delimiter=';')
                            for row in readCSV:
                                if i[0:3] == row[0:3]:
                                    tmp_row = [join(model, i[0], os.path.splitext(i[1])[0], i[1]),
                                               join(j, row[0], os.path.splitext(row[1])[0], row[1]),
                                               join(model, i[0], os.path.splitext(i[1])[0],i[2]),
                                               join(j, row[0], os.path.splitext(row[1])[0], row[2])]
                                    tmp_row.extend(i[5:9])  # main position
                                    tmp_row.extend(row[5:9])  # position other
                                    write_row(main_file, 'a', tmp_row)
                                    index_in_app = index_in_app + 1
                                    if old_screenshot != row[1] and old_screenshot != "":
                                        write_row(summary_file, 'a', [join(i[0],i[1]), index_in_app.__str__()])
                                        index_in_app=0
                                    old_screenshot = row[1]

    def csv_annotation_init(cls, method, filename):
        File_path = method + "_" + filename
        if not os.path.exists(File_path):
            print(" --- annotation " + method + " file not present ---")
            if not os.path.exists("/data"):
                raise Exception("Data folder not present")
            mobile_devices_folder = os.listdir("data")
            print(" --- csv sift annotation file creation ---")
            # eleWidth, eleHeight, point.getX(), point.getY(), point.getX() + eleWidth, point.getY() + eleHeight);
            if not exists(File_path):
                write_row(File_path, 'a',
                          ['Screenshot main model','Screenshot other model', 'Component Other device', "main_component_x", "predicted_center_x",
                           "predicted_center_y", "ransac_center_x", "ransac_center_y", "x_min", "x_max", "y_min",
                           "y_max"])
import csv
import os
from os.path import join, exists


def write_row(filename, mode='a', row=[]):
    with open(filename, mode=mode) as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(row)
        employee_file.close()


def read_all(model):
    vect_tmp = []
    with open(model) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        next(readCSV, None)  # skip the headers
        for i in readCSV:
            vect_tmp.append(i)
    return vect_tmp

def read_dim(file,model):
    with open(file, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')

        for i in spamreader:
            if i[0] == model:
                return int(i[1]),int(i[2])
    return None,None


def read_current_screenshot(model, current_app, current_screenshot):
    vect_main = []
    vect_other = []
    vect_pos = []

    with open(model) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        next(readCSV, None)  # skip the headers
        for i in readCSV:
            if (current_app in i[0]) and (current_screenshot in i[0]):
                vect_pos.append(i[3:7])
                vect_main.append(i[1])
                vect_other.append(i[2])
    return vect_main,vect_other,vect_pos


class Csv_writer:
    @classmethod
    def csv_init_main_annotation(cls, model, filename):
        main_file = model + filename
        summary_file = model + "_summary_" + filename
        index_in_app = 0
        old_screenshot = ""
        if not os.path.exists(main_file):
            print(" --- custom file not present ---")
            if not os.path.exists("/data"):
                print("Data folder not present")
            mobile_devices_folder = os.listdir("data")
            print(" --- csv tmp annotation file creation ---")
            # eleWidth, eleHeight, point.getX(), point.getY(), point.getX() + eleWidth, point.getY() + eleHeight);
            write_row(main_file, 'a',
                      ['Screenshot main model','Screenshot other model','Component_main_device','Component Other device', 'x_min_main', 'y_min_main', 'x_max_main',
                       'y_max_main', 'x_min_other', 'y_min_other', 'x_max_other', 'y_max_other'])
            #write_row(summary_file, 'a', ['App/screenshot', 'Total_element'])
            for i in read_all(join(join(os.path.curdir, join("data", model)), "annotation.csv")):
                print("----- combination of " + i[0] + "----------")
                for j in mobile_devices_folder:
                    if j != model:
                        with open(join("data", j, "annotation.csv")) as csvfile:
                            readCSV = csv.reader(csvfile, delimiter=';')
                            for row in readCSV:
                                if i[0:3] == row[0:3]:
                                    tmp_row = [join(model, i[0], os.path.splitext(i[1])[0], i[1]),
                                               join(j, row[0], os.path.splitext(row[1])[0], row[1]),
                                               join(model, i[0], os.path.splitext(i[1])[0],i[2]),
                                               join(j, row[0], os.path.splitext(row[1])[0], row[2])]
                                    tmp_row.extend(i[5:9])  # main position
                                    tmp_row.extend(row[5:9])  # position other
                                    write_row(main_file, 'a', tmp_row)
                                    index_in_app = index_in_app + 1
                                    if old_screenshot != row[1] and old_screenshot != "":
                                        write_row(summary_file, 'a', [join(i[0],i[1]), index_in_app.__str__()])
                                        index_in_app=0
                                    old_screenshot = row[1]

    def csv_annotation_init(cls, method, filename):
        File_path = method + "_" + filename
        if not os.path.exists(File_path):
            print(" --- annotation " + method + " file not present ---")
            if not os.path.exists("/data"):
                raise Exception("Data folder not present")
            mobile_devices_folder = os.listdir("data")
            print(" --- csv sift annotation file creation ---")
            # eleWidth, eleHeight, point.getX(), point.getY(), point.getX() + eleWidth, point.getY() + eleHeight);
            if not exists(File_path):
                write_row(File_path, 'a',
                          ['Screenshot main model','Screenshot other model', 'Component Other device', "main_component_x", "predicted_center_x",
                           "predicted_center_y", "ransac_center_x", "ransac_center_y", "x_min", "x_max", "y_min",
                           "y_max"])
