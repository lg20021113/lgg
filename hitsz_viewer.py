#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import networkx as nx
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QStackedWidget, QListWidgetItem, QScrollArea, 
                            QGridLayout, QGroupBox, QSplitter, QLineEdit, QTextEdit,
                            QFileDialog, QMessageBox, QDialog)
from PyQt5.QtGui import QColor, QFont, QPalette, QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, QSize

# 定义节点类型和颜色映射
NODE_TYPES = {
    "时间": {"color": "lightgreen", "shape": "oval", "nodes": []},
    "地点": {"color": "lightyellow", "shape": "hexagon", "nodes": []},
    "机构/组织": {"color": "pink", "shape": "box", "nodes": []},
    "人物": {"color": "lightcyan", "shape": "ellipse", "nodes": []},
    "教育理念": {"color": "lightsalmon", "shape": "diamond", "nodes": []},
    "课程": {"color": "lavender", "shape": "box", "nodes": []},
    "产品/技术": {"color": "lightgray", "shape": "box", "nodes": []},
    "事件": {"color": "white", "shape": "oval", "nodes": []},
    "成就": {"color": "gold", "shape": "star", "nodes": []},
    "启发/反思": {"color": "white", "fontcolor": "red", "shape": "plaintext", "nodes": []}
}

# 节点到类型的映射
NODE_TO_TYPE = {}

# 构建图结构
def build_graph_from_dot(dot_file_path):
    try:
        G = nx.DiGraph()
        
        # 读取DOT文件
        with open(dot_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析节点
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # 跳过注释和不相关行
            if line.startswith('//') or not line or line.startswith('digraph') or line.startswith('}') or line.startswith('rankdir') or line.startswith('node') or line.startswith('edge'):
                continue
            
            # 解析节点定义行
            if '->' not in line and '[' in line and ']' in line:
                node_id = line.split('[')[0].strip()
                attrs = line.split('[')[1].split(']')[0]
                
                # 提取label
                label = ""
                if 'label=' in attrs:
                    if 'label="' in attrs:
                        label = attrs.split('label="')[1].split('"')[0]
                    else:
                        label = attrs.split('label=')[1].split(',')[0].strip('"')
                
                # 提取形状和颜色
                shape = "box"  # 默认形状
                if 'shape=' in attrs:
                    shape = attrs.split('shape=')[1].split(',')[0].strip('"')
                    if shape.endswith(']'):
                        shape = shape[:-1]

                color = "lightblue"  # 默认颜色
                if 'fillcolor=' in attrs:
                    color = attrs.split('fillcolor=')[1].split(',')[0].strip('"')
                    if color.endswith(']'):
                        color = color[:-1]
                
                fontcolor = "black"  # 默认字体颜色
                if 'fontcolor=' in attrs:
                    fontcolor = attrs.split('fontcolor=')[1].split(',')[0].strip('"')
                    if fontcolor.endswith(']'):
                        fontcolor = fontcolor[:-1]
                
                # 添加节点到图中
                G.add_node(node_id, label=label, shape=shape, color=color, fontcolor=fontcolor)
                
                # 根据节点命名前缀推断类型
                node_type = None
                if node_id.startswith("t"):
                    node_type = "时间"
                elif node_id.startswith("place_"):
                    node_type = "地点"
                elif node_id.startswith("org_"):
                    node_type = "机构/组织"
                elif node_id.startswith("person_"):
                    node_type = "人物"
                elif node_id.startswith("concept_"):
                    node_type = "教育理念"
                elif node_id.startswith("course_"):
                    node_type = "课程"
                elif node_id.startswith("tech_"):
                    node_type = "产品/技术"
                elif node_id.startswith("event_"):
                    node_type = "事件"
                elif node_id == "achievement":
                    node_type = "成就"
                elif node_id.startswith("lesson"):
                    node_type = "启发/反思"
                
                if node_type:
                    NODE_TYPES[node_type]["nodes"].append((node_id, label))
                    NODE_TO_TYPE[node_id] = node_type
            
            # 解析边定义行
            if '->' in line:
                parts = line.split('->')
                source = parts[0].strip()
                if '[' in parts[1]:
                    target = parts[1].split('[')[0].strip()
                    attrs = parts[1].split('[')[1].split(']')[0]
                    
                    # 提取边的label
                    edge_label = ""
                    if 'label=' in attrs:
                        if 'label="' in attrs:
                            edge_label = attrs.split('label="')[1].split('"')[0]
                        else:
                            edge_label = attrs.split('label=')[1].split(',')[0].strip('"')
                    
                    G.add_edge(source, target, label=edge_label)
                else:
                    target = parts[1].strip()
                    if target.endswith(';'):
                        target = target[:-1]
                    G.add_edge(source, target, label="")
        
        return G
    except Exception as e:
        print(f"构建图时出错: {e}")
        return None

class PhotoPreviewDialog(QDialog):
    """照片预览对话框"""
    def __init__(self, photo_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("照片预览")
        self.resize(800, 600)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # 创建照片容器
        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        
        # 创建照片标签
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.photo_label)
        
        # 加载照片
        self.load_photo(photo_path)
        
        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
    
    def load_photo(self, photo_path):
        """加载照片到标签"""
        if os.path.exists(photo_path):
            try:
                pixmap = QPixmap(photo_path)
                
                # 检查是否加载成功
                if pixmap.isNull():
                    self.photo_label.setText(f"无法加载照片: {photo_path}")
                    return
                
                # 调整图片大小，保持纵横比
                pixmap = pixmap.scaled(780, 520, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # 显示照片
                self.photo_label.setPixmap(pixmap)
                
                # 调整标签大小以适应照片
                self.photo_label.setMinimumSize(pixmap.width(), pixmap.height())
            except Exception as e:
                self.photo_label.setText(f"预览照片出错: {str(e)}")
        else:
            self.photo_label.setText(f"找不到照片: {photo_path}")

class HITSZFlowViewer(QMainWindow):
    def __init__(self, graph):
        super().__init__()
        
        self.graph = graph
        self.current_node = None
        self.annotations_file = self.get_annotations_file_path()
        
        # 加载已有的标注信息
        self.load_annotations()
        
        self.init_ui()
    
    def get_annotations_file_path(self):
        """获取标注文件的保存路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "node_annotations.json")
    
    def load_annotations(self):
        """从JSON文件加载标注信息"""
        if os.path.exists(self.annotations_file):
            try:
                with open(self.annotations_file, 'r', encoding='utf-8') as f:
                    annotations = json.load(f)
                
                # 将标注信息应用到图中的节点
                for node_id, node_data in annotations.items():
                    if node_id in self.graph.nodes:
                        for key, value in node_data.items():
                            self.graph.nodes[node_id][key] = value
                
                print(f"成功从 {self.annotations_file} 加载标注信息")
            except Exception as e:
                print(f"加载标注信息时出错: {e}")
    
    def save_annotations(self):
        """将所有节点的标注信息保存到JSON文件"""
        try:
            # 创建一个字典保存所有节点的标注
            annotations = {}
            
            # 遍历图中的所有节点
            for node_id in self.graph.nodes:
                node_data = {}
                # 只保存标注相关的属性
                if 'description' in self.graph.nodes[node_id]:
                    node_data['description'] = self.graph.nodes[node_id]['description']
                if 'photo_paths' in self.graph.nodes[node_id]:
                    node_data['photo_paths'] = self.graph.nodes[node_id]['photo_paths']
                if 'photo_path' in self.graph.nodes[node_id]:
                    node_data['photo_path'] = self.graph.nodes[node_id]['photo_path']
                
                # 如果节点有标注数据，添加到字典中
                if node_data:
                    annotations[node_id] = node_data
            
            # 写入JSON文件
            with open(self.annotations_file, 'w', encoding='utf-8') as f:
                json.dump(annotations, f, ensure_ascii=False, indent=4)
            
            print(f"标注信息已保存到 {self.annotations_file}")
            return True
        except Exception as e:
            print(f"保存标注信息时出错: {e}")
            return False
    
    def init_ui(self):
        self.setWindowTitle('哈工大(深圳)发展历程浏览器')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧类别列表
        category_widget = QWidget()
        category_layout = QVBoxLayout(category_widget)
        
        category_label = QLabel("节点类别")
        category_label.setFont(QFont("SimSun", 12, QFont.Bold))
        category_layout.addWidget(category_label)
        
        self.category_list = QListWidget()
        for category in NODE_TYPES:
            if NODE_TYPES[category]["nodes"]:  # 只显示有节点的类别
                item = QListWidgetItem(category)
                color = NODE_TYPES[category]["color"]
                item.setBackground(QColor(color))
                self.category_list.addItem(item)
        
        self.category_list.currentItemChanged.connect(self.on_category_changed)
        category_layout.addWidget(self.category_list)
        
        # 创建中间节点列表
        node_widget = QWidget()
        node_layout = QVBoxLayout(node_widget)
        
        self.node_label = QLabel("节点列表")
        self.node_label.setFont(QFont("SimSun", 12, QFont.Bold))
        node_layout.addWidget(self.node_label)
        
        self.node_list = QListWidget()
        self.node_list.currentItemChanged.connect(self.on_node_changed)
        node_layout.addWidget(self.node_list)
        
        # 创建右侧详情面板
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        
        self.detail_label = QLabel("节点详情")
        self.detail_label.setFont(QFont("SimSun", 14, QFont.Bold))
        detail_layout.addWidget(self.detail_label)
        
        # 创建节点信息面板
        self.node_info = QLabel()
        self.node_info.setWordWrap(True)
        self.node_info.setFont(QFont("SimSun", 12))
        self.node_info.setMinimumHeight(100)
        self.node_info.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        detail_layout.addWidget(self.node_info)
        
        # 创建照片路径输入区域
        photo_group = QGroupBox("节点照片")
        photo_group.setFont(QFont("SimSun", 12))
        photo_layout = QVBoxLayout(photo_group)
        
        self.photo_path_label = QLabel("照片路径列表:")
        self.photo_path_label.setFont(QFont("SimSun", 11))
        photo_layout.addWidget(self.photo_path_label)
        
        # 创建照片路径列表
        self.photo_path_list = QListWidget()
        self.photo_path_list.setMinimumHeight(80)
        self.photo_path_list.itemDoubleClicked.connect(self.preview_photo)
        photo_layout.addWidget(self.photo_path_list)
        
        # 创建照片路径操作按钮布局
        photo_buttons_layout = QHBoxLayout()
        
        # 添加照片路径按钮
        self.add_photo_button = QPushButton("添加路径")
        self.add_photo_button.clicked.connect(self.add_photo_path)
        photo_buttons_layout.addWidget(self.add_photo_button)
        
        # 浏览文件按钮
        self.browse_photo_button = QPushButton("浏览...")
        self.browse_photo_button.clicked.connect(self.browse_photo_path)
        photo_buttons_layout.addWidget(self.browse_photo_button)
        
        # 删除照片路径按钮
        self.remove_photo_button = QPushButton("删除路径")
        self.remove_photo_button.clicked.connect(self.remove_photo_path)
        photo_buttons_layout.addWidget(self.remove_photo_button)
        
        # 预览照片按钮
        self.preview_button = QPushButton("预览照片")
        self.preview_button.clicked.connect(self.preview_selected_photo)
        photo_buttons_layout.addWidget(self.preview_button)
        
        photo_layout.addLayout(photo_buttons_layout)
        
        # 创建照片路径输入框
        self.photo_path_edit = QLineEdit()
        self.photo_path_edit.setPlaceholderText("输入照片路径...")
        photo_layout.addWidget(self.photo_path_edit)
        
        detail_layout.addWidget(photo_group)
        
        # 创建节点文字信息输入区域
        text_group = QGroupBox("节点描述")
        text_group.setFont(QFont("SimSun", 12))
        text_layout = QVBoxLayout(text_group)
        
        self.node_text_label = QLabel("描述文本:")
        self.node_text_label.setFont(QFont("SimSun", 11))
        text_layout.addWidget(self.node_text_label)
        
        self.node_text_edit = QTextEdit()
        self.node_text_edit.setPlaceholderText("输入节点描述文本...")
        self.node_text_edit.textChanged.connect(self.on_node_text_changed)
        text_layout.addWidget(self.node_text_edit)
        
        detail_layout.addWidget(text_group)
        
        # 创建关系面板
        relations_group = QGroupBox("关系")
        relations_group.setFont(QFont("SimSun", 12))
        relations_layout = QVBoxLayout(relations_group)
        
        # 创建入边和出边列表
        in_out_layout = QHBoxLayout()
        
        in_widget = QWidget()
        in_layout = QVBoxLayout(in_widget)
        in_label = QLabel("入边节点")
        in_label.setFont(QFont("SimSun", 11, QFont.Bold))
        in_layout.addWidget(in_label)
        self.in_list = QListWidget()
        self.in_list.itemClicked.connect(self.on_relation_node_clicked)
        in_layout.addWidget(self.in_list)
        
        out_widget = QWidget()
        out_layout = QVBoxLayout(out_widget)
        out_label = QLabel("出边节点")
        out_label.setFont(QFont("SimSun", 11, QFont.Bold))
        out_layout.addWidget(out_label)
        self.out_list = QListWidget()
        self.out_list.itemClicked.connect(self.on_relation_node_clicked)
        out_layout.addWidget(self.out_list)
        
        in_out_layout.addWidget(in_widget)
        in_out_layout.addWidget(out_widget)
        relations_layout.addLayout(in_out_layout)
        
        detail_layout.addWidget(relations_group)
        
        # 创建导航按钮
        nav_layout = QHBoxLayout()
        
        self.back_button = QPushButton("返回")
        self.back_button.setEnabled(False)
        self.back_button.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_button)
        
        self.home_button = QPushButton("首页")
        self.home_button.clicked.connect(self.go_home)
        nav_layout.addWidget(self.home_button)
        
        self.save_button = QPushButton("保存所有标注")
        self.save_button.clicked.connect(self.on_save_button_clicked)
        nav_layout.addWidget(self.save_button)
        
        detail_layout.addLayout(nav_layout)
        
        # 创建分割器来调整各部分宽度
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(category_widget)
        splitter1.addWidget(node_widget)
        
        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(detail_widget)
        
        # 设置分割器的初始尺寸比例
        splitter1.setSizes([200, 300])
        splitter2.setSizes([500, 700])
        
        main_layout.addWidget(splitter2)
        
        # 历史记录
        self.history = []
        
        # 默认选择第一个类别
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
    
    def on_category_changed(self, current, previous):
        if current:
            category = current.text()
            self.node_list.clear()
            self.node_label.setText(f"{category}节点列表")
            
            # 填充节点列表
            for node_id, label in NODE_TYPES[category]["nodes"]:
                item = QListWidgetItem(label)
                item.setData(Qt.UserRole, node_id)
                self.node_list.addItem(item)
            
            if self.node_list.count() > 0:
                self.node_list.setCurrentRow(0)
    
    def on_node_changed(self, current, previous):
        if current:
            node_id = current.data(Qt.UserRole)
            self.show_node_detail(node_id)
    
    def show_node_detail(self, node_id):
        if node_id in self.graph.nodes:
            # 更新当前节点
            old_node = self.current_node
            self.current_node = node_id
            
            # 更新历史记录
            if old_node and old_node != node_id:
                self.history.append(old_node)
                self.back_button.setEnabled(True)
            
            # 获取节点属性
            node_attrs = self.graph.nodes[node_id]
            label = node_attrs.get('label', node_id)
            node_type = NODE_TO_TYPE.get(node_id, "未知类型")
            shape = node_attrs.get('shape', "默认形状")
            color = node_attrs.get('color', "默认颜色")
            
            # 更新节点信息
            self.detail_label.setText(f"节点详情: {label}")
            self.node_info.setText(f"ID: {node_id}\n类型: {node_type}\n标签: {label}\n形状: {shape}\n颜色: {color}")
            self.node_info.setStyleSheet(f"background-color: {color}; padding: 10px; border-radius: 5px;")
            
            # 更新照片路径列表
            self.photo_path_list.clear()
            photo_paths = node_attrs.get('photo_paths', [])
            # 兼容旧版本单路径数据
            old_path = node_attrs.get('photo_path', '')
            if old_path and old_path not in photo_paths:
                photo_paths.append(old_path)
                
            for path in photo_paths:
                item = QListWidgetItem(path)
                item.setToolTip("双击预览照片")
                self.photo_path_list.addItem(item)
            
            self.photo_path_edit.clear()
            
            # 更新节点描述
            self.node_text_edit.blockSignals(True)
            self.node_text_edit.setText(node_attrs.get('description', ''))
            self.node_text_edit.blockSignals(False)
            
            # 更新入边列表
            self.in_list.clear()
            for pred in self.graph.predecessors(node_id):
                edge_data = self.graph.get_edge_data(pred, node_id)
                pred_label = self.graph.nodes[pred].get('label', pred)
                edge_label = edge_data.get('label', '')
                
                if edge_label:
                    item_text = f"{pred_label} ({edge_label})"
                else:
                    item_text = pred_label
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, pred)
                
                # 设置颜色
                if pred in NODE_TO_TYPE:
                    pred_type = NODE_TO_TYPE[pred]
                    item.setBackground(QColor(NODE_TYPES[pred_type]["color"]))
                
                self.in_list.addItem(item)
            
            # 更新出边列表
            self.out_list.clear()
            for succ in self.graph.successors(node_id):
                edge_data = self.graph.get_edge_data(node_id, succ)
                succ_label = self.graph.nodes[succ].get('label', succ)
                edge_label = edge_data.get('label', '')
                
                if edge_label:
                    item_text = f"{succ_label} ({edge_label})"
                else:
                    item_text = succ_label
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, succ)
                
                # 设置颜色
                if succ in NODE_TO_TYPE:
                    succ_type = NODE_TO_TYPE[succ]
                    item.setBackground(QColor(NODE_TYPES[succ_type]["color"]))
                
                self.out_list.addItem(item)
    
    def on_relation_node_clicked(self, item):
        node_id = item.data(Qt.UserRole)
        
        # 找到节点类型并选择相应的类别
        if node_id in NODE_TO_TYPE:
            node_type = NODE_TO_TYPE[node_id]
            
            # 选择对应的类别
            for i in range(self.category_list.count()):
                if self.category_list.item(i).text() == node_type:
                    self.category_list.setCurrentRow(i)
                    break
            
            # 在节点列表中选择对应的节点
            for i in range(self.node_list.count()):
                if self.node_list.item(i).data(Qt.UserRole) == node_id:
                    self.node_list.setCurrentRow(i)
                    break
    
    def go_back(self):
        if self.history:
            # 弹出最后一个历史记录
            previous_node = self.history.pop()
            
            # 如果历史记录为空，禁用返回按钮
            if not self.history:
                self.back_button.setEnabled(False)
            
            # 找到节点类型并选择相应的类别
            if previous_node in NODE_TO_TYPE:
                node_type = NODE_TO_TYPE[previous_node]
                
                # 选择对应的类别
                for i in range(self.category_list.count()):
                    if self.category_list.item(i).text() == node_type:
                        self.category_list.setCurrentRow(i)
                        break
                
                # 在节点列表中选择对应的节点
                for i in range(self.node_list.count()):
                    if self.node_list.item(i).data(Qt.UserRole) == previous_node:
                        self.node_list.setCurrentRow(i)
                        break
    
    def go_home(self):
        # 清空历史记录
        self.history = []
        self.back_button.setEnabled(False)
        
        # 选择第一个类别
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)

    def add_photo_path(self):
        """添加照片路径到列表"""
        path = self.photo_path_edit.text().strip()
        if path and self.current_node:
            item = QListWidgetItem(path)
            item.setToolTip("双击预览照片")
            self.photo_path_list.addItem(item)
            self.photo_path_edit.clear()
            self.save_photo_paths()
            
            # 询问是否预览新添加的照片
            if os.path.exists(path):
                reply = QMessageBox.question(self, '预览照片', 
                                            "是否预览新添加的照片？",
                                            QMessageBox.Yes | QMessageBox.No,
                                            QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.show_photo_preview(path)
    
    def browse_photo_path(self):
        """浏览并选择照片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择照片", "", "图片文件 (*.jpg *.jpeg *.png *.gif *.bmp)"
        )
        if file_path:
            self.photo_path_edit.setText(file_path)
    
    def remove_photo_path(self):
        """从列表中删除选中的照片路径"""
        selected_items = self.photo_path_list.selectedItems()
        for item in selected_items:
            self.photo_path_list.takeItem(self.photo_path_list.row(item))
        self.save_photo_paths()
    
    def save_photo_paths(self):
        """保存当前节点的所有照片路径"""
        if self.current_node and self.current_node in self.graph.nodes:
            paths = []
            for i in range(self.photo_path_list.count()):
                paths.append(self.photo_path_list.item(i).text())
            self.graph.nodes[self.current_node]['photo_paths'] = paths
            
            # 保存到JSON文件
            self.save_annotations()
    
    def on_node_text_changed(self):
        """当节点描述文本更改时保存"""
        if self.current_node:
            node_text = self.node_text_edit.toPlainText().strip()
            if self.current_node in self.graph.nodes:
                self.graph.nodes[self.current_node]['description'] = node_text
                
                # 保存到JSON文件
                self.save_annotations()

    def on_save_button_clicked(self):
        """保存按钮点击事件处理"""
        if self.save_annotations():
            QMessageBox.information(self, "保存成功", "所有节点标注信息已成功保存。")
        else:
            QMessageBox.warning(self, "保存失败", "保存节点标注信息时发生错误，请检查控制台输出。")

    def closeEvent(self, event):
        """程序关闭时的事件处理"""
        reply = QMessageBox.question(self, '保存确认',
                                     "是否在退出前保存所有标注信息？",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                     QMessageBox.Yes)
        
        if reply == QMessageBox.Cancel:
            event.ignore()
            return
        
        if reply == QMessageBox.Yes:
            if not self.save_annotations():
                reply = QMessageBox.warning(self, '保存失败',
                                          "保存标注信息失败，是否仍要退出？",
                                          QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.No)
                if reply == QMessageBox.No:
                    event.ignore()
                    return
        
        event.accept()

    def preview_photo(self, item):
        """预览列表中的照片"""
        photo_path = item.text()
        self.show_photo_preview(photo_path)
    
    def preview_selected_photo(self):
        """预览选中的照片"""
        selected_items = self.photo_path_list.selectedItems()
        if selected_items:
            photo_path = selected_items[0].text()
            self.show_photo_preview(photo_path)
        else:
            QMessageBox.information(self, "提示", "请先选择一个照片路径")
    
    def show_photo_preview(self, photo_path):
        """显示照片预览对话框"""
        if not os.path.exists(photo_path):
            QMessageBox.warning(self, "文件不存在", f"找不到照片文件:\n{photo_path}")
            return
            
        dialog = PhotoPreviewDialog(photo_path, self)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 设置中文字体
    font = QFont("SimSun", 10)
    app.setFont(font)
    
    # 获取当前文件目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建dot文件路径
    dot_file_path = os.path.join(current_dir, "presentation_HITSZ", "hitsz_flow.dot")
    
    # 如果文件不存在，尝试其他可能的路径
    if not os.path.exists(dot_file_path):
        dot_file_path = os.path.join(current_dir, "hitsz_flow.dot")
    
    if not os.path.exists(dot_file_path):
        # 显示错误消息框而不只是打印到控制台
        QMessageBox.critical(None, "错误", f"找不到文件 {dot_file_path}")
        return
    
    # 构建图
    graph = build_graph_from_dot(dot_file_path)
    
    if graph:
        # 创建并显示主窗口
        window = HITSZFlowViewer(graph)
        window.show()
        
        sys.exit(app.exec_())
    else:
        QMessageBox.critical(None, "错误", "无法构建图")

if __name__ == "__main__":
    main() 