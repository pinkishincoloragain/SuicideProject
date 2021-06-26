import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget,QMainWindow

# pyinstaller -w -F qtextbrowser_advanced.py

class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Name!')
        self.resize(500, 350)
        self.center()
        self.show()
        self.statusBar().showMessage('Ready')

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
