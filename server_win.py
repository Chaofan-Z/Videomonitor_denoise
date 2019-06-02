from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mBox
from PIL import ImageTk

import os
import numpy as np
import cv2
import time
import shutil
import io
from PIL import Image, ImageDraw, ImageFont
import socket
import threading
from config import *
import videosocket
import datetime

FPS = 10
MAX_CILENT = 10

host = '127.0.0.1'
port = 50000
outpath = './out/output.mp4'


class Server_win():
    def __init__(self, mainwin, ConnectTime):
        # self.server = Server(host, port, outpath)
        # #self.server.run()
        self.file = StringVar()
        self.start_time = StringVar()
        self.end_time = StringVar()
        self.choice = IntVar()
        self.choice.set(0)
        self.ConnectTime = ConnectTime

        #main_frame = Frame(mainwin)
        #lbl = Label(main_frame, text="服务器正在监听："+str(host)+":"+str(port), relief='ridge')
        st_lbl = Label(mainwin, text="开始时间(s):")
        et_lbl = Label(mainwin, text="结束时间(s):")
        st_text_edit = Entry(mainwin, textvariable=self.start_time)
        st_text_edit.insert(0, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        et_text_edit = Entry(mainwin, textvariable=self.end_time)
        et_text_edit.insert(0, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

        file_text_edit = Entry(mainwin, textvariable=self.file)

        # sh = ttk.Separator(mainwin, orient=HORIZONTAL)
        # sh.grid(row=2, column=1, columnspan=3, sticky="we")

        select_button = Button(mainwin, text = "选择文件", command=self.select_btn_callback)
        split_button = Button(mainwin, text = "剪切", command=self.split_btn_callback)
        denoise_button = Button(mainwin, text= "降噪", command=lambda : self.denoise_btn_callback(self.file.get()))
        show_button = Button(mainwin, text="效果对比", command=showvideo)

        Radiobutton(mainwin, variable=self.choice, text='效果1', value=1).grid(row=6, column=0)
        Radiobutton(mainwin, variable=self.choice, text='效果2', value=2).grid(row=6, column=1)
        Radiobutton(mainwin, variable=self.choice, text='效果3', value=3).grid(row=6, column=2)

        #lbl.grid(row=4)
        se_line1 = ttk.Separator(mainwin, orient=HORIZONTAL)
        se_line1.grid(row=3, column=0, columnspan=4 ,sticky="we")
        # se_line2 = ttk.Separator(mainwin, orient=HORIZONTAL)
        # se_line2.grid(row=5, column=0, columnspan=4 ,sticky="we")

        st_lbl.grid(row=1, column=0)
        et_lbl.grid(row=2, column=0)
        st_text_edit.grid(row=1, column=1, columnspan=2)
        et_text_edit.grid(row=2, column=1, columnspan=2)
        split_button.grid(row=1, column=3, rowspan=2)
        select_button.grid(row=4, column=0)
        file_text_edit.grid(row=4, column=1, columnspan=2)
        denoise_button.grid(row=6, column=3)
        show_button.grid(row=7, column=3)

        image = Image.open('./tkvideo/test.jpeg')
        self.image = ImageTk.PhotoImage(image)
        self.panel2 = Label(image=self.image, relief='sunken')
        self.panel2.image = self.image
        self.panel2.grid(row=8, column=0, columnspan=4)

    def split_btn_callback(self):
        #TODO 输入合法性判断
        st = self.start_time.get()
        ed = self.end_time.get()

        a, b = Checktime(self.ConnectTime, st, ed)
        if a==-1 and b==-1:
            return
        thread1 = threading.Thread(target=split_video_online, args=(st,ed, ))
        thread1.start()
        # split_video_online(st, ed)
        # st, ed = convert(self.ConnectTime, self.start_time.get(), self.end_time.get())
        # if st == -1 and ed == -1:
        #     return
        # splitvideo_online(st, ed)

    def denoise_btn_callback(self, filename):
        if filename == '':
            mBox.showerror("错误", "请选择要降噪的文件！")
            return

        c = self.choice.get()
        if c == 0:
            mBox.showerror("错误", "请选择降噪方式")
            return
        elif c == 1:
            thread1 = threading.Thread(target=denoise1, args=(filename, './outdenoise/denoise1/denoised.mp4', ))
            thread1.start()

        elif c == 2:
            thread1 = threading.Thread(target=denoise2, args=(filename, './outdenoise/denoise2/denoised.mp4',))
            thread1.start()
        else:
            thread1 = threading.Thread(target=denoise3, args=(filename, './outdenoise/denoise3/denoised.mp4',))
            thread1.start()
        # print("denoise the video: ", filename.get())
        # denoise2(filename.get(), './outdenoise/output2.mp4')

    def select_btn_callback(self):
        filename = filedialog.askopenfilename(filetype=[("MP4", ".mp4"), ("AVI", ".avi")])
        self.file.set(filename)

def Checktime(ConnectTime, st, ed):
    # ConnectTime连接时间，server类内记录；
    # st, ed 从label中拿到时间字符串

    if st == '' or ed == '':
        mBox.showerror("错误", "时间不能为空！")
        return -1, -1

    # 不合法字符串 弹出窗口时间格式不对
    try:
        starttime = datetime.datetime.strptime(st,"%Y-%m-%d-%H-%M-%S")
        endtime = datetime.datetime.strptime(ed, "%Y-%m-%d-%H-%M-%S")
    except:
        mBox.showerror(message="时间格式不对")
        return -1, -1

    # 时间判断前后
    diff1 = diffseconds(starttime, endtime)
    if diff1 < 0:
        mBox.showerror(message="结束时间早于开始时间")
        return -1, -1

    diffst = diffseconds(ConnectTime, starttime)
    diffed = diffseconds(ConnectTime, endtime)
    if diffst < 0:
        mBox.showerror(message="剪切开始时间应当晚于录制开始时间！")
        return -1, -1
    if diffseconds(endtime, datetime.datetime.now()) < 0:
        mBox.showerror(message="剪切结束时间应当早于当前时间")
        return -1, -1

    return diffst, diffed


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
        self.ConnectTime = datetime.datetime.now()
        self.initialize()

    def initialize(self):
        shutil.rmtree('./frames')
        shutil.rmtree('./out')
        shutil.rmtree('./outsplit')
        shutil.rmtree('./outdenoise')

        os.mkdir('./frames')
        os.mkdir('./out')
        os.mkdir('./outsplit')
        os.mkdir('./outdenoise')
        os.mkdir('./outdenoise/denoise1')
        os.mkdir('./outdenoise/denoise2')
        os.mkdir('./outdenoise/denoise3')

    def run_gui(self):
        self.root = Tk()
        self.root.title('C/S监控系统服务器端')
        menubar = Menu(self.root)
        # #filemenu = Menu(menubar, tearoff=0)
        # menubar.add_cascade(label='设置', menu=filemenu)
        # filemenu.add_command(label='配置路径')
        # filemenu.add_separator()  # 添加一条分隔线
        # filemenu.add_command(label='退出', command=self.root.quit)  # 用tkinter里面自带的quit()函数

        editmenu = Menu(menubar, tearoff=0)
        # 将上面定义的空菜单命名为 Edit，放在菜单栏中，就是装入那个容器中
        menubar.add_cascade(label='关于', menu=editmenu)

        #self.root.geometry('800x500')
        self.root.config(menu=menubar)
        self.win = Server_win(self.root, self.ConnectTime)
        t_gui = threading.Thread(target=self.root.mainloop())
        t_gui.start()


    def set_frame(self, frame_bytes, video_writer, i):
        pil_bytes = io.BytesIO(frame_bytes)
        pil_image = Image.open(pil_bytes)
        font = ImageFont.truetype('C:/windows/fonts/Arial.ttf',size=20)
        draw = ImageDraw.Draw(pil_image)
        draw.text((0, 0), datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), (255, 255, 0), font=font)
        pil_image.save(os.path.join('./frames', '{}.jpg'.format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")+str(i))))

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
            self.ConnectTime = datetime.datetime.now()
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

    st = int(st);ed = int(ed)
    if st >= ed:
        mBox.showerror("错误", "起始时间应当小于结束时间！")
        return

    fps = 14
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

def split_video_online(st, ed, framepath='./frames', output_video='./outsplit/out.mp4'):
    print(st)
    frame_list = os.listdir(framepath)
    dir_list = sorted(frame_list, key=lambda x: os.path.getctime(os.path.join(framepath, x)))
    target_file = []
    st_index = 0
    ed_index = 0
    for filename in dir_list:
        if st in filename:
            st_index = dir_list.index(filename)
            break
    for filename in dir_list:
        if ed in filename:
            ed_index = dir_list.index(filename)

    target_file = dir_list[st_index:ed_index+1]

    print(target_file)
    fps = 15
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (640, 480))
    for i in target_file:
        img = cv2.imread(os.path.join(framepath, i)) # 使用opencv读取图像，直接返回numpy.ndarray 对象，通道顺序为BGR
        video.write(img)  #把图片写进视频

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
    mBox.showinfo("提示", "降噪完成，用时：{}s".format(ed - st))

def denoise1(inputvideo, outputvideo):
    kernel_size = (3, 3)
    sigma = 1.8

    print("start to GaussianBlur_denoise")
    st = time.time()
    videoCapture = cv2.VideoCapture(inputvideo)  # 从文件读取视频
    FPS = videoCapture.get(cv2.CAP_PROP_FPS)  # 获取原视频的帧率
    SIZE = (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))  # 获取原视频帧的大小
    print(FPS, SIZE)

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video_writer = cv2.VideoWriter()
    video_writer.open(outputvideo, fourcc, fps=FPS, frameSize=SIZE)

    while True:
        success, frame = videoCapture.read()
        if success:
            denoise_img = cv2.GaussianBlur(frame, kernel_size, sigma);
            # denoise_img = cv2.fastNlMeansDenoisingColored(frame, None, 5, 5, 7, 21)
            video_writer.write(denoise_img)
        else:
            break

    video_writer.release()
    ed = time.time()
    print("use ", ed - st, "s")
    mBox.showinfo("提示", "降噪完成，用时：{}s".format(ed - st))


def denoise3(inputvideo, outputvideo):
    print("start to denoisebest")
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


def diffseconds(st, ed):
    return (ed-st).days*86400 + (ed-st).seconds

def show(panel1, panel2):
    video1 = './outsplit/out.mp4'
    video2 = './outdenoise/denoise1/denoised.mp4'
    videoCapture1 = cv2.VideoCapture(video1)  # 从文件读取视频
    videoCapture2 = cv2.VideoCapture(video2)  # 从文件读取视频

    index = 0
    while True:
        index += 1
        success, frame = videoCapture1.read()
        success2, frame2 = videoCapture2.read()

        if success and success2:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            image = ImageTk.PhotoImage(image)
            panel1.configure(image=image)
            panel1.image = image

            frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            image2 = Image.fromarray(frame2)
            image2 = ImageTk.PhotoImage(image2)
            panel2.configure(image=image2)
            panel2.image = image2
        else:
            break

def showvideo():
    root2 = Toplevel()
    image = Image.open('./tkvideo/test.jpeg')
    image = ImageTk.PhotoImage(image)

    panel1 = Label(root2, image=image, relief="sunken")
    panel1.image = image
    panel1.grid(row=1, column=1)

    panel2 = Label(root2, image=image, relief="sunken")
    panel2.image = image
    panel2.grid(row=1, column=2)

    thread2 = threading.Thread(target=show,args=(panel1,panel2,))
    thread2.start()
    thread1 = threading.Thread(target=root2.mainloop)
    thread1.start()



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


