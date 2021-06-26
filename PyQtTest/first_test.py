import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox

# C:\Users\S1807\venv\Lib\site-packages\PySide2 - 여기서 venv 등 파이썬 파일 내에 Qt designer.exe나 그런 게 있음.
# 저기서 빌드해도 되는데 아마 저거 쓰면서는 빌드 안 하고 그냥 있는 템플릿 쓰게 되지 않을까..

class MyApp(QWidget):

    def __init__(self): # 약간 자바랑 비슷함. 생성자.
        super().__init__()
        self.initUI() # UI 설정하는 거 추가 가능.

    def initUI(self):
        self.lbl = QLabel('Option1', self)
        self.lbl.move(50, 150)

        cb = QComboBox(self) # 콤보박스 생성
        cb.addItem('전처리') # 콤보박스 항목
        cb.addItem('몰랑')
        cb.addItem('다른 거')
        cb.addItem('다른 작업')
        cb.move(50, 50) # 위치 바꿀 수 있음.

        cb.activated[str].connect(self.onActivated) # activated 함수로 넘겨줌

        self.setWindowTitle('QComboBox') # 생성한 콤보박스 붙이기.
        self.setGeometry(300, 300, 300, 200) #
        self.show() # 보여줘!

    def onActivated(self, text):
        self.lbl.setText(f"{text}을(를) 실행합니다") # 이게 영향받는거. lbl 안에 text 바꿔 줌.
        self.lbl.adjustSize() # 이건 그냥 text size 맞게 adjustSize


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())

