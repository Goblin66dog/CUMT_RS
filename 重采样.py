import cv2
from osgeo import gdal, gdalconst

from Dataset import Dataset
import math

def resampling(source_file, target_file):
    data = Dataset(source_file)
    dataset = gdal.Open(source_file)

    pixel_height = data.pixel_height / 360 * 2 * (2 * math.pi * 6371004)
    pixel_width = data.pixel_width / 360 * 2 * (2 * math.pi * 6371004)

    scale = pixel_width / 1000

    pixel_height_c = (-1000) *360/(2 * (2 * math.pi * 6371004))
    pixel_width_c = 1000 *360/(2 * (2 * math.pi * 6371004))
    geotrans = (data.geotrans[0], pixel_width_c, data.geotrans[2], data.geotrans[3], data.geotrans[4], pixel_height_c)

    cols = int(data.im_height * scale)
    rows = int(data.im_width * scale)

    cols_old = int(data.im_height * abs(pixel_height))
    rows_old = int(data.im_width *pixel_width)

    target = dataset.GetDriver().Create(target_file, xsize=rows, ysize=cols, bands=data.im_bands,eType=data.datatype)
    target.SetGeoTransform(geotrans)
    target.SetProjection(data.proj)

    data = dataset.GetRasterBand(1).ReadAsArray(buf_xsize=rows, buf_ysize=cols,
                                                    resample_alg=gdalconst.GRIORA_Average)
    out_band = target.GetRasterBand(1)

    out_band.WriteArray(data)  # 写入数据到新影像中

    out_band.FlushCache()
    out_band.ComputeBandStats(False)  # 计算统计信息

    del dataset
    del target
    del out_band

resampling(r"D:\Pycharm_Project\0000000\Sigma0_VV.img",r"D:\Pycharm_Project\0000000\00.img")
