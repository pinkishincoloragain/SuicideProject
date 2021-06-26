import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout


class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 세 개의 QLabel 인스턴트를 생성합니다.
        lbl_red = QLabel('Red')
        lbl_green = QLabel('Green')
        lbl_blue = QLabel('Blue')

        # 각 라벨의 스타일시트를 기술합니다.
        lbl_red.setStyleSheet("color: red;"
                              "border-style: solid;"
                              "border-width: 2px;"
                              "border-color: #FA8072;"
                              "border-radius: 3px")

        lbl_green.setStyleSheet("color: green;"
                                "background-color: #7FFFD4")

        lbl_blue.setStyleSheet("color: blue;"
                               "background-color: #87CEFA;"
                               "border-style: dashed;"
                               "border-width: 3px;"
                               "border-color: #1E90FF")

        # QVBoxLayout 인스턴트를 생성합니다: 이 인스턴트에 포함된 위젯들은 수직 정렬이 됩니다.
        vbox = QVBoxLayout()

        # 세 개의 라벨 인스터트를 vbox에 추가합니다.
        vbox.addWidget(lbl_red)
        vbox.addWidget(lbl_green)
        vbox.addWidget(lbl_blue)

        self.setLayout(vbox)

        self.setWindowTitle('StyleSheet')
        self.setGeometry(300, 300, 300, 200)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())