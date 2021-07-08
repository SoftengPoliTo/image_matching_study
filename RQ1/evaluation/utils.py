from collections import Counter
import pygcransac
from sklearn.cluster import MeanShift
import numpy as np
from xml_read import bounds
import cv2


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


def drawMatches_img(matchesMask, matches, img1, kp1, img2, kp2, file_name):
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=(255, 0, 0),
                       matchesMask=matchesMask,
                       flags=2)

    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches, None, **draw_params)
    img3 = cv2.resize(img3, (800, 800))
    cv2.imshow("prova", img3)
    cv2.waitKey()


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


def crop_image_GRAY_SCALE(image, bounds):
    box1_main = [bounds.x_min,

                 bounds.y_min,
                 bounds.x_max,
                 bounds.y_max]

    img1 = cv2.imread(image,
                      cv2.IMREAD_GRAYSCALE)

    cropped_image1 = img1[int(bounds.y_min):int(bounds.y_max), int(bounds.x_min):int(bounds.x_max)]

    return cropped_image1


def ransac(good_matches, MIN_MATCH_COUNT, img1, img2, kp1, kp2):
    matchesMask = None
    if len(good_matches) >= MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 2)
        h1 = img1.shape[0]
        w1 = img1.shape[1]
        h2 = img2.shape[0]
        w2 = img2.shape[1]

        M, mask = pygcransac.findHomography(src_pts, dst_pts, h1, w1, h2, w2, 100.0)
        # M, mask = cv2.findHomography(src_pts, dst_pts, cv2.FM_RANSAC, 250, maxIters=2000)

        if M is not None:
            matchesMask = mask.ravel().tolist()
            h = img1.shape[0]
            w = img1.shape[1]
            pts = np.float32([[0, 0], [0, - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)
            # img2 = cv2.polylines(img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)


    else:
        print
        "Not enough matches are found - %d/%d" % (len(good_matches), MIN_MATCH_COUNT)

    return matchesMask


def sift_function(image_name_1, image_name_2, src, cropped):
    img2 = cv2.imread(image_name_2,
                      cv2.IMREAD_GRAYSCALE)

    if cropped:
        img1 = crop_image_GRAY_SCALE(image_name_1, src.bounds)
    else:
        img1 = cv2.imread(image_name_1,
                          cv2.IMREAD_GRAYSCALE)


    # Initiate  detector
    print("..based_matcher SIFT processing...")
    ptr = cv2.xfeatures2d.SIFT_create()
    kp1, des1 = ptr.detectAndCompute(img1, None)
    kp2, des2 = ptr.detectAndCompute(img2, None)
    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=10)  # or pass empty dictionary
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # Need to draw only good matches, so create a mask
    simplemask = [[0, 0] for i in range(len(matches))]
    good = []
    # ratio test as per Lowe's paper
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.9 * n.distance:
            simplemask[i] = [1, 0]
            good.append(m)

    ## ransac method applied
    ransac_matches = ransac(good, 10, img1, img2, kp1, kp2)

    if ransac_matches != None:

        src_pts = [kp1[good[x].queryIdx].pt for x in range(len(good)) if ransac_matches[x] == 1]
        dst_pts = [kp2[good[x].trainIdx].pt for x in range(len(good)) if ransac_matches[x] == 1]
    else:
        src_pts = [kp1[good[x].queryIdx].pt for x in range(len(good))]
        dst_pts = [kp2[good[x].trainIdx].pt for x in range(len(good))]

    if not cropped:
        dst_pts, matches_correct, matches, kp1_list, kp2_list = get_points_of_component(src_pts, dst_pts, src,
                                                                                        good, kp1, kp2)

    if len(dst_pts) != 0:
        clustering = MeanShift(bandwidth=0.1).fit(np.array(dst_pts))
        c = Counter(clustering.labels_)

        cluster_max = c.most_common(1)[0][0]
        point_of_max = clustering.cluster_centers_[cluster_max]

        #drawMatches_img(matches_correct, matches, img1, kp1, img2, kp2, "ransac_one_object.png")

        return point_of_max

    return [None, None]


def get_center(src, source_image_name, dest_image_name, cropped):
    point_of_max = sift_function(source_image_name, dest_image_name, src, cropped)
    return point_of_max


def get_points_of_component(src_pts, dst_pts, main_component, good, kp1, kp2):
    correct_pts = []
    matches = []
    matched_true = []
    dst_correct = 0
    kp1_list = []
    kp2_list = []
    for point_src in range(len(good)):
        if main_component.bounds.x_min < kp1[good[point_src].queryIdx].pt[0] < main_component.bounds.x_max:
            if main_component.bounds.y_min < kp1[good[point_src].queryIdx].pt[1] < main_component.bounds.y_max:
                correct_pts.append([int(kp2[good[point_src].trainIdx].pt[0]), int(kp2[good[point_src].trainIdx].pt[1])])
                matches.append(good[point_src])
                kp1_list.append(kp1[good[point_src].queryIdx])
                kp2_list.append(kp2[good[point_src].trainIdx])
                dst_correct += 1
                matched_true.append(True)

    if dst_correct == len(correct_pts):
        return correct_pts, matched_true, matches, kp1_list, kp2_list
    else:
        return None, None
