"""
文件列表模块
包含拖拽区域和文件列表组件
"""

from typing import List, Optional, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from core.utils import get_video_info, format_size, format_duration, is_supported_format


class DropZone(QFrame):
    """
    拖拽区域组件
    支持拖拽文件和点击选择文件
    """

    # 信号定义
    files_dropped = pyqtSignal(list)  # 文件拖入

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """构建 UI"""
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setLineWidth(2)
        self.setMinimumHeight(120)

        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 图标标签
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_label)

        # 提示文字
        hint_label = QLabel("拖拽视频文件到此处 或 点击选择文件")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(hint_label)

        # 支持格式提示
        format_label = QLabel("支持 MP4, MOV, AVI, MKV, WMV, FLV, WEBM, M4V")
        format_label.setAlignment(Qt.AlignCenter)
        format_label.setStyleSheet("font-size: 12px; color: #999;")
        layout.addWidget(format_label)

        # 选择文件按钮
        self.select_btn = QPushButton("选择文件")
        self.select_btn.setFixedWidth(120)
        self.select_btn.clicked.connect(self._on_select_clicked)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.select_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 样式
        self.setStyleSheet("""
            DropZone {
                background-color: #f5f5f5;
                border: 2px dashed #ccc;
                border-radius: 8px;
            }
            DropZone:hover {
                background-color: #e8f4f8;
                border-color: #4a9eff;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 高亮边框
            self.setStyleSheet("""
                DropZone {
                    background-color: #e8f4f8;
                    border: 2px solid #4a9eff;
                    border-radius: 8px;
                }
            """)

    def dragLeaveEvent(self, event):
        """拖离事件"""
        # 恢复样式
        self.setStyleSheet("""
            DropZone {
                background-color: #f5f5f5;
                border: 2px dashed #ccc;
                border-radius: 8px;
            }
            DropZone:hover {
                background-color: #e8f4f8;
                border-color: #4a9eff;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        """放下事件"""
        # 恢复样式
        self.setStyleSheet("""
            DropZone {
                background-color: #f5f5f5;
                border: 2px dashed #ccc;
                border-radius: 8px;
            }
            DropZone:hover {
                background-color: #e8f4f8;
                border-color: #4a9eff;
            }
        """)

        # 提取文件路径
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if is_supported_format(file_path):
                files.append(file_path)

        if files:
            self.files_dropped.emit(files)

    def _on_select_clicked(self):
        """选择文件按钮点击事件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.mov *.avi *.mkv *.wmv *.flv *.webm *.m4v);;所有文件 (*.*)"
        )

        if file_paths:
            self.files_dropped.emit(file_paths)


class FileListWidget(QWidget):
    """
    文件列表组件
    显示已添加的视频文件列表
    """

    # 表格列索引
    COL_NAME = 0
    COL_SIZE = 1
    COL_DURATION = 2
    COL_STATUS = 3

    # 信号定义
    files_changed = pyqtSignal()  # 文件列表变化

    def __init__(self, parent=None):
        super().__init__(parent)

        self._files: List[Dict[str, Any]] = []
        self._setup_ui()

    def _setup_ui(self):
        """构建 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 拖拽区域
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.add_files)
        layout.addWidget(self.drop_zone)

        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel("文件列表:")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self.clear_files)
        title_layout.addWidget(self.clear_btn)

        layout.addLayout(title_layout)

        # 文件列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["文件名", "大小", "时长", "状态"])

        # 表格样式
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)

        # 列宽设置
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_SIZE, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_DURATION, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_STATUS, QHeaderView.ResizeToContents)

        # 右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # 按键事件
        self.table.keyPressEvent = self._table_key_press

        layout.addWidget(self.table)

    def add_files(self, file_paths: List[str]):
        """
        添加文件到列表

        Args:
            file_paths: 文件路径列表
        """
        added = False

        for file_path in file_paths:
            # 检查是否已存在
            if any(f['path'] == file_path for f in self._files):
                continue

            # 获取视频信息
            info = get_video_info(file_path)
            if not info:
                # 无法获取信息,跳过
                continue

            # 创建文件数据
            file_data = {
                'path': file_path,
                'name': info['file_name'],
                'size': info['file_size'],
                'duration': info['duration'],
                'status': '等待中',
                'info': info
            }

            # 添加到列表
            self._files.append(file_data)
            self._add_table_row(file_data)
            added = True

        if added:
            self.files_changed.emit()

    def remove_selected(self):
        """移除选中的文件"""
        selected_rows = set(item.row() for item in self.table.selectedItems())

        if not selected_rows:
            return

        # 从后往前删除,避免索引变化
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)
            del self._files[row]

        self.files_changed.emit()

    def clear_files(self):
        """清空所有文件"""
        self._files.clear()
        self.table.setRowCount(0)
        self.files_changed.emit()

    def update_status(self, index: int, status: str):
        """
        更新文件状态

        Args:
            index: 文件索引
            status: 状态文字
        """
        if 0 <= index < len(self._files):
            self._files[index]['status'] = status
            self.table.setItem(index, self.COL_STATUS, QTableWidgetItem(status))

    def get_files(self) -> List[str]:
        """
        获取文件路径列表

        Returns:
            文件路径列表
        """
        return [f['path'] for f in self._files]

    def get_file_info(self, index: int) -> Optional[Dict[str, Any]]:
        """
        获取文件信息

        Args:
            index: 文件索引

        Returns:
            文件信息字典
        """
        if 0 <= index < len(self._files):
            return self._files[index]['info']
        return None

    def file_count(self) -> int:
        """获取文件数量"""
        return len(self._files)

    def has_files(self) -> bool:
        """是否有文件"""
        return len(self._files) > 0

    def _add_table_row(self, file_data: Dict[str, Any]):
        """
        添加表格行

        Args:
            file_data: 文件数据
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        # 文件名
        self.table.setItem(row, self.COL_NAME, QTableWidgetItem(file_data['name']))

        # 大小
        size_str = format_size(file_data['size'])
        self.table.setItem(row, self.COL_SIZE, QTableWidgetItem(size_str))

        # 时长
        duration_str = format_duration(file_data['duration'])
        self.table.setItem(row, self.COL_DURATION, QTableWidgetItem(duration_str))

        # 状态
        self.table.setItem(row, self.COL_STATUS, QTableWidgetItem(file_data['status']))

    def _table_key_press(self, event):
        """
        表格按键事件

        Args:
            event: 按键事件
        """
        if event.key() == Qt.Key_Delete:
            self.remove_selected()
        else:
            QTableWidget.keyPressEvent(self.table, event)

    def _show_context_menu(self, pos):
        """
        显示右键菜单

        Args:
            pos: 鼠标位置
        """
        if not self.table.selectedItems():
            return

        menu = QMenu(self)

        remove_action = QAction("移除选中", self)
        remove_action.triggered.connect(self.remove_selected)
        menu.addAction(remove_action)

        clear_action = QAction("清空列表", self)
        clear_action.triggered.connect(self.clear_files)
        menu.addAction(clear_action)

        menu.exec_(self.table.viewport().mapToGlobal(pos))
