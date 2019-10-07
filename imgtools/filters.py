# -- encoding: utf-8 --

import cv2
import numpy as np


def grayscale(input_img):
    # image = cv2.imread('C:/Users/N/Desktop/Test.jpg')
    gray_image = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    return gray_image

def write_image(img, filename):
    cv2.imwrite(filename, img)

def read_image(filename):
    img = cv2.imread(filename)
    return img

def wasted(input_image):
    # gray_image = grayscale(input_image)
    print(input_image.shape)
    height, width, colordim = input_image.shape
    watermark_height = height/4.0
    watermark_width = width
    darkened_image = change_hsv_range(input_image, 0, 0, width, height, 1.2, 0.6)
    watermark_y0 = int(height/2 - watermark_height/2)
    watermark_y1 = int(height/2 + watermark_height/2)
    watermarked_image = change_hsv_range(darkened_image, 0, watermark_y0, width, watermark_y1, 1.2, 0.3)

    thickness = int(round((height/314)*2))
    font_scale = (height/314)*1.2 # so when avatar is 314x314, you use the full 1.2 scale. anything different is scaled off of that
    font_size = cv2.getTextSize('WASTED', cv2.LINE_AA, font_scale, 2)
    # font_height, font_width, 
    cv2.putText(watermarked_image, 'WASTED', (int(width/2 - font_size[0][0]/2), int(height/2 + font_size[0][1]/2)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (200,200,200), thickness, cv2.LINE_AA)

    # average_color_per_row = np.average(input_image, 0)
    # average_color = np.average(average_color_per_row, 0)
    # average_color = np.uint8(average_color)
    # print(average_color)

    return watermarked_image


def rgb_to_hsv(input_image):
    # 方法2(OpenCVで実装)
    hsv = cv2.cvtColor(input_image, cv2.COLOR_BGR2HSV)
    return hsv

def change_hsv(input_image):
    img_hsv = cv2.cvtColor(input_image,cv2.COLOR_BGR2HSV)  # 色空間をBGRからHSVに変換
    s_magnification = 1.0  # 彩度(Saturation)の倍率
    v_magnification = 0.2  # 明度(Value)の倍率

    img_hsv[:,:,(1)] = img_hsv[:,:,(1)]*s_magnification  # 彩度の計算
    img_hsv[:,:,(2)] = img_hsv[:,:,(2)]*v_magnification  # 明度の計算
    img_bgr = cv2.cvtColor(img_hsv,cv2.COLOR_HSV2BGR)  # 色空間をHSVからBGRに変換

    return img_bgr

def change_hsv_range(input_image, x0, y0, x1, y1, s_magnification, v_magnification):
    img_hsv = cv2.cvtColor(input_image,cv2.COLOR_BGR2HSV)  # 色空間をBGRからHSVに変換
    # s_magnification = 1.0  # 彩度(Saturation)の倍率
    # v_magnification = 0.2  # 明度(Value)の倍率

    img_hsv[y0:y1,x0:x1,(1)] = img_hsv[y0:y1,x0:x1,(1)]*s_magnification  # 彩度の計算
    img_hsv[y0:y1,x0:x1,(2)] = img_hsv[y0:y1,x0:x1,(2)]*v_magnification  # 明度の計算
    img_bgr = cv2.cvtColor(img_hsv,cv2.COLOR_HSV2BGR)  # 色空間をHSVからBGRに変換

    return img_bgr
    