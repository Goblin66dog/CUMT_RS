import os

import matplotlib.pyplot as plt
from osgeo import gdal
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import glob
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

    def process_img(self):
        # 读取遥感图像文件
        # pseudo_color_image = Dataset(r"D:\Pycharm_Project\data2\crop_fields_shp_by_ID_tif\Corn\24Winnipeg-20120617_phase_coherence_hh_vv.tif")
        pseudo_color_image = self.data_array
        # 创建伪彩色图像
        # 创建直方图
        fig = plt.figure(figsize=(20, 10)) # 创建一个画布
        ax0 = fig.add_axes([0.1, 0.55, 0.8, 0.4]) # 创建ax[0]，左下角坐标为(0.1, 0.5)，宽度为0.8，高度为0.4
        ax1 = fig.add_axes([0.335, 0.05, 0.335, 0.4]) # 创建ax[1]，左下角坐标为(0.1, 0.1)，宽度为0.8，高度为0.4

        ax0.imshow(pseudo_color_image, cmap='RdBu_r')
        ax0.set_title('Pseudo-Color Image')
        ax0.set_axis_off()
        divider = make_axes_locatable(ax0) # 创建一个分割器
        cax = divider.append_axes("right", size="5%", pad=0.05) # 在ax0的右边创建一个新的轴
        plt.colorbar(ax0.get_images()[0], cax=cax) # 在cax中绘制颜色条

        # 显示直方图
        ax1.hist(pseudo_color_image.flatten(), bins=500, color='blue', alpha=0.7)
        ax1.set_title('Histogram')
        ax1.set_xlabel('Pixel Value')
        ax1.set_ylabel('Frequency')
        mean = np.mean(pseudo_color_image) # 计算数据的平均值
        y_max = ax1.get_ylim()[1]

        ax1.axvline(mean, color='r', linestyle='--') # 在ax1上绘制一条红色的虚线，表示均值
        ax1.text(mean + 0.01, y_max*0.75, f'mean = {mean:.2f}', color='r')
        # plt.show()


        # # 保存伪彩色图像为PNG格式
        # pseudo_color_output = 'pseudo_color_image.png'  # 自定义输出文件名
        # plt.imsave(pseudo_color_output, pseudo_color_image)

        # 保存直方图为PNG格式
        # name_cut_num = self.file_path.rfind("\\")
        histogram_output = self.file_path[:-4] + '_hist_image.png'  # 自定义输出文件名
        histogram_output = histogram_output.replace("crop_fields_shp_by_ID_result", "crop_fields_shp_by_ID_hist_image")
        fig.savefig(histogram_output)
        plt.close()

def batch_process(pack_path):

    each_packer_list = glob.glob(pack_path+"\*")

    #make new packer
    save_packer_path = pack_path.replace("crop_fields_shp_by_ID_result", "crop_fields_shp_by_ID_hist_image")
    os.mkdir(save_packer_path)
    for each_packer_path in each_packer_list:

        #make new packer
        each_save_packer_path = each_packer_path.replace("crop_fields_shp_by_ID_result", "crop_fields_shp_by_ID_hist_image")
        os.mkdir(each_save_packer_path)

        each_file_list = glob.glob(each_packer_path + "\*")
        for each_file_path in each_file_list:
            Dataset(each_file_path).process_img()



if __name__ == "__main__":
    batch_process(r"Python_Programming&RS_Image_Processing_2\crop_fields_shp_by_ID_result")