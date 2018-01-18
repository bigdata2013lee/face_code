# _*_coding:utf-8 _*_
# !/usr/bin/env python

from PIL import Image
import colorsys


# 图片尺寸
def getPictureSize(file_path):
    try:
        img = Image.open(file_path)
        return img.size[0] + '*' + img.size[1]
    except Exception, e:
        x = 178
        y = 220
        return str(x) + '*' + str(y)


# 图片分辨率
def getPictureDpi(file_path):
    try:
        img = Image.open(file_path)
        return img.info["DPI"]
    except Exception, e:
        # print e
        x = 96
        y = 96
        return str(x) + '*' + str(y)


# 图片像素
def getPicturePixels(file_path):
    try:
        img = Image.open(file_path)
        return img
    except Exception, e:
        # print e
        x = 96
        y = 96
        return str(x) + '*' + str(y)


# 图片是否彩色
def pictureIsColor(input_path):
    # 颜色模式转换，以便输出rgb颜色值
    try:
        image = Image.open(input_path)
        image = image.convert('RGBA')

        # 生成缩略图，减少计算量，减小cpu压力
        image.thumbnail((200, 200))

        max_score = None
        dominant_color = None

        for count, (r, g, b, a) in image.getcolors(image.size[0] * image.size[1]):
            # 跳过纯黑色
            if a == 0:
                continue

            saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]

            y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)

            y = (y - 16.0) / (235 - 16)

            # 忽略高亮色
            if y > 0.9:
                continue

            # Calculate the score, preferring highly saturated colors.
            # Add 0.1 to the saturation so we don't completely ignore grayscale
            # colors by multiplying the count by zero, but still give them a low
            # weight.
            score = (saturation + 0.1) * count

            if score > max_score:
                max_score = score
                dominant_color = (r, g, b)
                if (r == g and g == b):
                    # not color
                    iscolour = 0
                else:
                    # color
                    iscolour = 1
    except Exception as error:
        print "图片读取出错", error
        iscolour = 3
    return iscolour


# 图片是否有网纹
def pictureIsReticulate(file_path):
    pass


# 图片是否清晰
def pictureIsClear(file_path):
    pass
