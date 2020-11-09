# -*- coding:UTF-8 -*-
# AUTHOR: youzhiyuan

# DESCRIPTION:  聊天室客户端
import threading
from socket import socket, AF_INET, SOCK_DGRAM
import json
import os
import sys
from PySide2 import QtCore, QtWidgets, QtGui

class RecvThread(QtCore.QThread):
    signal = QtCore.Signal(object)

    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self):
        while True:
            msg, addr = self.sock.recvfrom(8192)
            msg = str(msg, encoding="utf-8")
            self.signal.emit(msg)


class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("login")
        self.resize(280, 230)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint,QtCore.Qt.ApplicationModal)

        self.layout = QtWidgets.QVBoxLayout()
        self.label1 = QtWidgets.QLabel("username")
        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText("Enter Username Here")
        self.username.move(20, 20)
        self.label2 = QtWidgets.QLabel("password")
        self.passwd = QtWidgets.QLineEdit()
        self.passwd.setPlaceholderText("Enter Password Here")
        self.passwd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwd.move(20, 20)
        self.button = QtWidgets.QPushButton("login")
        self.button.clicked.connect(self.login)
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.username)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.passwd)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.show()
        app.exec_()

    def login(self):
        self.close()




class Client(QtWidgets.QWidget):
    def __init__(self,localAddr,serverAddr):
        '''
        初始化
        '''
        super().__init__()
        # QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Python-ChatRoom")
        self.resize(800, 600)
        self.layout = QtWidgets.QVBoxLayout()
        self.mainEdit = QtWidgets.QTextEdit()
        self.mainEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.inputEdit = QtWidgets.QTextEdit()
        self.sendButton = QtWidgets.QPushButton("send")
        self.layout.addWidget(self.mainEdit)
        self.layout.addWidget(self.inputEdit)
        self.layout.addWidget(self.sendButton)
        self.setLayout(self.layout)

        self.addr = localAddr
        self.serverAddr = serverAddr
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(localAddr)
        self.auth = {}
        self.queue = []
        self.loginWindow = LoginWindow()
        # self.loginWindow.show()


        # login.close()
        self.start()

    def login(self):
        '''
        用户登陆
        '''
        name = self.loginWindow.username.text()
        self.setWindowTitle(name + " - Python-ChatRoom")
        pwd = self.loginWindow.passwd.text()
        self.auth = {
            "name": name,
            "pwd": pwd
        }

        msg = {}
        msg["auth"] = self.auth
        msg["type"] = "notice"
        msg = json.dumps(msg)
        msg = bytes(msg, encoding='utf-8')
        self.sock.sendto(msg, self.serverAddr)
        msg, addr = self.sock.recvfrom(8192)
        msg = str(msg, encoding="utf-8")
        loginStatus = QtWidgets.QMessageBox()
        loginStatus.setText(msg)
        loginStatus.exec_()
        if msg == "Login failed":
            # self.loginWindow = LoginWindow()
            # self.start()
            sys.exit()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def recieve(self, msg):
        '''
        接收消息
        '''
        # self.queue.append(msg)
        # self.chatWindow()
        self.mainEdit.append(f'{msg} \n')

    # def chatWindow(self):
    #     '''
    #     聊天界面
    #     '''
    #     self.mainEdit.clear()
    #     if len(self.queue)>=6:
    #         for msg in self.queue[-6:]:
    #             self.mainEdit.append(f'{msg} \n')
    #     else:
    #         for msg in self.queue:
    #             self.mainEdit.append(f'{msg} \n')


    def pack(self):
        '''
        消息处理
        '''
        msg = {}
        msg["auth"] = self.auth
        modes = ["broadcast", "solo", "list all users"]
        mode, ok = QtWidgets.QInputDialog().getItem(self, "mode", "mode: ", modes, 0, False)
        if ok:
            if mode == "solo":
                msg["type"] = "solo"
                who, ok = QtWidgets.QInputDialog().getText(self, "to who", "to: ", QtWidgets.QLineEdit.Normal, None)
                if ok:
                    msg["toWho"] = who
                else:
                    msg["type"] = ""
                if self.inputEdit.toPlainText() == "":
                    msg["type"] = ""
                    warning = QtWidgets.QMessageBox()
                    warning.setText("say something")
                    warning.exec_()
                else:
                    msg["text"] = self.inputEdit.toPlainText()
            elif mode == "broadcast":
                msg["type"] = "broadcast"
                if self.inputEdit.toPlainText() == "":
                    msg["type"] = ""
                    warning = QtWidgets.QMessageBox()
                    warning.setText("say something")
                    warning.exec_()
                else:
                    msg["text"] = self.inputEdit.toPlainText()
            elif mode == "list all users":
                msg["type"] = "show"
        msg = json.dumps(msg)
        msg = bytes(msg, encoding='utf-8')
        self.inputEdit.clear()
        return msg

    def send(self):
        msg = self.pack()
        self.sock.sendto(msg, self.serverAddr)

    def start(self):
        # t = threading.Thread(target=self.recieve,args=(self.addr,))
        # t.setDaemon(True)
        # t.start()

        self.login()
        self.recvThread = RecvThread(self.sock)
        self.recvThread.signal.connect(self.recieve)
        self.recvThread.start()
        self.sendButton.clicked.connect(self.send)



if __name__ == "__main__":
    localHost = sys.argv[1]
    localPort = int(sys.argv[2])
    localAddr = (localHost,int(localPort))

    romoteHost = sys.argv[3]
    romotePort = sys.argv[4]
    romoteAddr = (romoteHost,int(romotePort))
    
    app = QtWidgets.QApplication([]) 
    window = Client(localAddr,romoteAddr)
    sys.exit(app.exec_())



