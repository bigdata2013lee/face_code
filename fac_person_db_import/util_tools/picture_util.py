#_*_coding:utf-8 _*_

from PIL import Image
import colorsys


#图片是否彩色
def picture_is_colour(img):
    if img == type(str):
        img = Image.open(img)

    # 颜色模式转换，以便输出rgb颜色值
    img = img.convert('RGBA')

    # 生成缩略图，减少计算量，减小cpu压力
    img.thumbnail((200, 200))

    max_score = -1
    is_colour = '3'
    for count, (r, g, b, a) in img.getcolors(img.size[0] * img.size[1]):
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
            if(r==g and g==b):
                #not color
                is_colour = '0'
            else:
                #color
                is_colour = '1'
    return is_colour

