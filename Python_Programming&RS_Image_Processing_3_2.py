import random

from skimage import io
import numpy as np
import matplotlib.pyplot as plt
import cv2
from osgeo import gdal
import os
from sklearn.ensemble import RandomForestClassifier

def svc_classifier(image_path, label_path, output_path, n_classes):
    obj = gdal.Open(image_path)
    transform = obj.GetGeoTransform()
    project = obj.GetProjectionRef()
    del obj

    img = io.imread(image_path)
    img = np.transpose(img, [2,0,1])
    image = []
    for i in img:
        i = cv2.normalize(i, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        image.append(i)
    img = np.array(image)
    img = np.transpose(img, [1,2,0])
    lab = io.imread(label_path)

    rows, cols, bands = img.shape
    palette = []
    for i in range(n_classes):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        palette.append([r, g, b])
    palette = np.array(palette)

    X = img.reshape(rows*cols, bands)

    supervised = np.array(lab, dtype=np.int8)
    supervised -= 1
    supervised[supervised < 0] =supervised.max() + 1

    y = supervised.ravel()
    train = np.flatnonzero(supervised < n_classes)
    test = np.flatnonzero(supervised == n_classes)

    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X[train], y[train])
    y[test] = clf.predict(X[test])
    supervised = y.reshape(rows, cols)
    plt.imshow(palette[supervised])
    plt.show()
    driver = gdal.GetDriverByName("GTiff")

    outfile = output_path
    filepath, filename = os.path.split(outfile)
    short, ext = os.path.splitext(filename)
    try:
        print("如果输出文件已存在，将被覆盖")
        if os.path.exists(os.path.join(filepath, short + ".tif")): os.remove(os.path.join(filepath, short + ".tif"))
        if os.path.exists(os.path.join(filepath, short + ".tfw")): os.remove(os.path.join(filepath, short + ".tfw"))
        if os.path.exists(os.path.join(filepath, short + ".tif.aux.xml")): os.remove(
            os.path.join(filepath, short + ".tif.aux.xml"))
        if os.path.exists(os.path.join(filepath, short + ".tif.ovr")): os.remove(
            os.path.join(filepath, short + ".tif.ovr"))
    except Exception as e:
        print(e)
        os._exit(2)
    print("创建输出文件")
    out = driver.Create(outfile, cols, rows, 1,gdal.GDT_Byte)
    out.SetGeoTransform(transform)
    out.SetProjection(project)
    print("写入数据……")
    out.GetRasterBand(1).WriteArray(supervised)
    out.FlushCache()
    out = None
    print("计算完成")

if __name__ == "__main__":
    img_path = r"Python_Programming&RS_Image_Processing_3\image1.tif"
    lab_path = r"Python_Programming&RS_Image_Processing_3\label.tif"
    out_path = r"Python_Programming&RS_Image_Processing_3\result_RF.tif"
    svc_classifier(img_path, lab_path, out_path, 5)