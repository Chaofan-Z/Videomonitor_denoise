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

FPS = 15.0
MAX_CILENT = 10

class Server(object):
    def __init__(self, args):
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((args.host, args.port))

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
        video_writer.open(args.outpath, fourcc, fps=FPS, frameSize=(640,480))
        vsock = videosocket.VideoSocket(client)
        while True:
            frame_bytes = vsock.vreceive()
            self.set_frame(frame_bytes,video_writer) #client端为什么不需要？

        video_writer.release()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run the client.')
    parser.add_argument('-i', '--host', type=str, default='127.0.0.1', help='the server ip')
    parser.add_argument('-p', '--port', type=int, default='50000', help='the server port')
    parser.add_argument('-o', '--outpath', type=str, default='./out/output.mp4', help='the output file path')
    args = parser.parse_args()
    print('args:',args)
    server = Server(args)
    server.run()


