# import matplotlib.pyplot as plt
import glob
import os
from osgeo import gdal
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
        # 仿射变换参数
        self.geotrans = self.data.GetGeoTransform()
        self.min_x = self.geotrans[0]
        self.max_y = self.geotrans[3]
        self.pixel_width = self.geotrans[1]
        self.pixel_height = self.geotrans[5]
        self.max_x = self.min_x + (self.im_width * self.pixel_width)
        self.min_y = self.max_y + (self.im_height * self.pixel_height)
        # 读取图像栅格数据
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
    def extract_by_shp(shp_path, input_raster, output_path):
        # 利用gdal.Warp进行裁剪
        result = gdal.Warp(
            output_path,
            input_raster,
            format='GTiff',
            cutlineDSName=shp_path,  # 用于裁剪的矢量
            cropToCutline=True,  # 是否使用cutlineDSName的extent作为输出的界线
            dstNodata=0  # 输出数据的nodata值
        )
        return result
    @staticmethod
    def read_shp(file_path):
        file_path_list = glob.glob(file_path+'\*')
        file_list = []
        for path in file_path_list:
            shp_path = glob.glob(path+"\*.shp")
            file_list.append(shp_path)
        return file_list
    @staticmethod
    def read_img(file_path):
        file_path_list = glob.glob(file_path+'\*.tif')
        return file_path_list

def batch_process(img_path, shp_path):
    pack_path_old = "0"
    pack_path_old_2 = "9"
    round_num = 0
    for img in Dataset.read_img(img_path):
        data = gdal.Open(img)
        del_num = img.rfind("\\")
        img = img[del_num+1:]
        round_num += 1
        for files in Dataset.read_shp(shp_path):
            for shp in files:
                pack_path = shp.replace("crop_fields_shp_by_ID","crop_fields_shp_by_ID_result")
                del_num = pack_path.rfind("\\")
                pack_path = pack_path[:del_num]
                del_num = pack_path.rfind("\\")
                pack_path = pack_path[:del_num]

                if pack_path == pack_path_old:
                    pass
                else:
                    os.mkdir(pack_path)
                pack_path_old = pack_path
            for shp in files:
                if round_num == 1:
                    pack_path_2 = shp.replace("crop_fields_shp_by_ID","crop_fields_shp_by_ID_result")
                    del_num = pack_path_2.rfind("\\")
                    pack_path_2 = pack_path_2[:del_num]
                    if pack_path_2 == pack_path_old_2:
                        pass
                    else:
                        os.mkdir(pack_path_2)
                    pack_path_old_2 = pack_path_2
                Dataset.extract_by_shp(shp, data, shp.replace("crop_fields_shp_by_ID","crop_fields_shp_by_ID_result")[:-4]+img[:-4]+'.tif')
                # print(shp.replace("crop_fields_shp_by_ID","crop_fields_shp_by_ID_tif")[:-4]+img[:-4]+'.tif')

# data1 = Dataset(r"D:\Pycharm_Project\data2\Phase_difference_coherence\Winnipeg-20120617_phase_coherence_hh_vv.tif")
#
# print(Dataset.read_shp(r"D:\Pycharm_Project\data2\crop_fields_shp_by_ID"),
# Dataset.read_img(r"D:\Pycharm_Project\data2\Phase_difference_coherence"))
batch_process(r"Python_Programming&RS_Image_Processing_2\Phase_difference_coherence", r"Python_Programming&RS_Image_Processing_2\crop_fields_shp_by_ID")

