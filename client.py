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

class Client(object):
    def __init__(self,args):
        self.socket = socket.socket()
        self.socket.settimeout(1)
        self.vsock = videosocket.VideoSocket(self.socket)
        self.server_ip = args.ip
        self.server_port = args.port

    def getframebyte(self, frame):
        pil_im = Image.fromarray(frame)
        b = io.BytesIO()
        pil_im.save(b, 'jpeg')
        im_bytes = b.getvalue()
        return im_bytes

    def run(self):
        try :
            self.socket.connect((self.server_ip, self.server_port))
        except :
            print("socket connect error")

        cap = cv2.VideoCapture(0)
        while True:
            #从摄像头读取图片
            sucess, img=cap.read()
            img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)
            cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame = self.getframebyte(img)

            # 传输给server降噪后的
            denoise_img = cv2.fastNlMeansDenoisingColored(img)
            denosie_frame = self.getframebyte(denoise_img)

            #TODO 以下代码有时会出错
            try:
                self.vsock.vsend(denosie_frame)
            except:
                print("frame send error")

            cv2.imshow("client-img",img)

            #保持画面的持续。
            k=cv2.waitKey(1)
            if k == 27:
                #通过esc键退出摄像
                self.socket.shutdown(socket.SHUT_RDWR)
                cv2.destroyAllWindows()
                break
            # elif k==ord("s"):
            #     #通过s键保存图片，并退出。
            #     cv2.imwrite("image2.jpg",img)
            #     cv2.destroyAllWindows()
            #     break
        cap.release()
        #关闭摄像头

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run the client.')
    parser.add_argument('-i', '--ip', type=str, default='127.0.0.1', help='the server ip')
    parser.add_argument('-p', '--port', type=int, default='50000', help='the server port')
    args = parser.parse_args()
    print('args:',args)
    client = Client(args)
    client.run()