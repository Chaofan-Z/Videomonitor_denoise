# -*- coding=utf8 -*-
import numpy as np
import cv2
import time
import socket
import tkinter as tk
import io
from PIL import Image

import videosocket
#from videofeed import VideoFeed
from config import *
import argparse


class Spliter(object):
    def __init__(self, videopath, st, ed, outputpath):
        self.videopath = videopath
        self.st = st
        self.ed = ed
        self.outputpath = outputpath

    def splitvideo(self):
        videoCapture = cv2.VideoCapture(self.videopath)  # 从文件读取视频
        fps = videoCapture.get(cv2.CAP_PROP_FPS)  # 获取原视频的帧率
        size = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))  # 获取原视频帧的大小

        print(fps, size)


if __name__ == '__main__':
    a = Spliter("./out/test.mov", 0, 5, "./process/output.mp4")
    a.splitvideo()