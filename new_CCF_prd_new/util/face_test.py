#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Console
    ~~~~~~~~~~~~~~~

    Face-aware image cropper application (console interface).

    :copyright: (c) 2017 by Qinglong Li.

    Usage:
      image_crop_landmark.py <input-dir> <target-dir>
      image_crop_landmark.py -d <input-dir> <target-dir>
      image_crop_landmark.py -o <input-dir> <target-dir>
      image_crop_landmark.py -m <input-dir> <target-dir>
      image_crop_landmark.py -m -d <input-dir> <target-dir>
      image_crop_landmark.py -m -o <input-dir> <target-dir>

    Options:
      -h --help     Show this screen.
      --version     Show version.
      -m            landmarks input-dir with dlib first and then opencv.
      -d            use dlib only.
      -o            use opencv only.
"""

from cropman.cropper import Cropper
import cv2
import dlib
from PIL import Image, ImageDraw
import face_recognition
import os,os.path
import datetime
import traceback

# Get user supplied values
OPENCV_DEFAULT_CONFIG_FILE = os.path.join(
    os.path.split(os.path.realpath(__file__))[0],
    'cropman/config/haarcascade_frontalface_default.xml'
    )

#globle cropper
cropper = Cropper()

def get_target_filename(src_parent, src_filename, input_dir, target_dir):
    ''' get file name '''
    input_filename = os.path.join(src_parent, src_filename)
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #print time_str + ", the input file:" + input_filename
    target_filename = input_filename.replace(input_dir, target_dir)
    target_filedir = os.path.dirname(target_filename)
    if not os.path.exists(target_filedir):
        os.makedirs(target_filedir)
    return input_filename, target_filename

def better_location(left, right, top, bottom):
    target_center_x = (left + right) / 2
    target_center_y = (top + bottom) / 2
    target_left = int(round(target_center_x - (target_center_x - left) * 1.3))
    target_right = int(round(target_center_x + (right - target_center_x) * 1.3))
    target_top = int(round(target_center_y - (target_center_y - top) * 1.7))
    target_bottom = int(round(target_center_y + (bottom - target_center_y) * 1.5))
    #target_top = int(round(target_center_y - (target_center_y - top) * 2))
    #target_bottom = int(round(target_center_y + (bottom - target_center_y) * 2))

    if (target_left <= 0) :
        target_left = 0

    if (target_top <= 0) :
        target_top = 0

    if (target_right <= 0):
        target_right = right

    if (target_bottom <= 0):
        target_bottom = bottom

    return target_left, target_right, target_top, target_bottom

def dlib_landmark_pic(input_filename, target_filename):
    #open image
    try:
        image = face_recognition.load_image_file(input_filename)
    except:
        #print "load file failed:" + input_filename
        traceback.print_exc()
        return False

    if image is None:
        #print "read file None." + input_filename
        return False

    # Find all facial features in all the faces in the image
    face_landmarks_list = face_recognition.face_landmarks(image)
    #print("I found {} face(s) in this photograph.".format(len(face_landmarks_list)))
    if (len(face_landmarks_list) == 0):
        #print 'mark list is 0:' + input_filename
        return False

    pil_image = Image.fromarray(image)
    pil_image.save(target_filename)
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #print time_str + ',dlib landmarks Done. target file:%s' % target_filename

    return True


def landmarks_pic(filename, target_dir, alg_type=0):  # alg_type 0:all 1:dlib 2:opencv
    #print("landmarks..." + str(alg_type) + "\n")

    # dlib landmark
    dlib_marked = False
    if (alg_type != 2):
        return dlib_landmark_pic(filename, target_dir)


#angle pic
def rotatepic(input_dir,tmp_dir,angle):
    img = cv2.imread(input_dir)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows, cols, clolor = img.shape
    # 这里的第一个参数为旋转中心，第二个为旋转角度，第三个为旋转后的缩放因子
    # 可以通过设置旋转中心，缩放因子，以及窗口大小来防止旋转后超出边界的问题
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    # 第三个参数是输出图像的尺寸中心
    dst = cv2.warpAffine(img, M, (2 * cols, 2 * rows))
    target_image = cropper.crop_original(dst)
    cv2.imwrite(tmp_dir, target_image)
    return tmp_dir

def rotatepic_pil(input_dir,tmp_dir,angle):
     pil_im = Image.open(input_dir)
     pil_im = pil_im.rotate(angle)
     pil_im.save(tmp_dir)

def crop_pic(input_dir, target_dir, alg_type):
    #print("----- crop...")

    for parent,dirnames,filenames in os.walk(input_dir):
        for filename in filenames:
            #get target filepath
            input_filename, target_filename = get_target_filename(parent, filename, input_dir, target_dir)

            #dlib
            have_face = False
            if (alg_type != 2):
                have_face = dlib_crop(input_filename, target_filename)

            #opencv
            if ((not have_face) and (alg_type != 1)):
                opencv_crop(input_filename, target_filename)

def dlib_crop(input_filename, target_filename):

    ''' get file name '''
    # Load the jpg file into a numpy array
    try:
        input_image = face_recognition.load_image_file(input_filename)
    except:
        #print "load file failed:" + input_filename
        traceback.print_exc()
        return False

    if input_image is None:
        #print "read file None." + input_filename
        return False

    # Find all the faces in the image
    face_locations = face_recognition.face_locations(input_image)
    if face_locations is None:
        #print 'location failed:' + input_filename
        return False

    #print("I found {} face(s) in this photograph.".format(len(face_locations)))
    if (len(face_locations) == 0):
        #print 'locations is 0==================:' + input_filename
        return False

    face_num = 0
    for face_location in face_locations:
        face_num += 1

        # Print the location of each face in this image
        top, right, bottom, left = face_location
        #print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        # You can access the actual face itself like this:
        target_left, target_right, target_top, target_bottom = better_location(left, right, top, bottom)
        #print("face new location Top: {}, Left: {}, Bottom: {}, Right: {}".format(target_top, target_left, target_bottom, target_right))

        face_image = input_image[target_top:target_bottom, target_left:target_right]
        pil_image = Image.fromarray(face_image)

        file_flex = '.' + target_filename.split('.')[-1]
        #new_target_filename = target_filename.replace(file_flex , '_' + str(face_num) + file_flex)
        new_target_filename = target_filename
        #print new_target_filename
        pil_image.save(new_target_filename)
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print time_str + ", dlib crop Done, target file:" + new_target_filename

    return True

def opencv_crop(input_filename, target_filename):
    ''' get file name '''
    input_image = cv2.imread(input_filename)
    if input_image is None:
        #print "crop read file None:" + input_filename
        return False

    target_image = cropper.crop_original(input_image)
    if target_image is None:
        #print 'Cropping failed:' + input_filename
        return False
    else:
        file_flex = '.' + target_filename.split('.')[-1]
        new_target_filename = target_filename.replace(file_flex , '_0' + file_flex)
        cv2.imwrite(new_target_filename, target_image)
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print time_str + ',opencv crop Done. %s' % new_target_filename
        return True

def dlib_exists_face(input_filename):

    ''' get file name '''
    # Load the jpg file into a numpy array
    try:
        input_image = face_recognition.load_image_file(input_filename)
    except:
        #print "load file failed:" + input_filename
        traceback.print_exc()
        return False

    if input_image is None:
        #print "read file None." + input_filename
        return False

    # Find all the faces in the image
    face_locations = face_recognition.face_locations(input_image)
    if face_locations is None:
        #print 'location failed:' + input_filename
        return False

    #print("I found {} face(s) in this photograph.".format(len(face_locations)))
    if (len(face_locations) == 0):
        #print 'locations is 0==================:' + input_filename
        return False

    return True
'''
if __name__ == '__main__':

    input_dir = '/home/mjq998/Pictures/1/7777.jpg'
    target_dir = '/home/mjq998/Pictures/2/7777.jpg'
    tmp_dir = '/home/mjq998/Pictures/tmp/7777.jpg'
    alg_type = 1
    scan = 90
    # 使用dlib自带的frontal_face_detector作为我们的特征提取器
    detector = dlib.get_frontal_face_detector()
    for i in range(0, 359,scan):
        #print input_dir
        if(dlib_crop(input_dir, target_dir)):
            print "3121"
            break
        else:
            print "4444"
            target_image = rotatepic_pil(input_dir,tmp_dir,scan)
            input_dir = tmp_dir
'''


