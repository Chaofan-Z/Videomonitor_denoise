# -*- coding=utf8 -*-

import numpy as np
import cv2
import time
import socket
from threading import Thread
import tkinter as tk
import io
from PIL import Image
import socket
import threading
import videosocket
from config import *




def set_frame(frame_bytes):
    pil_bytes = io.BytesIO(frame_bytes)
    pil_image = Image.open(pil_bytes)
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    cv2.imshow("img", cv_image)

    c = cv2.waitKey(1)
    if 'q' == chr(c & 255):
        cv2.destroyAllWindows()
        return True
    return False


host = "127.0.0.1"
port = 50000

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
host = host
port = port
buffer_size = 2048

server.listen(10)
print("Server is ON. Waiting for clients to connect!!!")
client, client_addr = server.accept()
print("Client with address: %s:%s has connected" %(client_addr))

vsock = videosocket.VideoSocket(client)
while True:
    frame_bytes = vsock.vreceive()
    set_frame(frame_bytes)

# threading.Thread(target=self.handle_client, args=(client,)).start()



