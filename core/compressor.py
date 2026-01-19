"""
压缩器模块
包含单文件压缩器和批量压缩器
"""

import os
import re
import subprocess
import threading
from dataclasses import dataclass
from typing import Optional, List
from PyQt5.QtCore import QObject, pyqtSignal

from .presets import CompressionSettings, get_ffmpeg_params
from .utils import get_video_info, parse_duration, get_output_path


@dataclass
class CompressionResult:
    """压缩结果数据类"""
    success: bool
    input_path: str
    output_path: str
    original_size: int = 0
    compressed_size: int = 0
    error_message: str = ""


class VideoCompressor(QObject):
    """
    单文件视频压缩器
    在独立线程中运行 FFmpeg,支持实时进度更新和取消操作
    """

    # 信号定义
    progress_updated = pyqtSignal(float)  # 进度更新 (0-100)
    status_updated = pyqtSignal(str)  # 状态文字更新
    compression_finished = pyqtSignal(CompressionResult)  # 压缩完成
    compression_error = pyqtSignal(str)  # 压缩错误

    def __init__(self, parent=None):
        super().__init__(parent)

        self._process: Optional[subprocess.Popen] = None
        self._is_cancelled = False
        self._is_paused = False
        self._pause_event = threading.Event()
        self._pause_event.set()  # 初始为非暂停状态

    def compress(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ):
        """
        启动压缩任务 (在新线程中运行)

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            settings: 压缩设置
        """
        self._is_cancelled = False
        self._is_paused = False
        self._pause_event.set()

        # 在新线程中运行压缩
        thread = threading.Thread(
            target=self._compress_thread,
            args=(input_path, output_path, settings),
            daemon=True
        )
        thread.start()

    def cancel(self):
        """取消压缩"""
        self._is_cancelled = True
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass

    def pause(self):
        """暂停压缩"""
        self._is_paused = True
        self._pause_event.clear()

    def resume(self):
        """恢复压缩"""
        self._is_paused = False
        self._pause_event.set()

    @property
    def is_paused(self) -> bool:
        """是否已暂停"""
        return self._is_paused

    @property
    def is_cancelled(self) -> bool:
        """是否已取消"""
        return self._is_cancelled

    def _compress_thread(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings
    ):
        """
        压缩线程主函数

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            settings: 压缩设置
        """
        try:
            # 获取视频信息
            self.status_updated.emit("正在获取视频信息...")
            video_info = get_video_info(input_path)

            if not video_info:
                self.compression_error.emit(f"无法获取视频信息: {input_path}")
                result = CompressionResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    error_message="无法获取视频信息"
                )
                self.compression_finished.emit(result)
                return

            # 构建 FFmpeg 命令
            cmd = self._build_ffmpeg_command(input_path, output_path, settings, video_info)

            # 启动 FFmpeg 进程
            self.status_updated.emit("正在压缩...")
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'
            )

            # 解析进度
            total_duration = video_info.get('duration', 0)
            self._parse_progress(total_duration)

            # 等待进程完成
            self._process.wait()

            # 检查是否被取消
            if self._is_cancelled:
                # 删除未完成的输出文件
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception:
                        pass

                result = CompressionResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    error_message="已取消"
                )
                self.compression_finished.emit(result)
                return

            # 检查返回码
            if self._process.returncode != 0:
                result = CompressionResult(
                    success=False,
                    input_path=input_path,
                    output_path=output_path,
                    error_message=f"FFmpeg 返回错误码: {self._process.returncode}"
                )
                self.compression_finished.emit(result)
                return

            # 压缩成功
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            result = CompressionResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size
            )
            self.compression_finished.emit(result)

        except Exception as e:
            self.compression_error.emit(str(e))
            result = CompressionResult(
                success=False,
                input_path=input_path,
                output_path=output_path,
                error_message=str(e)
            )
            self.compression_finished.emit(result)

    def _build_ffmpeg_command(
        self,
        input_path: str,
        output_path: str,
        settings: CompressionSettings,
        video_info: dict
    ) -> List[str]:
        """
        构建 FFmpeg 命令

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            settings: 压缩设置
            video_info: 视频信息

        Returns:
            命令列表
        """
        cmd = ['ffmpeg', '-y', '-i', input_path]

        # 获取 FFmpeg 参数
        params = get_ffmpeg_params(settings, video_info)

        # 视频编码器
        cmd.extend(['-c:v', params['video_codec']])

        # CRF 或 码率
        if 'crf' in params:
            cmd.extend(['-crf', str(params['crf'])])
        if 'video_bitrate' in params:
            cmd.extend(['-b:v', params['video_bitrate']])

        # 预设
        if 'preset' in params:
            cmd.extend(['-preset', params['preset']])

        # 分辨率
        if 'scale' in params:
            cmd.extend(['-vf', f"scale={params['scale']}"])

        # 帧率
        if 'fps' in params:
            cmd.extend(['-r', str(params['fps'])])

        # 音频
        if params.get('no_audio'):
            cmd.append('-an')
        else:
            if 'audio_codec' in params:
                cmd.extend(['-c:a', params['audio_codec']])
            if 'audio_bitrate' in params:
                cmd.extend(['-b:a', params['audio_bitrate']])

        # H.265 兼容性
        if params['video_codec'] == 'libx265':
            cmd.extend(['-tag:v', 'hvc1'])

        # 输出文件
        cmd.append(output_path)

        return cmd

    def _parse_progress(self, total_duration: float):
        """
        解析 FFmpeg 输出获取进度

        Args:
            total_duration: 总时长 (秒)
        """
        if not self._process or not self._process.stdout:
            return

        time_pattern = re.compile(r'time=(\d+:\d+:\d+\.?\d*)')

        try:
            for line in iter(self._process.stdout.readline, ''):
                if not line:
                    break

                # 检查是否取消
                if self._is_cancelled:
                    break

                # 暂停检查
                self._pause_event.wait()

                # 提取时间信息
                match = time_pattern.search(line)
                if match and total_duration > 0:
                    time_str = match.group(1)
                    current_time = parse_duration(time_str)
                    progress = min(100.0, (current_time / total_duration) * 100)
                    self.progress_updated.emit(progress)

        except Exception as e:
            print(f"解析进度失败: {e}")


class BatchCompressor(QObject):
    """
    批量压缩器
    串行处理多个文件,提供批量进度跟踪
    """

    # 信号定义
    file_started = pyqtSignal(int, str)  # 开始处理某文件 (索引, 文件名)
    file_progress = pyqtSignal(int, float)  # 某文件进度 (索引, 进度)
    file_finished = pyqtSignal(int, CompressionResult)  # 某文件完成
    batch_finished = pyqtSignal(list)  # 批量完成 (结果列表)
    batch_cancelled = pyqtSignal()  # 批量取消

    def __init__(self, parent=None):
        super().__init__(parent)

        self._compressor = VideoCompressor()
        self._current_index = -1
        self._files: List[str] = []
        self._output_dir = ""
        self._settings: Optional[CompressionSettings] = None
        self._suffix = ""
        self._results: List[CompressionResult] = []
        self._is_running = False

        # 连接信号
        self._compressor.progress_updated.connect(self._on_progress)
        self._compressor.compression_finished.connect(self._on_file_finished)
        self._compressor.compression_error.connect(self._on_error)

    def start_batch(
        self,
        files: List[str],
        output_dir: str,
        settings: CompressionSettings,
        suffix: str = "_compressed"
    ):
        """
        启动批量压缩

        Args:
            files: 文件路径列表
            output_dir: 输出目录
            settings: 压缩设置
            suffix: 文件后缀
        """
        self._files = files
        self._output_dir = output_dir
        self._settings = settings
        self._suffix = suffix
        self._results = []
        self._current_index = -1
        self._is_running = True

        # 开始压缩第一个文件
        self._compress_next()

    def cancel(self):
        """取消批量压缩"""
        self._is_running = False
        self._compressor.cancel()
        self.batch_cancelled.emit()

    def pause(self):
        """暂停压缩"""
        self._compressor.pause()

    def resume(self):
        """恢复压缩"""
        self._compressor.resume()

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._is_running

    @property
    def current_index(self) -> int:
        """当前处理文件索引"""
        return self._current_index

    @property
    def total_files(self) -> int:
        """总文件数"""
        return len(self._files)

    def _compress_next(self):
        """压缩下一个文件"""
        if not self._is_running:
            return

        self._current_index += 1

        # 检查是否完成所有文件
        if self._current_index >= len(self._files):
            self._is_running = False
            self.batch_finished.emit(self._results)
            return

        # 获取当前文件
        input_path = self._files[self._current_index]
        file_name = os.path.basename(input_path)

        # 生成输出路径
        output_path = get_output_path(input_path, self._output_dir, self._suffix)

        # 发射文件开始信号
        self.file_started.emit(self._current_index, file_name)

        # 启动压缩
        self._compressor.compress(input_path, output_path, self._settings)

    def _on_progress(self, progress: float):
        """
        接收单文件进度

        Args:
            progress: 进度 (0-100)
        """
        self.file_progress.emit(self._current_index, progress)

    def _on_file_finished(self, result: CompressionResult):
        """
        接收单文件完成

        Args:
            result: 压缩结果
        """
        # 记录结果
        self._results.append(result)

        # 发射文件完成信号
        self.file_finished.emit(self._current_index, result)

        # 压缩下一个文件
        self._compress_next()

    def _on_error(self, error: str):
        """
        接收错误

        Args:
            error: 错误信息
        """
        print(f"压缩错误: {error}")
