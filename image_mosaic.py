from osgeo import gdal
from Dataset import Dataset
import cv2
import numpy as np

#该方法将过程中的变量写入磁盘栅格文件中，而后再进行读取

def mosaic(data1, data2):

    min_x1 = data1.min_x
    max_x1 = data1.max_x
    min_y1 = data1.min_y
    max_y1 = data1.max_y

    min_x2 = data2.min_x
    max_x2 = data2.max_x
    min_y2 = data2.min_y
    max_y2 = data2.max_y

    pixel_width1 = data1.pixel_width
    pixel_height1 = data1.pixel_height

    pixel_width2= data2.pixel_width
    pixel_height2 = data2.pixel_height

    # 获取输出图像的行&列
    min_X = min(min_x1, min_x2)
    max_X = max(max_x1, max_x2)
    min_Y = min(min_y1, min_y2)
    max_Y = max(max_y1, max_y2)

    # todo:行列是否需要int?
    #镶嵌时两张图像的空间分辨率相同
    image_out_cols = int((max_X - min_X) / pixel_width1)
    image_out_rows = int((max_Y - min_Y) / abs(pixel_height1))

    # 计算图1左上角的偏移值（在输出图像中）
    xOffset1 = int((min_x1 - min_X) / pixel_width1)
    yOffset1 = int((max_y1 - max_Y) / pixel_height1)

    # 计算图2左上角的偏移值（在输出图像中）
    xOffset2 = int((min_x2 - min_X) / pixel_width2)
    yOffset2 = int((max_y2 - max_Y) / pixel_height2)

    # todo:1是bands，默认
    # 创建一个输出图像
    driver = gdal.GetDriverByName("GTiff")
    dsOut1 = driver.Create('mosiac1.tif', image_out_cols, image_out_rows, 1, data1.datatype)
    dsOut2 = driver.Create('mosiac2.tif', image_out_cols, image_out_rows, 1, data2.datatype)

    bandOut1 = dsOut1.GetRasterBand(1)
    bandOut2 = dsOut2.GetRasterBand(1)

    bandOut1.WriteArray(data1.data_array, xOffset1, yOffset1)
    bandOut2.WriteArray(data2.data_array, xOffset2, yOffset2)

    bandOut1.FlushCache()  # 刷新磁盘
    bandOut2.FlushCache()  # 刷新磁盘

    # 设置输出图像的几何信息和投影信息
    geotransform = [min_X, pixel_width1, 0, max_Y, 0, pixel_height1]

    dsOut1.SetGeoTransform(geotransform)
    dsOut1.SetProjection(data1.proj)

    dsOut2.SetGeoTransform(geotransform)
    dsOut2.SetProjection(data2.proj)


def write(array, img, save_path):
    driver = gdal.GetDriverByName('GTiff')  # 数据类型必须有，因为要计算需要多大内存空间
    data = driver.Create(save_path, img.im_width, img.im_height, img.im_bands, img.datatype)
    data.SetGeoTransform(img.geotrans)  # 写入仿射变换参数
    data.SetProjection(img.proj)  # 写入投影

    if img.im_bands == 1:
        data.GetRasterBand(1).WriteArray(array)  # 写入数组数据
    else:
        for i in range(img.im_bands):
            data.GetRasterBand(i + 1).WriteArray(array[i])
    del data

if "__main__" == __name__:

    dataset1 = Dataset(r"D:\Pycharm_Project\0000000\Sigma1_VV.img")
    dataset2 = Dataset(r"D:\Pycharm_Project\0000000\Sigma0_VV.img")

    mosaic(dataset1, dataset2)

    del dataset1
    del dataset2

    dataco1 = Dataset(r"mosiac1.tif")
    dataco2 = Dataset(r"mosiac2.tif")

    dataco1_array = dataco1.data_array
    dataco2_array = dataco2.data_array

    del dataco2

    dataco_plus = dataco1_array + dataco2_array
    write(dataco_plus, dataco1, r"dataco_plus.tif")
    del dataco_plus

    dataco1_array[dataco1_array > dataco1_array.min()] = 1.0
    dataco2_array[dataco2_array > dataco2_array.min()] = 1.0

    dataco = dataco1_array + dataco2_array

    del dataco1_array
    del dataco2_array

    dataco[dataco == 2.0] = 0.5

    write(dataco, dataco1, r"dataco_multiply.tif")
    del dataco
    del dataco1

    dataco_plus = Dataset(r"dataco_plus.tif")
    dataco_multiply = Dataset(r"dataco_multiply.tif")

    dataco = dataco_multiply.data_array * dataco_plus.data_array

    del dataco_plus
    write(dataco, dataco_multiply, "mosiac.tif")
