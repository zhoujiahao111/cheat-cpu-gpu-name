from PyQt5.QtGui import QCursor

from Ui_tips import Ui_Dialog
from PyQt5.QtWidgets import  QDialog
from PyQt5.QtCore import Qt, QTimer

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


class TipUi(QDialog):
    def __init__(self, text: str, parent=None):
        # 设置ui
        super().__init__(parent)
        self.move(QCursor.pos().x(), QCursor.pos().y())
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # 设置定时器，用于动态调节窗口透明度
        self.timer = QTimer()

        # 显示的文本
        self.ui.pushButton.setText(text)
        # 设置隐藏标题栏、无边框、隐藏任务栏图标、始终置顶
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        # 设置窗口透明背景
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 窗口关闭自动退出，一定要加，否则无法退出
        self.setAttribute(Qt.WA_QuitOnClose, True)
        # 用来计数的参数
        self.windosAlpha = 0
        # 设置定时器25ms，1600ms记64个数
        self.timer.timeout.connect(self.hide_windows)
        self.timer.start(25)

    # 槽函数
    def hide_windows(self):
        self.timer.start(25)
        # 前750ms设置透明度不变，后850ms透明度线性变化
        if self.windosAlpha <= 30:
            self.setWindowOpacity(1.0)
        else:
            self.setWindowOpacity(1.882 - 0.0294 * self.windosAlpha)
        self.windosAlpha += 1
        # 差不多3秒自动退出
        if self.windosAlpha >= 63:
            self.close()



    @static_vars(tip=None)
    def show_tip(text):

        TipUi.show_tip.tip = TipUi(text)
        TipUi.show_tip.tip.show()
