# -*- coding=utf8 -*-

import numpy as np
import cv2
import time
import socket
import tkinter as tk
import io
from PIL import Image
import socket
import threading
import videosocket
from config import *
import argparse
import videofeed
import videosocket
from matplotlib import pyplot as plt


FPS = 10.0
MAX_CILENT = 10

class Server(object):
    def __init__(self, host = '127.0.0.1', port = 50000, outpath = './out/output.mp4'):
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((str(host), int(port)))
        self.startframe = 0
        self.endframe = 0
        self.outpath = outpath


    @staticmethod
    def set_frame(frame_bytes, video_writer):
        pil_bytes = io.BytesIO(frame_bytes)
        pil_image = Image.open(pil_bytes)
        img = np.asarray(pil_image)
        cv_image = np.array(pil_image)
        video_writer.write(img)
        cv2.imshow("server-img", cv_image)
        c = cv2.waitKey(1)
        if c == ord('q'):
            cv2.destroyAllWindows()
            return True
        return False
    #TODO 客户端退出后服务器端需要检测并等待重连

    def run(self):
        self.server.listen(MAX_CILENT)
        print("Server is ON. Waiting for clients to connect!!!")
        client, client_addr = self.server.accept()
        print("Client with address: %s:%s has connected" %(client_addr))
        self.show_video(client)


    def show_video(self, client):
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        video_writer = cv2.VideoWriter()
        video_writer.open(self.outpath, fourcc, fps=FPS, frameSize=(640,480))
        vsock = videosocket.VideoSocket(client)
        while True:
            frame_bytes = vsock.vreceive()
            self.set_frame(frame_bytes, video_writer) #client端为什么不需要？

        video_writer.release()

    def splitvideo(self, inputvideo, st, ed, outputvideo):
        videoCapture = cv2.VideoCapture(inputvideo)  # 从文件读取视频
        FPS = videoCapture.get(cv2.CAP_PROP_FPS)  # 获取原视频的帧率
        SIZE = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))  # 获取原视频帧的大小
        print(FPS, SIZE)

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        video_writer = cv2.VideoWriter()
        video_writer.open(outputvideo, fourcc, fps=FPS, frameSize=SIZE)

        startframe = int(st * FPS)
        endframe = int(ed * FPS)
        print("startframe:", startframe, "endframe:", endframe)

        i = 0
        while True:
            success, frame = videoCapture.read()
            if success:
                i += 1
                if i >= startframe and i <= endframe:
                    video_writer.write(frame)
            if i > endframe or not success:
                break

        self.startframe = startframe
        self.endframe = endframe

        video_writer.release()

    def denoise(self, inputvideo, outputvideo):
        print("start to denoise")
        st = time.time()
        videoCapture = cv2.VideoCapture(inputvideo)  # 从文件读取视频
        FPS = videoCapture.get(cv2.CAP_PROP_FPS)  # 获取原视频的帧率
        SIZE = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))  # 获取原视频帧的大小

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        video_writer = cv2.VideoWriter()
        video_writer.open(outputvideo, fourcc, fps=FPS, frameSize=SIZE)

        while True:
            success, frame = videoCapture.read()
            if success:
                denoise_img = cv2.fastNlMeansDenoisingColored(frame, None, 5, 5, 7, 21)
                video_writer.write(denoise_img)
            else :
                break

        video_writer.release()
        ed = time.time()
        print("use ", ed - st, "s")

    def denoise2(self, inputvideo, outputvideo):
        print("start to denoise2")
        st = time.time()
        videoCapture = cv2.VideoCapture(inputvideo)  # 从文件读取视频
        FPS = videoCapture.get(cv2.CAP_PROP_FPS)  # 获取原视频的帧率
        SIZE = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))  # 获取原视频帧的大小

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        video_writer = cv2.VideoWriter()
        video_writer.open(outputvideo, fourcc, fps=FPS, frameSize=SIZE)

        img = []
        while True:
            success, frame = videoCapture.read()
            if success:
                img.append(frame)
            else:
                break

        dst = []
        for i in range(2, len(img) - 2):
            print(i)
            dst.append(cv2.fastNlMeansDenoisingMulti(img, i, 5, None, 4, 7, 35))

        for singleimg in dst:
            video_writer.write(singleimg)

        video_writer.release()
        ed = time.time()
        print("use ", ed - st, "s")

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='run the client.')
    # parser.add_argument('-i', '--host', type=str, default='127.0.0.1', help='the server ip')
    # parser.add_argument('-p', '--port', type=int, default='50000', help='the server port')
    # #TODO 根据路径创建output文件夹
    # parser.add_argument('-o', '--outpath', type=str, default='./out/output.mp4', help='the output file path')
    # args = parser.parse_args()
    # print('args:',args)

    host = '127.0.0.1'
    port = '50000'
    outpath = './out/output.mp4'
    server = Server(host, port, outpath)

    server.run()
    # server.splitvideo('./out/output.mp4', 10, 13, './outsplit/output.mp4')
    # # server.denoise('./outsplit/output.mp4', './outdenoise/output.mp4')
    # server.denoise2('./outsplit/output.mp4', './outdenoise/output2.mp4')

