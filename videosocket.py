import socket
from config import *

class VideoSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self,host,port):
        self.sock.connect((host,port))

    def vsend(self, framestring):
        length = len(framestring)
        lengthstr = str(length).zfill(8)

        lensent = 0
        # send length of the image first
        while lensent < 18 :
            msg = bytes(lengthstr[lensent:], ENCODING)
            sent = self.sock.send(msg)
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            lensent += sent

        # send actual data
        totalsent = 0
        while totalsent < length :
            sent = self.sock.send(framestring[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            totalsent += sent

    def vreceive(self, index=0):
        # first length of the image is received
        lenArray = []
        flag = True
        lenrec = 0
        # print("receive:", str(index))
        while lenrec < 18:
            chunk = self.sock.recv(18 - lenrec)
            if not chunk:
                print("chunk is none\n")
                flag = False
                return "-1", False
                # raise RuntimeError("Socket connection broken")
            lenArray.append(chunk.decode(ENCODING))
            lenrec += len(chunk)
        lengthstr = ''.join(lenArray)
        # print("receive:", str(index))

        length = int(lengthstr)

        # now we know length of image array
        # receive the image
        totrec = 0
        imgArray = []
        while totrec < length:
            chunk = self.sock.recv(length - totrec)
            if not chunk:
                # print("chunk2 is none\n")
                flag = False
                return "-1", False

                # raise RuntimeError("Socket connection broken")
            imgArray.append(chunk)
            totrec += len(chunk)
        frame = b''.join(imgArray)
        # print("receive:", str(index))

        try:
            # check if the other party has quit
            if frame.decode(ENCODING) == "-1":
                print("1\n")
                return "1", False
            if frame.decode(ENCODING) == "-2":
                print("2\n")
                return "2", False
            if frame.decode(ENCODING) == "-5":
                print("client request video call")
                return "request", True
            if frame.decode(ENCODING) == "accept":
                print("server send accept to client")
                return "accept", True
        except:
            pass

        return frame, flag