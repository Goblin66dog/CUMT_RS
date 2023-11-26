from osgeo import gdal
import cv2
import numpy as np


# Dataset类:
class Dataset:
    # 初始化（图像栅格、图像shape、投影、栅格数据类型）
    def __init__(self, file_path):
        # 读取影像
        self.file_path = file_path
        self.data = gdal.Open(self.file_path)
        # 读取图像行数
        self.im_width = self.data.RasterXSize
        # 读取图像列数
        self.im_height = self.data.RasterYSize
        # 地图投影信息
        self.proj = self.data.GetProjection()
        # 仿射变换参数(geotrans[1]:x方向空间分辨率；geotrans[5]:y方向空间分辨率（为负）)
        self.geotrans = self.data.GetGeoTransform()
        self.min_x = self.geotrans[0]
        self.max_y = self.geotrans[3]
        self.pixel_width = self.geotrans[1]
        self.pixel_height = self.geotrans[5]
        self.max_x = self.min_x + (self.im_width * self.pixel_width)
        self.min_y = self.max_y + (self.im_height * self.pixel_height)
        self.data_array = self.data.ReadAsArray(0, 0, self.im_width, self.im_height)

        # 图像维度/波段
        if len(self.data_array.shape) == 2:
            self.im_bands = 1
        else:
            self.im_bands = self.data_array.shape[0]
        # 判断栅格数据的类型
        if 'int8' in self.data_array.dtype.name:
            self.datatype = gdal.GDT_Byte
        elif 'int16' in self.data_array.dtype.name:
            self.datatype = gdal.GDT_UInt16
        else:
            self.datatype = gdal.GDT_Float32

        # 释放内存，如果不释放，在arcgis，envi中打开该图像时会显示文件被占用
        del self.data

    @staticmethod
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

        #获取输出图像的行&列
        min_X = min(min_x1, min_x2)
        max_X = max(max_x1, max_x2)
        min_Y = min(min_y1, min_y2)
        max_Y = max(max_y1, max_y2)

        #todo:行列是否需要int?
        #镶嵌时两张图像的空间分辨率相同
        image_out_cols = int((max_X - min_X) / pixel_width1)
        image_out_rows = int((max_Y - min_Y) / abs(pixel_height1))

        # 计算图1左上角的偏移值（在输出图像中）
        xOffset1 = int((min_x1 - min_X) / pixel_width1)
        yOffset1 = int((max_y1 - max_Y) / pixel_height1)

        # 计算图2左上角的偏移值（在输出图像中）
        xOffset2 = int((min_x2 - min_X) / pixel_width2)
        yOffset2 = int((max_y2 - max_Y) / pixel_height2)

        #todo:1是bands，默认
        # 创建一个输出图像
        driver = gdal.GetDriverByName("GTiff")
        dsOut1 = driver.Create('mosiac1.tif', image_out_cols, image_out_rows, 1, data1.datatype)
        dsOut2 = driver.Create('mosiac2.tif', image_out_cols, image_out_rows, 1, data1.datatype)

        bandOut1 = dsOut1.GetRasterBand(1)
        bandOut2 = dsOut2.GetRasterBand(1)

        bandOut1.WriteArray(data1.data_array, xOffset1, yOffset1)
        bandOut2.WriteArray(data2.data_array, xOffset2, yOffset2)
        bandOut1.FlushCache()  # 刷新磁盘
        bandOut2.FlushCache()  # 刷新磁盘

        stats = bandOut1.GetStatistics(0, 1)  # 第一个参数是1的话，是基于金字塔统计，第二个
        stats = bandOut2.GetStatistics(0, 1)

        # 第二个参数是1的话：整幅图像重度，不需要统计
        # 设置输出图像的几何信息和投影信息
        geotransform = [min_X, pixel_width1, 0, max_Y, 0, pixel_height1]

        dsOut1.SetGeoTransform(geotransform)
        dsOut1.SetProjection(data1.proj)

        dsOut2.SetGeoTransform(geotransform)
        dsOut2.SetProjection(data2.proj)
        # 建立输出图像的金字塔
        gdal.SetConfigOption('HFA_USE_RRD', 'YES')
        dsOut1.BuildOverviews(overviewlist=[2, 4, 8, 16])  # 4层
        dsOut2.BuildOverviews(overviewlist=[2, 4, 8, 16])  # 4层


    @staticmethod
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

    dataset1 = Dataset(r"D:\Pycharm Project\0000000\Sigma1_VV.img")
    dataset2 = Dataset(r"D:\Pycharm Project\0000000\Sigma0_VV.img")

    Dataset.mosaic(dataset1, dataset2)

    del dataset1
    del dataset2

    dataco1 = Dataset(r"mosiac1.tif")
    dataco2 = Dataset(r"mosiac2.tif")

    dataco1_array = dataco1.data_array
    dataco2_array = dataco2.data_array

    del dataco2

    dataco_plus = dataco1_array + dataco2_array
    Dataset.write(dataco_plus, dataco1, r"dataco_plus.tif")
    del dataco_plus

    dataco1_array[dataco1_array > dataco1_array.min()] = 1.0
    dataco2_array[dataco2_array > dataco2_array.min()] = 1.0

    dataco = dataco1_array + dataco2_array

    del dataco1_array
    del dataco2_array

    dataco[dataco == 2.0] = 0.5

    Dataset.write(dataco, dataco1, r"dataco_multiply.tif")
    del dataco
    del dataco1

    dataco_plus = Dataset(r"dataco_plus.tif")
    dataco_multiply = Dataset(r"dataco_multiply.tif")

    dataco = dataco_multiply.data_array * dataco_plus.data_array

    del dataco_plus
    Dataset.write(dataco, dataco_multiply, "mosiac.tif")
