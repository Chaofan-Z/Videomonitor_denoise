from tkinter import filedialog
from tkinter import *
from tkinter import messagebox as mBox
from PIL import ImageTk

import os
import numpy as np
import cv2
import time
import socket
import io
from PIL import Image
import socket
import threading
import videosocket
from config import *
import videofeed
import videosocket

FPS = 10.0
MAX_CILENT = 10

#host = '172.19.219.51'
host = '172.20.10.8'
port = 50000
outpath = './out/output.mp4'


class Server_win():
    def __init__(self, mainwin, host, port):
        # self.server = Server(host, port, outpath)
        # #self.server.run()
        self.file = StringVar()
        self.start_time = StringVar()
        self.end_time = StringVar()

        #main_frame = Frame(mainwin)
        #lbl = Label(main_frame, text="服务器正在监听："+str(host)+":"+str(port), relief='ridge')
        st_lbl = Label(mainwin, text="开始时间(s)")
        et_lbl = Label(mainwin, text="结束时间(s)")
        st_text_edit = Entry(mainwin, textvariable=self.start_time)
        et_text_edit = Entry(mainwin, textvariable=self.end_time)
        file_text_edit = Entry(mainwin, textvariable=self.file)
        select_button = Button(mainwin, text = "选择文件", command=self.select_btn_callback, relief='ridge')
        split_button = Button(mainwin, text = "剪切", command=self.split_btn_callback, relief='ridge')
        denoise_button = Button(mainwin, text= "降噪", command=lambda : self.denoise_btn_callback(self.file), relief='ridge')

        #lbl.grid(row=4)
        st_lbl.grid(row=1, column=0)
        et_lbl.grid(row=2, column=0)
        st_text_edit.grid(row=1, column=1)
        et_text_edit.grid(row=2, column=1)
        split_button.grid(row=1, column=2, rowspan=2)
        select_button.grid(row=3, column=0)
        file_text_edit.grid(row=3, column=1)
        denoise_button.grid(row=3, column=2)

        image = Image.open('./tkvideo/test.jpeg')
        self.image = ImageTk.PhotoImage(image)
        self.panel2 = Label(image=self.image, relief='sunken')
        self.panel2.image = self.image
        self.panel2.grid(row=4, column=0, columnspan=3)


    def split_btn_callback(self):
        #TODO 输入合法性判断
        print("clip from {}s to {}s".format(self.start_time.get(), self.end_time.get()))
        #splitvideo(self.file.get(), int(self.start_time.get()), int(self.end_time.get()), './outsplit/splited.mp4')
        splitvideo_online(int(self.start_time.get()), int(self.end_time.get()))

    def denoise_btn_callback(self, filename):
        print("denoise the video: ", filename.get())
        denoise2(filename.get(), './outdenoise/output2.mp4')

    def select_btn_callback(self):
        filename = filedialog.askopenfilename(filetype=[("MP4", ".mp4"), ("AVI", ".avi")])
        self.file.set(filename)




def getframebyte(frame):
    pil_im = Image.fromarray(frame)
    b = io.BytesIO()
    pil_im.save(b, 'jpeg')
    im_bytes = b.getvalue()
    return im_bytes


class Server(object):
    def __init__(self, host='127.0.0.1', port=50000, outpath='./out/output.mp4'):
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.server.settimeout(10)
        self.server.bind((str(host), int(port)))
        self.startframe = 0
        self.endframe = 0
        self.outpath = outpath

    def run_gui(self):
        self.root = Tk()
        self.root.title('C/S监控系统')
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='设置', menu=filemenu)
        filemenu.add_command(label='配置路径')
        filemenu.add_separator()  # 添加一条分隔线
        filemenu.add_command(label='退出', command=self.root.quit)  # 用tkinter里面自带的quit()函数

        editmenu = Menu(menubar, tearoff=0)
        # 将上面定义的空菜单命名为 Edit，放在菜单栏中，就是装入那个容器中
        menubar.add_cascade(label='关于', menu=editmenu)

        #self.root.geometry('800x500')
        self.root.config(menu=menubar)
        self.win = Server_win(self.root, host, port)
        t_gui = threading.Thread(target=self.root.mainloop())
        t_gui.start()


    def set_frame(self, frame_bytes, video_writer, i):
        pil_bytes = io.BytesIO(frame_bytes)
        pil_image = Image.open(pil_bytes)
        pil_image.save(os.path.join('./frames', '{}.jpg'.format(str(i))))

        img = np.asarray(pil_image)
        # b, g, r = img.split()
        # im = Image.merge("RGB", (r, g, b))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        video_writer.write(img)

        # cv_image = np.array(pil_image)
        # cv2.imshow("server-img", cv_image)
        # image = Image.fromarray(np.array(pil_image))
        # pil_image = pil_image.convert("RGB")
        image = ImageTk.PhotoImage(pil_image)
        self.win.panel2.configure(image=image)
        self.win.panel2.image = image

        # c = cv2.waitKey(1)
        # if c == ord('q'):
        #     cv2.destroyAllWindows()
        #     return True
        return False



    def run(self):
        self.server.listen(MAX_CILENT)
        print("Server is ON. Waiting for clients to connect!!!")

        while True:
            client, client_addr = self.server.accept()
            print("Client with address: %s:%s has connected" % (client_addr))
            self.show_video(client)

    def show_video(self, client):
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        video_writer = cv2.VideoWriter()
        video_writer.open(self.outpath, fourcc, fps=FPS, frameSize=(640, 480))
        vsock = videosocket.VideoSocket(client)

        index = 0
        while True:
            index += 1
            frame_bytes, flag = vsock.vreceive(index)

            if frame_bytes == "request":
                self.new_window(vsock)
                print("接收到request，发送accpet")
                #vsock.vsend(bytes("accept", ENCODING))
                continue

            if not flag:
                #self.server.shutdown(socket.SHUT_RDWR)
                #client.close()
                video_writer.release()
                cv2.destroyAllWindows()
                print("client disconnect")
                image = ImageTk.PhotoImage(Image.open('./tkvideo/test.jpeg'))
                self.win.panel2.configure(image=image)
                self.win.panel2.image = image
                return False

            self.set_frame(frame_bytes, video_writer, index)  # client端为什么不需要？

        video_writer.release()
        return True


    def new_window(self, vsock):
        answer = mBox.askyesno("连接确认", "是否接受客户端请求？\n您的选择是：", parent=self.root)
        if answer == True:
            vsock.vsend(bytes("accept", ENCODING))
        else:
            vsock.vsend(bytes("refuse", ENCODING))

        # select_button1 = Button(win2, text="接受", command=lambda :self.button1(win2, vsock))
        # select_button1.grid(row=1)
        # select_button2 = Button(win2, text="拒绝", command=lambda :self.button2(win2, vsock))
        # select_button2.grid(row=2)
        # win2.mainloop()

    # def button1(self, win, vsock):
    #     vsock.vsend(bytes("accept", ENCODING))
    #     win.destroy()
    #
    # def button2(self, win, vsock):
    #     vsock.vsend(bytes("accept", ENCODING))
    #     win.destroy()

def splitvideo_online(st, ed, framepath='./frames', output_video='./outsplit/out.mp4'):
    if st >= ed:
        mBox.showerror("错误", "起始时间应当小于结束时间")
        return
    fps = 15
    start_frame = st*fps+2
    end_frame = ed*fps+2
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (640, 480))

    for i in range(start_frame, end_frame):
        img = cv2.imread(os.path.join(framepath,str(i)+'.jpg'))  # 使用opencv读取图像，直接返回numpy.ndarray 对象，通道顺序为BGR
        video.write(img)  # 把图片写进视频

    print("finish splitvideo_online")
    mBox.showinfo("提示", "视频{}s到{}s剪切完成！".format(st, ed))
    video.release()


def splitvideo(inputvideo, st, ed, outputvideo):
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

    #self.startframe = startframe
    #self.endframe = endframe

    video_writer.release()

def denoise(inputvideo, outputvideo):
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
        else:
            break

    video_writer.release()
    ed = time.time()
    print("use ", ed - st, "s")


def denoise2(inputvideo, outputvideo):
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
    mBox.showinfo("提示", "降噪完成，用时：{}s".format(ed-st))


# def func():
#     #host, port = server.get_addr()
#     mainwin = Tk()
#     mainwin.geometry('800x600')
#     server_win = Server_win(mainwin, host, port)
#     #mainwin.after(0, server_win.server.run())
#     mainwin.mainloop()

if __name__ == "__main__":

    #denoise2('./outsplit/splited.mp4', './outdenoise/output2.mp4')
    server = Server(host, port, outpath)
    t1 = threading.Thread(target=server.run)
    t1.start()

    t2= threading.Thread(target=server.run_gui)
    t2.start()

    # t2 = threading.Thread(target=func)
    # t2.start()
    # #TODO gui关闭后线程1也应当关闭
    # t2.join()


