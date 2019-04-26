# -*- coding=utf8 -*-

import numpy as np
import cv2
import time
import socket
from threading import Thread
import tkinter as tk
import io
from PIL import Image

import videosocket
from videofeed import VideoFeed
from config import *

def rescale_frame(frame, percent = 75):
    scale_percent = percent
    width = (int)(frame.shape[1] * scale_percent / 100)
    height = (int)(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)


def getframebyte(frame):
    pil_im = Image.fromarray(frame)
    b = io.BytesIO()
    pil_im.save(b, 'jpeg')
    im_bytes = b.getvalue()
    return im_bytes

socket = socket.socket()
socket.settimeout(1)
buffer_size = 2048
vsock = videosocket.VideoSocket(socket)

server_port = 50000
server_ip = "172.19.174.14"
server_ip = "127.0.0.1"


try :
    socket.connect((server_ip, server_port))
except :
    print("socket connect error")


cap = cv2.VideoCapture(0)
while True:
    #从摄像头读取图片
    sucess,img=cap.read()
    img = rescale_frame(img,percent = 50)
    cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    frame = getframebyte(img)
    try:
        vsock.vsend(frame)
    except:
        a = 1
    cv2.imwrite("image2.jpg",img)

    cv2.imshow("img",img)
    #保持画面的持续。
    k=cv2.waitKey(1)
    if k == 27:
        #通过esc键退出摄像
        cv2.destroyAllWindows()
        break
    elif k==ord("s"):
        #通过s键保存图片，并退出。
        cv2.imwrite("image2.jpg",img)
        cv2.destroyAllWindows()
        break


#关闭摄像头
