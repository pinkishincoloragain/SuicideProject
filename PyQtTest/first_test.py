import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox

# C:\Users\S1807\venv\Lib\site-packages\PySide2


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.lbl = QLabel('Option1', self)
        self.lbl.move(50, 150)

        cb = QComboBox(self)
        cb.addItem('전처리')
        cb.addItem('몰랑')
        cb.addItem('다른 거')
        cb.addItem('다른 작업')
        cb.move(50, 50)

        cb.activated[str].connect(self.onActivated)

        self.setWindowTitle('QComboBox')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def onActivated(self, text):
        self.lbl.setText(f"{text}을(를) 실행합니다")
        self.lbl.adjustSize()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())

