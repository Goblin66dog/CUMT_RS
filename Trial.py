import cv2
from Dataset import Dataset
import numpy as np
from osgeo import gdal

if __name__ == "__main__":
    dataset1 = Dataset(r"D:\Pycharm_Project\0000000\Sigma0_VV.img")
    save_path = "mosiac.tif"
    driver = gdal.GetDriverByName("GTiff")
    data = driver.Create(save_path, dataset1.im_width, dataset1.im_height, dataset1.im_bands, dataset1.datatype)
    data.SetGeoTransform(dataset1.geotrans)
    data.SetProjection(dataset1.proj)

    for cols in dataset1.data_array:

        data.GetRasterBand(1).WriteArray(cols)
    del data