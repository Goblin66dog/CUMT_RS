import cv2
from Dataset import Dataset
import numpy as np


if __name__ == "__main__":
    dataset1 = Dataset(r"C:\Users\Vegio-admin\Pictures\0.png")
    img = dataset1.data_array
    img = np.transpose(img, (1,2,0))
    b, g, r = cv2.split(img)
    img = cv2.merge([r,g,b])
    cv2.imshow("a",img)
    cv2.waitKey(0)