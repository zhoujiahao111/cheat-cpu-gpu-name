from PyQt5.Qt import QLabel, QPushButton,QLineEdit,QApplication,QMessageBox
from PyQt5.QtGui import QIcon, QFont,  QPixmap
from PyQt5.QtWidgets import  QWidget,  QGridLayout
from reg import *
from PopupAnimation import *
import random
import sys
import os
import pywintypes
import win32api

class window(QWidget):

    def __init__(self):
        super().__init__()
        self.init_setting()
        self.main_ui()


    def init_setting(self):
        self.mainLayout = QGridLayout(self)
        self.setWindowIcon(QIcon('image/icon.jpg'))
        self.configDict = loadFile()

        if isAdmin():
            QMessageBox.question(self, '权限不足', '请以管理员身份运行程序',
                                         QMessageBox.Yes)
            sys.exit()

        self.show_cat = ShowCat()


    def main_ui(self):

        #cpu
        cpulabel = QLabel("   cpu:",self)
        cpulabel.setFont(QFont("Roman times", 12))

        self.cpuLineEdit = QLineEdit(self)

        self.cpuname = searchReg(1)
        if 'cpu' in self.configDict and self.configDict['cpu'] == self.cpuname:
            self.cpuLineEdit.setText(self.configDict['cpu'])

        else:
            self.cpuLineEdit.setText(self.cpuname)

        self.cpuButton = QPushButton("确认",self)

        self.cpuButton.clicked.connect(lambda : self.showinfo(self.cpuLineEdit.text(),0))


        #显卡
        self.gpuNameDict = searchReg(0)

        flag = True
        if len(self.gpuNameDict) == 0:
            for i in self.configDict:
                if 'gpu' in i:
                    flag = False
                    break

            if flag:
                self.messageDialog("错误","无法查询到显卡名称")
            else:
                num = 0
                for i in self.configDict:
                    if 'gpu' in i:
                        self.gpuNameDict[num] = self.configDict[i]
                        num += 1

        elif len(self.gpuNameDict) > 1:
            numlist = list(self.gpuNameDict.keys())
            numlist.sort(reverse=True)

            tDict = {}
            num = 0
            for i in numlist:
                tDict[num] = self.gpuNameDict[i]
                num += 1

            self.gpuNameDict = tDict


        self.gpulabelList = [QLabel(self) for _ in  range(1,len(self.gpuNameDict)+1) ]
        self.gpuEditlList = [QLineEdit(self) for _ in  range(1,len(self.gpuNameDict)+1) ]
        self.gpuButtonList = [QPushButton("确认", self) for _ in  range(1,len(self.gpuNameDict)+1) ]


        for item in range(0,len(self.gpuNameDict)):
            self.gpulabelList[item].setText("  gpu" +str(item)+":")
            self.gpulabelList[item].setFont(QFont("Roman times", 12))

            if 'gpu'+ str(item) in self.configDict:
                self.gpuEditlList[item].setText(self.configDict['gpu'+ str(item)].split('&&&&&')[0])
            else:
                self.gpuEditlList[item].setText(self.gpuNameDict[item].split('&&&&&')[0])


            self.gpuButtonList[item].setObjectName(str(item)) #设置一个id
            self.gpuButtonList[item].clicked.connect(lambda :
                                                     self.showinfo(self.gpuEditlList[int(self.sender().objectName())].text(),
                                                               1,
                                                                item=int(self.sender().objectName()),
                                                               location=self.gpuNameDict[int(self.sender().objectName())].split('&&&&&')[-1]))

            #self.sender()  表示点击的按钮本身
            #self.sender().objectName()就是获取按钮的id, id和循环的item一样,也就是其它列表的索引

            self.mainLayout.addWidget(self.gpulabelList[item], item+2, 1)
            self.mainLayout.addWidget(self.gpuEditlList[item], item+2, 2, 1, 3)
            self.mainLayout.addWidget(self.gpuButtonList[item], item+2, 5)


        self.infoLabel = QLabel(self) #信息输出


        #底部确认取消等
        self.allOk = QPushButton("全部确认",self)
        self.allOk.clicked.connect(self.allOkCheat)

        self.reset = QPushButton("取消修改",self)
        self.reset.clicked.connect(self.resetCheat)

        self.cancel = QPushButton("退出软件",self)
        self.cancel.clicked.connect(sys.exit)

        self.resetAll = QPushButton("还原默认",self)
        self.resetAll.clicked.connect(self.resetAllCheat)

        self.lookCat = QPushButton("看看猫猫",self)

        self.lookCat.clicked.connect(lambda : self.show_cat.show())


        self.mainLayout.addWidget(cpulabel,1,1)
        self.mainLayout.addWidget(self.cpuLineEdit,1,2,1,3)
        self.mainLayout.addWidget(self.cpuButton,1,5)



        self.mainLayout.addWidget(self.infoLabel,8,1)

        self.mainLayout.addWidget(self.allOk, 10, 1)
        self.mainLayout.addWidget(self.reset,10,2)
        self.mainLayout.addWidget(self.cancel,10,3)
        self.mainLayout.addWidget(self.resetAll,10,4)
        self.mainLayout.addWidget(self.lookCat,10,5)


    def allOkCheat(self):
        try:
            self.configDict['cpu'] = self.cpuLineEdit.text()
            alter_reg(self.cpuLineEdit.text(), 0)
        except:
            TipUi.show_tip("cpu设置失败")

        try:
            for item in range(0, len(self.gpuNameDict)):
                self.configDict['gpu'+str(item)] = self.gpuEditlList[item].text() + '&&&&&' + self.gpuNameDict[item].split('&&&&&')[-1]
                alter_reg(self.gpuEditlList[item].text(), 1, self.gpuNameDict[item].split('&&&&&')[-1])
        except:
            TipUi.show_tip("gpu设置失败")
            return
        saveFile(self.configDict)
        TipUi.show_tip("全部修改完成")

    def resetCheat(self):
        self.cpuLineEdit.setText(self.cpuname)

        for item in range(0, len(self.gpuNameDict)):
            self.gpuEditlList[item].setText(self.gpuNameDict[item].split('&&&&&')[0])

        TipUi.show_tip("重置完毕")

    def resetAllCheat(self):
        computerInfo = get_real_name(self.gpuNameDict)

        try:
            self.cpuLineEdit.setText(computerInfo['cpu'])
            self.configDict['cpu'] = computerInfo['cpu']
            alter_reg(computerInfo['cpu'].split('&&&&&')[0], 0)
        except:
            TipUi.show_tip("cpu还原失败")

        try:
            for i in range(len(computerInfo)-1):
                self.configDict['gpu'+str(i)] = computerInfo[i]
                self.gpuEditlList[i].setText(computerInfo[i].split('&&&&&')[0])
                alter_reg(computerInfo[i].split('&&&&&')[0], 1,self.gpuNameDict[i].split('&&&&&')[-1])
        except:
            TipUi.show_tip("gpu还原失败")

        saveFile(self.configDict)


    def showinfo(self,name,mode,location = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",item=0):
        if mode: #1是gpu
            self.configDict['gpu'+str(item)] = name + '&&&&&' +location
        else:
            self.configDict['cpu'] = name

        saveFile(self.configDict)
        text = alter_reg(name,mode,location)
        TipUi.show_tip(text)

    # 警告框
    def messageDialog(self,title,msg):
        msg_box = QMessageBox(QMessageBox.Warning, title,msg)
        msg_box.exec_()

    def closeEvent(self,event):
        sys.exit()



class ShowCat(QWidget):
    def __init__(self):
        super().__init__()

        num = str(random.randint(1,len(os.listdir("image"))-1))
        self.setWindowTitle("第{}个猫猫".format(num))
        self.desktop = QApplication.desktop()

        pic_show_label = QLabel(self)
        pic_show_label.resize(self.desktop.width() // 2, self.desktop.height() // 2)

        image = QPixmap("image/image_cat_{}.jpg".format(num))

        pic_show_label.setPixmap(image)
        pic_show_label.setScaledContents(True)

    def closeEvent(self,event):
        window.show_cat = ShowCat()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = window()
    window.setWindowTitle("改名字  (ฅ>ω<*ฅ)")
    window.show()
    sys.exit(app.exec_())
