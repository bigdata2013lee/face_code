# -*- coding: utf-8 -*-
"""
    Cropman Library - Cropper
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements face-ware image cropping functions.

    :copyright: (c) 2017 by Qinglong Li.
    :license: .
"""

import sys
from detector import Detector

# ----------------------------------------------------------------------------

class Cropper(object):
    """Cropper"""
    def __init__(self):
        super(Cropper, self).__init__()
        self.detector  = Detector()

    @staticmethod
    def _bounding_rect(faces):
        top,    left  =  sys.maxint,  sys.maxint
        bottom, right = -sys.maxint, -sys.maxint
        for (x, y, w, h) in faces:
            if x < left:
                left = x
            if x+w > right:
                right = x+w
            if y < top:
                top = y
            if y+h > bottom:
                bottom = y+h
        return top, left, bottom, right

    def better_location(self, left, top, right, bottom):
        target_center_x = (left + right) / 2
        target_center_y = (top + bottom) / 2
        target_left = int(round(target_center_x - (target_center_x - left) * 1.3))
        target_right = int(round(target_center_x + (right - target_center_x) * 1.3))
        target_top = int(round(target_center_y - (target_center_y - top) * 1.7))
        target_bottom = int(round(target_center_y + (bottom - target_center_y) * 1.5))
        if (target_left <= 0) or (target_right <= 0) or (target_top <= 0) or (target_bottom <= 0) :
            target_left = left
            target_right = right
            target_top = top
            target_bottom = bottom
        return target_left, target_right, target_top, target_bottom

    def crop_original(self, img):
        original_height, original_width = img.shape[:2]
        faces = self.detector.detect_faces(img)
        if len(faces) == 0:  # no detected faces
            print("---- not detect!")
            return
        else:
            top, left, bottom, right = self._bounding_rect(faces)
            target_left, target_right, target_top, target_bottom = self.better_location(left, top, right, bottom)
            return img[target_top:target_bottom, target_left:target_right]






# ----------------------------------------------------------------------------
