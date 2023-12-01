from osgeo import gdal, gdalconst
import os
import numpy as np
import glob
import math
from pyproj import Transformer
import pyproj

def resampling(source_file, target_file):
    """
    影像重采样
    :param source_file: 源文件
    :param target_file: 输出影像
    :param scale: 像元缩放比例
    :return:
    """
    dataset = gdal.Open(source_file, gdalconst.GA_ReadOnly)
    band_count = dataset.RasterCount
    cols = dataset.RasterXSize  # 列数
    rows = dataset.RasterYSize  # 行数

    geotrans = list(dataset.GetGeoTransform())
    print(geotrans)
    # 度转米
    """transformer = Transformer.from_crs('epsg:4326', 'epsg:32650')
    geotrans[3],geotrans[0] = transformer.transform(geotrans[3],geotrans[0])
          #geotrans[5]/360*2*(2*math.pi*6371004)
    """
    src_crs = pyproj.CRS('EPSG:4326')
    dst_crs = pyproj.CRS('EPSG:32650')
    # 定义转换器
    transformer = pyproj.Transformer.from_crs(src_crs, dst_crs)
    # 对每个点进行坐标转换
    geotrans[0], geotrans[3] = transformer.transform(geotrans[3], geotrans[0])
    origin_res=geotrans[1]
    geotrans[1] = 1000
    geotrans[5] = -1000
    scale=origin_res/360*2*(2*math.pi*6371004)/geotrans[1]
    cols = int(cols * scale)  # 计算新的行列数
    rows = int(rows * scale)
    print(geotrans)
    """
    geotrans[1] = geotrans[1] / scale  # 像元宽度变为原来的scale倍
    geotrans[5] = geotrans[5] / scale  # 像元高度变为原来的scale倍
    print(geotrans)
    """
    if os.path.exists(target_file) and os.path.isfile(target_file):  # 如果已存在同名影像
        os.remove(target_file)  # 则删除之

    band1 = dataset.GetRasterBand(1)
    data_type = band1.DataType
    target = dataset.GetDriver().Create(target_file, xsize=cols, ysize=rows, bands=band_count,
                                        eType=data_type)
    target.SetProjection("EPSG:32650")  # 设置投影坐标  :dataset.GetProjection()
    target.SetGeoTransform(geotrans)  # 设置地理变换参数
    total = band_count + 1
    for index in range(1, total):
        # 读取波段数据
        # print("正在写入" + str(index) + "波段")
        data = dataset.GetRasterBand(index).ReadAsArray(buf_xsize=cols, buf_ysize=rows,
                                                        resample_alg=gdalconst.GRIORA_Average)
        out_band = target.GetRasterBand(index)
        # out_band.SetNoDataValue(dataset.GetRasterBand(index).GetNoDataValue())
        out_band.WriteArray(data)  # 写入数据到新影像中
        out_band.FlushCache()
        out_band.ComputeBandStats(False)  # 计算统计信息
    # print("正在写入完成")
    del dataset
    del target


if __name__ == "__main__":
    sourcefile="C:\\Users\\19608\\Desktop\\S1A_IW_GRDH_1SDV_20220501T100418_20220501T100443_043016_0522D8_F84C_NR_Orb_Cal_Spk_TC\\Sigma0_VH.img"
    outfile="C:\\Users\\19608\\Desktop\\S1A_IW_GRDH_1SDV_20220501T100418_20220501T100443_043016_0522D8_F84C_NR_Orb_Cal_Spk_TC\\resampling.tiff"
    resampling(sourcefile,outfile)
