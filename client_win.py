import tkinter
from PIL import Image, ImageTk
import threading
import cv2
import socket
import io
from PIL import Image
import videosocket
from config import *
import time



def getframebyte(frame):
    pil_im = Image.fromarray(frame)
    b = io.BytesIO()
    pil_im.save(b, 'jpeg')
    im_bytes = b.getvalue()
    return im_bytes

class Client(object):
    def __init__(self, ip = "127.0.0.1", port = 50000):
        self.socket = socket.socket()
        self.socket.settimeout(10)
        # self.vsock = videosocket.VideoSocket(self.socket)
        self.server_ip = str(ip)
        self.server_port = int(port)
        self.stopEvent = None

        # frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)

        image = Image.open('./tkvideo/test.jpeg')
        # image = cv2.resize(image, (640, 480), interpolation=cv2.INTER_AREA)
        self.image = ImageTk.PhotoImage(image)
        self.panel2 = tkinter.Label(image=self.image, relief="sunken")
        self.panel2.image = self.image
        self.panel2.grid(row=3, column=1, columnspan=3, padx=3)


    def run(self):
        self.socket = socket.socket()
        self.socket.settimeout(5)
        self.vsock = videosocket.VideoSocket(self.socket)
        connection = -1
        try:
            print(self.server_ip, self.server_port)
            connection = self.socket.connect((self.server_ip, self.server_port))
        except socket.gaierror as e:
            print("%s" % e)
            if connection == -1:
                print("socket connect error")

        # 连接成功后先发送一个请求，成功后再继续
        # 客户端先发送-5，服务器端receive接收到-5后发送给客户端一个accept然后发送视频，
        # 这里应该持续receive等待几秒
        if connection != -1:
            print("socket connect successful")
            self.vsock.vsend(bytes("-5", ENCODING))

        result = ""
        while result != "accept":
            result, flag = self.vsock.vreceive()
            if result == "accept":
                print("connect successful to video call")
                break
            else:
                print(result)
                print("server refuse to video call")
                return

        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.videoLoop)
        thread.start()

    def videoLoop(self):
        cap = cv2.VideoCapture(0)
        panel = None

        while not self.stopEvent.is_set():
            sucess, frame = cap.read()
            frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            image = ImageTk.PhotoImage(image)
            # if panel is None:
            #     panel = tkinter.Label(image=image)
            #     panel.image = image
            #     panel.grid()
            #
            #     # otherwise, simply update the panel
            # else:
            self.panel2.configure(image=image)
            self.panel2.image = image

            frame = getframebyte(frame)
            try:
                self.vsock.vsend(frame)
            except:
                print("frame send error of ")

        self.socket.shutdown(socket.SHUT_RDWR)

        # panel.destroy()

        self.panel2.configure(image=self.image)
        self.panel2.image = self.image

        print(" I shutdown")
        cap.release()

    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()

        # self.root.quit()


global ip
global port

def connect():
    client.server_ip = ip_entry.get()
    client.server_port = int(port_entry.get())
    ip = ip_entry.get()
    port = int(port_entry.get())
    print(ip, port)

    client.run()
    # tkinter.messagebox.showinfo("infor", ip + " " + port)

def close():
    client.onClose()

if __name__ == '__main__':
    # 主窗口
    root = tkinter.Tk()
    root.title("C/S监控系统客户端")  #
    # root.geometry('600x450')
    root.resizable(0, 0)
    # 标题
    label2 = tkinter.Label(root, text = " IP ", relief="ridge", width=5, height=1, bg="beige")
    label3 = tkinter.Label(root, text = "端口", relief="ridge", width=5, height=1, bg="beige")

    #连接按钮
    button1 = tkinter.Button(root, text="连接", command=connect, width=8, height=2, relief="raised")

    #ip和port输入窗口
    ip_entry = tkinter.Entry(root, relief="ridge", width=20)
    # ip_entry.insert(0, "172.19.77.240")
    ip_entry.insert(0, "127.0.0.1")
    port_entry = tkinter.Entry(root, relief="ridge", width=20)
    port_entry.insert(0, "50000")

    ip = ip_entry.get()
    port = port_entry.get()
    client = Client(str(ip), int(port))

    label2.grid(row=1, column=1, sticky='e')
    label3.grid(row=2, column=1, sticky='e')
    ip_entry.grid(row=1, column=2)
    port_entry.grid(row=2, column=2)
    button1.grid(row=1, column=3, sticky='w')

    button2 = tkinter.Button(root, text="退出", command=client.onClose,  width=8, height=2, relief="raised")

    button2.grid(row=2, column=3, sticky='w')
    root.mainloop()

