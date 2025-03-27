from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys


class HTMLViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('HTML查看器')
        self.setGeometry(100, 100, 800, 600)

        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建加载按钮
        self.load_button = QPushButton('加载HTML文件')
        self.load_button.clicked.connect(self.load_html_file)
        layout.addWidget(self.load_button)

        # 创建网页视图组件
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

    def load_html_file(self):
        # 打开文件选择对话框
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择HTML文件",
            "",
            "HTML文件 (*.html);;所有文件 (*.*)"
        )

        if file_name:
            # 将文件路径转换为URL并加载
            url = QUrl.fromLocalFile(file_name)
            self.web_view.setUrl(url)

def main():
    app = QApplication(sys.argv)
    viewer = HTMLViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    print("跑起来了")