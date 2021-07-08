from os.path import join
from Android_class import ViewHierarchy
from utils import object_ui, center_included, get_center, lines_to_list, test_object


def eval(cropped=False):
    source_xml_path = ["Screenshot_0dump_a_Pixel.txt"]
    source_png_path = ["Screenshot_0_a_Pixel.png"]
    dest_xml_path = ["Screenshot_0dump.txt"]
    dest_png_path = ["Screenshot_0.png"]
    source_device = "Pixel_3a_XL_API_25"
    dest_device = "Pixel_3a_XL_API_25"
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

        for src in ui_objects_src:
            print(ui_objects_src.index(src).__str__())
            gt[i] += 1
            for dst in ui_objects_dst:
                if src.resource_id == dst.resource_id and src.text == dst.text and src.content_desc == dst.content_desc and src.android_class == dst.android_class and src.element_path == dst.element_path:
                    # oggetto trovato
                    center = get_center(src, source_png_path[i], dest_png_path[i], cropped)

                    if center[0] is not None and center_included(center, dst):
                        if not dst.used:
                            tp[i] += 1
                            dst.used = True
                        else:
                            fp[i] += 1


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
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--cropped', dest='cropped', action='store_true')

    args = parser.parse_args()

    eval(args.cropped)
