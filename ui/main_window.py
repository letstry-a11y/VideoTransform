"""
主窗口模块
应用程序的主界面,整合所有组件
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

from core.compressor import BatchCompressor, CompressionResult
from core.utils import check_ffmpeg_installed, format_size, calculate_compression_ratio
from .file_list import FileListWidget
from .settings import SettingsPanel


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()

        self._batch_compressor = BatchCompressor()
        self._is_compressing = False

        self._setup_ui()
        self._connect_signals()
        self._check_ffmpeg()

    def _setup_ui(self):
        """构建 UI"""
        self.setWindowTitle("视频压缩工具")
        self.setMinimumSize(800, 900)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 文件列表
        self.file_list = FileListWidget()
        layout.addWidget(self.file_list)

        # 设置面板
        self.settings_panel = SettingsPanel()
        layout.addWidget(self.settings_panel)

        # 进度区域
        progress_widget = self._create_progress_widget()
        layout.addWidget(progress_widget)

        # 按钮区域
        button_widget = self._create_button_widget()
        layout.addWidget(button_widget)

    def _create_progress_widget(self) -> QWidget:
        """创建进度显示区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 当前文件标签
        self.current_file_label = QLabel("准备就绪")
        self.current_file_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.current_file_label)

        # 文件进度条
        self.file_progress = QProgressBar()
        self.file_progress.setRange(0, 100)
        self.file_progress.setValue(0)
        self.file_progress.setTextVisible(True)
        layout.addWidget(self.file_progress)

        # 总进度标签
        self.total_progress_label = QLabel("")
        layout.addWidget(self.total_progress_label)

        return widget

    def _create_button_widget(self) -> QWidget:
        """创建按钮区域"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addStretch()

        # 开始压缩按钮
        self.start_btn = QPushButton("开始压缩")
        self.start_btn.setMinimumWidth(120)
        self.start_btn.setMinimumHeight(35)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
            QPushButton:pressed {
                background-color: #2a7edf;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        layout.addWidget(self.start_btn)

        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumWidth(120)
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        layout.addWidget(self.cancel_btn)

        layout.addStretch()

        return widget

    def _connect_signals(self):
        """连接信号槽"""
        # 按钮信号
        self.start_btn.clicked.connect(self._start_compression)
        self.cancel_btn.clicked.connect(self._cancel_compression)

        # 文件列表信号
        self.file_list.files_changed.connect(self._update_start_button)

        # 批量压缩器信号
        self._batch_compressor.file_started.connect(self._on_file_started)
        self._batch_compressor.file_progress.connect(self._on_file_progress)
        self._batch_compressor.file_finished.connect(self._on_file_finished)
        self._batch_compressor.batch_finished.connect(self._on_batch_finished)
        self._batch_compressor.batch_cancelled.connect(self._on_batch_cancelled)

    def _check_ffmpeg(self):
        """检查 FFmpeg 是否可用"""
        if not check_ffmpeg_installed():
            QMessageBox.warning(
                self,
                "FFmpeg 未找到",
                "未检测到 FFmpeg。\n\n"
                "请确保 FFmpeg 已安装并添加到系统 PATH,\n"
                "或将 FFmpeg 可执行文件放置在 ffmpeg/bin/ 目录下。"
            )

    def _update_start_button(self):
        """更新开始按钮状态"""
        has_files = self.file_list.has_files()
        self.start_btn.setEnabled(has_files and not self._is_compressing)

    def _start_compression(self):
        """开始压缩"""
        # 检查文件列表
        if not self.file_list.has_files():
            QMessageBox.information(self, "提示", "请先添加视频文件")
            return

        # 获取输出目录
        output_dir = self.settings_panel.get_output_dir()
        if not output_dir:
            QMessageBox.warning(self, "错误", "请设置输出目录")
            return

        # 创建输出目录
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建输出目录:\n{e}")
            return

        # 获取设置
        settings = self.settings_panel.get_settings()
        files = self.file_list.get_files()
        suffix = self.settings_panel.get_suffix()

        # 更新 UI 状态
        self._is_compressing = True
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.settings_panel.set_enabled(False)
        self.file_progress.setValue(0)
        self.total_progress_label.setText("")

        # 重置所有文件状态
        for i in range(self.file_list.file_count()):
            self.file_list.update_status(i, "等待中")

        # 启动批量压缩
        self._batch_compressor.start_batch(files, output_dir, settings, suffix)

    def _cancel_compression(self):
        """取消压缩"""
        reply = QMessageBox.question(
            self,
            "确认取消",
            "确定要取消压缩吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._batch_compressor.cancel()

    def _on_file_started(self, index: int, file_name: str):
        """
        处理文件开始

        Args:
            index: 文件索引
            file_name: 文件名
        """
        self.current_file_label.setText(f"正在压缩: {file_name}")
        self.file_progress.setValue(0)
        self.file_list.update_status(index, "压缩中")

        total = self._batch_compressor.total_files
        self.total_progress_label.setText(f"总进度: {index + 1}/{total}")

    def _on_file_progress(self, index: int, progress: float):
        """
        处理文件进度

        Args:
            index: 文件索引
            progress: 进度 (0-100)
        """
        self.file_progress.setValue(int(progress))

    def _on_file_finished(self, index: int, result: CompressionResult):
        """
        处理文件完成

        Args:
            index: 文件索引
            result: 压缩结果
        """
        if result.success:
            self.file_list.update_status(index, "完成")
        else:
            self.file_list.update_status(index, f"失败: {result.error_message}")

    def _on_batch_finished(self, results: list):
        """
        处理批量完成

        Args:
            results: 结果列表
        """
        # 恢复 UI 状态
        self._is_compressing = False
        self.start_btn.setEnabled(self.file_list.has_files())
        self.cancel_btn.setEnabled(False)
        self.settings_panel.set_enabled(True)
        self.current_file_label.setText("压缩完成")
        self.file_progress.setValue(100)

        # 统计结果
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        total_original_size = sum(r.original_size for r in results if r.success)
        total_compressed_size = sum(r.compressed_size for r in results if r.success)

        # 计算压缩率
        compression_ratio = calculate_compression_ratio(
            total_original_size,
            total_compressed_size
        )

        # 显示结果对话框
        result_text = (
            f"压缩完成!\n\n"
            f"成功: {success_count}/{total_count} 个文件\n"
            f"原始大小: {format_size(total_original_size)}\n"
            f"压缩后大小: {format_size(total_compressed_size)}\n"
            f"压缩率: {compression_ratio:.1f}%"
        )

        QMessageBox.information(self, "压缩完成", result_text)

        # 播放提示音
        if self.settings_panel.should_play_sound():
            try:
                if sys.platform == 'win32':
                    import winsound
                    winsound.MessageBeep()
            except Exception:
                pass

        # 打开输出目录
        if self.settings_panel.should_open_folder():
            output_dir = self.settings_panel.get_output_dir()
            try:
                if sys.platform == 'win32':
                    os.startfile(output_dir)
                elif sys.platform == 'darwin':
                    os.system(f'open "{output_dir}"')
                else:
                    os.system(f'xdg-open "{output_dir}"')
            except Exception as e:
                print(f"无法打开目录: {e}")

    def _on_batch_cancelled(self):
        """处理批量取消"""
        # 恢复 UI 状态
        self._is_compressing = False
        self.start_btn.setEnabled(self.file_list.has_files())
        self.cancel_btn.setEnabled(False)
        self.settings_panel.set_enabled(True)
        self.current_file_label.setText("已取消")
        self.file_progress.setValue(0)

        QMessageBox.information(self, "已取消", "压缩已取消")

    def closeEvent(self, event):
        """
        窗口关闭事件

        Args:
            event: 关闭事件
        """
        if self._is_compressing:
            reply = QMessageBox.question(
                self,
                "确认退出",
                "正在压缩中,确定要退出吗?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self._batch_compressor.cancel()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
