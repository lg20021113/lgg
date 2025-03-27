#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                            QHBoxLayout, QWidget, QPushButton, QScrollArea,
                            QGridLayout, QFrame, QSplitter)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize

class NodeViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 加载数据
        self.load_data()
        
        # 设置窗口
        self.setWindowTitle("哈工深节点查看器")
        self.setGeometry(100, 100, 1200, 700)
        
        # 创建主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局 - 使用水平布局
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # 创建三个主要区域：左侧导航（后向）、中间内容、右侧导航（前向）
        # 左侧导航区域 - 后向节点
        self.left_nav_widget = QWidget()
        self.left_nav_layout = QVBoxLayout(self.left_nav_widget)
        
        self.backward_label = QLabel("后向节点")
        self.backward_label.setAlignment(Qt.AlignCenter)
        self.backward_label.setFont(QFont("SimSun", 14, QFont.Bold))
        self.backward_label.setStyleSheet("color: #333; margin: 10px;")
        self.left_nav_layout.addWidget(self.backward_label)
        
        self.backward_scroll = QScrollArea()
        self.backward_scroll.setWidgetResizable(True)
        self.backward_scroll.setFrameShape(QFrame.NoFrame)
        self.backward_buttons = QWidget()
        self.backward_layout = QVBoxLayout(self.backward_buttons)
        self.backward_layout.setSpacing(10)
        self.backward_layout.setAlignment(Qt.AlignTop)
        self.backward_scroll.setWidget(self.backward_buttons)
        self.left_nav_layout.addWidget(self.backward_scroll)
        
        # 中间内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # 文字内容区域（标题和描述）放在一个widget中
        self.text_widget = QWidget()
        self.text_layout = QVBoxLayout(self.text_widget)
        self.text_layout.setContentsMargins(0, 0, 0, 0)  # 减少边距
        
        # 节点标题
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("SimSun", 16, QFont.Bold))
        self.title_label.setStyleSheet("color: #333; margin: 5px;")  # 减少margin
        self.text_layout.addWidget(self.title_label)
        
        # 节点描述
        self.desc_scroll = QScrollArea()
        self.desc_scroll.setWidgetResizable(True)
        self.desc_scroll.setFrameShape(QFrame.NoFrame)
        self.desc_container = QWidget()  # 创建容器小部件
        self.desc_container_layout = QVBoxLayout(self.desc_container)
        self.desc_container_layout.setContentsMargins(5, 5, 5, 5)
        
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setFont(QFont("SimSun", 12))
        self.desc_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.desc_label.setStyleSheet("padding: 5px; background-color: #f8f8f8; border-radius: 5px;")
        self.desc_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许文本选择
        
        self.desc_container_layout.addWidget(self.desc_label)
        self.desc_scroll.setWidget(self.desc_container)
        
        # 设置最小高度确保内容可见，但保持较小的区域
        self.desc_scroll.setMinimumHeight(80)
        self.desc_scroll.setMaximumHeight(150)  # 稍微增加最大高度以确保能看到更多内容
        
        self.text_layout.addWidget(self.desc_scroll)
        
        self.content_layout.addWidget(self.text_widget)
        
        # 图片区域
        self.image_widget = QWidget()
        self.image_layout = QGridLayout(self.image_widget)
        self.image_layout.setSpacing(10)
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setFrameShape(QFrame.NoFrame)
        self.image_scroll.setWidget(self.image_widget)
        self.content_layout.addWidget(self.image_scroll)
        
        # 设置文字区域和图片区域的比例
        self.content_layout.setStretch(0, 1)  # 文字区域比例为1
        self.content_layout.setStretch(1, 4)  # 图片区域比例为4
        
        # 右侧导航区域 - 前向节点
        self.right_nav_widget = QWidget()
        self.right_nav_layout = QVBoxLayout(self.right_nav_widget)
        
        self.forward_label = QLabel("前向节点")
        self.forward_label.setAlignment(Qt.AlignCenter)
        self.forward_label.setFont(QFont("SimSun", 14, QFont.Bold))
        self.forward_label.setStyleSheet("color: #333; margin: 10px;")
        self.right_nav_layout.addWidget(self.forward_label)
        
        self.forward_scroll = QScrollArea()
        self.forward_scroll.setWidgetResizable(True)
        self.forward_scroll.setFrameShape(QFrame.NoFrame)
        self.forward_buttons = QWidget()
        self.forward_layout = QVBoxLayout(self.forward_buttons)
        self.forward_layout.setSpacing(10)
        self.forward_layout.setAlignment(Qt.AlignTop)
        self.forward_scroll.setWidget(self.forward_buttons)
        self.right_nav_layout.addWidget(self.forward_scroll)
        
        # 创建分割器，使区域大小可调整
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_nav_widget)
        self.splitter.addWidget(self.content_widget)
        self.splitter.addWidget(self.right_nav_widget)
        
        # 设置区域的初始宽度比例
        self.splitter.setSizes([200, 600, 200])
        
        # 添加到主布局
        self.main_layout.addWidget(self.splitter)
        
        # 设置样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-family: SimSun;
                font-size: 12px;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-family: SimSun;
            }
            QScrollArea {
                border: none;
            }
        """)
        
        # 显示初始节点
        self.current_node = list(self.nodes.keys())[0]  # 默认显示第一个节点
        self.display_node(self.current_node)
    
    def load_data(self):
        # 加载节点注释数据
        with open("node_annotations.json", "r", encoding="utf-8") as f:
            self.node_annotations = json.load(f)
        
        # 加载图结构
        self.nodes = {}
        self.parse_dot_file("hitsz_flow.dot")
    
    def parse_dot_file(self, filename):
        """解析DOT文件获取节点和边的信息"""
        with open(filename, "r", encoding="utf-8") as f:
            dot_content = f.read()
        
        # 提取节点定义
        node_pattern = r'(\w+)\s+\[label="([^"]+)"'
        for match in re.finditer(node_pattern, dot_content):
            node_id = match.group(1)
            node_label = match.group(2)
            if node_id not in self.nodes:
                self.nodes[node_id] = {
                    "id": node_id,
                    "label": node_label,
                    "forward": [],
                    "backward": []
                }
        
        # 提取边定义
        edge_pattern = r'(\w+)\s+->\s+(\w+)'
        for match in re.finditer(edge_pattern, dot_content):
            from_node = match.group(1)
            to_node = match.group(2)
            
            # 确保节点存在
            if from_node not in self.nodes:
                self.nodes[from_node] = {"id": from_node, "label": from_node, "forward": [], "backward": []}
            if to_node not in self.nodes:
                self.nodes[to_node] = {"id": to_node, "label": to_node, "forward": [], "backward": []}
            
            # 添加前向和后向链接
            if to_node not in self.nodes[from_node]["forward"]:
                self.nodes[from_node]["forward"].append(to_node)
            if from_node not in self.nodes[to_node]["backward"]:
                self.nodes[to_node]["backward"].append(from_node)
    
    def display_node(self, node_id):
        """显示指定节点的信息"""
        self.current_node = node_id
        node_info = self.nodes[node_id]
        
        # 设置标题
        self.title_label.setText(node_info["label"])
        
        # 设置描述
        description = ""
        if node_id in self.node_annotations:
            if "description" in self.node_annotations[node_id]:
                description = self.node_annotations[node_id]["description"]
        
        # 确保描述文本可见
        if not description:
            description = "暂无描述"
            
        self.desc_label.setText(description)
        # 更新滚动区域以适应新内容
        self.desc_scroll.ensureWidgetVisible(self.desc_label)
        
        # 清除现有图片
        for i in reversed(range(self.image_layout.count())): 
            self.image_layout.itemAt(i).widget().setParent(None)
        
        # 添加图片
        photo_paths = []
        if node_id in self.node_annotations and "photo_paths" in self.node_annotations[node_id]:
            photo_paths = self.node_annotations[node_id]["photo_paths"]
        
        if photo_paths:
            img_folder = "photo_HITSZ"
            for i, img_path in enumerate(photo_paths):
                full_path = os.path.join(img_folder, img_path)
                if os.path.exists(full_path):
                    img_label = QLabel()
                    pixmap = QPixmap(full_path)
                    
                    # 增大图片显示尺寸
                    max_width = 600  # 增加最大宽度
                    if pixmap.width() > max_width:
                        pixmap = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)
                    
                    img_label.setPixmap(pixmap)
                    img_label.setAlignment(Qt.AlignCenter)
                    
                    row = i // 2
                    col = i % 2
                    self.image_layout.addWidget(img_label, row, col)
        
        # 更新导航按钮
        self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """更新导航按钮"""
        # 清除现有按钮
        for i in reversed(range(self.forward_layout.count())): 
            self.forward_layout.itemAt(i).widget().setParent(None)
        
        for i in reversed(range(self.backward_layout.count())): 
            self.backward_layout.itemAt(i).widget().setParent(None)
        
        # 添加前向按钮
        if self.nodes[self.current_node]["forward"]:
            for next_node in self.nodes[self.current_node]["forward"]:
                btn = QPushButton(self.nodes[next_node]["label"])
                btn.setMinimumHeight(40)
                btn.clicked.connect(lambda _, n=next_node: self.display_node(n))
                self.forward_layout.addWidget(btn)
        else:
            no_forward = QLabel("无前向节点")
            no_forward.setAlignment(Qt.AlignCenter)
            no_forward.setStyleSheet("color: gray; padding: 10px;")
            self.forward_layout.addWidget(no_forward)
        
        # 添加后向按钮
        if self.nodes[self.current_node]["backward"]:
            for prev_node in self.nodes[self.current_node]["backward"]:
                btn = QPushButton(self.nodes[prev_node]["label"])
                btn.setMinimumHeight(40)
                btn.clicked.connect(lambda _, n=prev_node: self.display_node(n))
                self.backward_layout.addWidget(btn)
        else:
            no_backward = QLabel("无后向节点")
            no_backward.setAlignment(Qt.AlignCenter)
            no_backward.setStyleSheet("color: gray; padding: 10px;")
            self.backward_layout.addWidget(no_backward)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = NodeViewer()
    viewer.show()
    sys.exit(app.exec_()) 