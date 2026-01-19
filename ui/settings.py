"""
设置面板模块
包含压缩参数设置和输出设置
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QRadioButton,
    QButtonGroup, QSpinBox, QPushButton, QFrame, QComboBox, QLineEdit,
    QCheckBox, QFileDialog
)
from PyQt5.QtCore import pyqtSignal

from core.presets import (
    CompressionSettings, QualityLevel, VideoCodec, Resolution,
    FrameRate, CompressionMode, AUDIO_BITRATE_OPTIONS
)


class SettingsPanel(QWidget):
    """
    设置面板组件
    提供压缩参数配置界面
    """

    # 信号定义
    settings_changed = pyqtSignal()  # 设置变更

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """构建 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 压缩设置组
        compress_group = self._create_compress_settings()
        layout.addWidget(compress_group)

        # 输出设置组
        output_group = self._create_output_settings()
        layout.addWidget(output_group)

        # 完成后操作组
        completion_group = self._create_completion_settings()
        layout.addWidget(completion_group)

    def _create_compress_settings(self) -> QGroupBox:
        """创建压缩设置组"""
        group = QGroupBox("压缩设置")
        layout = QVBoxLayout()

        # 质量等级
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("质量等级:"))

        self.quality_group = QButtonGroup(self)
        self.quality_high = QRadioButton("高质量")
        self.quality_medium = QRadioButton("中等质量")
        self.quality_low = QRadioButton("低质量")

        self.quality_group.addButton(self.quality_high, 0)
        self.quality_group.addButton(self.quality_medium, 1)
        self.quality_group.addButton(self.quality_low, 2)

        self.quality_medium.setChecked(True)  # 默认中等质量

        quality_layout.addWidget(self.quality_high)
        quality_layout.addWidget(self.quality_medium)
        quality_layout.addWidget(self.quality_low)
        quality_layout.addStretch()

        layout.addLayout(quality_layout)

        # 压缩模式
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("压缩模式:"))

        self.mode_group = QButtonGroup(self)
        self.mode_quality = QRadioButton("按质量")
        self.mode_ratio = QRadioButton("按比例")
        self.mode_size = QRadioButton("按大小")

        self.mode_group.addButton(self.mode_quality, 0)
        self.mode_group.addButton(self.mode_ratio, 1)
        self.mode_group.addButton(self.mode_size, 2)

        self.mode_quality.setChecked(True)  # 默认按质量

        mode_layout.addWidget(self.mode_quality)
        mode_layout.addWidget(self.mode_ratio)

        # 比例设置
        self.ratio_spin = QSpinBox()
        self.ratio_spin.setRange(5, 95)
        self.ratio_spin.setValue(50)
        self.ratio_spin.setSuffix("%")
        self.ratio_spin.setEnabled(False)
        mode_layout.addWidget(self.ratio_spin)

        mode_layout.addWidget(self.mode_size)

        # 大小设置
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 10000)
        self.size_spin.setValue(100)
        self.size_spin.setSuffix(" MB")
        self.size_spin.setEnabled(False)
        mode_layout.addWidget(self.size_spin)

        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # 高级选项按钮
        self.advanced_btn = QPushButton("▶ 高级选项")
        self.advanced_btn.setCheckable(True)
        self.advanced_btn.setStyleSheet("text-align: left; padding: 5px;")
        self.advanced_btn.clicked.connect(self._toggle_advanced)
        layout.addWidget(self.advanced_btn)

        # 高级选项面板
        self.advanced_panel = self._create_advanced_panel()
        self.advanced_panel.setVisible(False)
        layout.addWidget(self.advanced_panel)

        group.setLayout(layout)
        return group

    def _create_advanced_panel(self) -> QFrame:
        """创建高级选项面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()

        # 视频码率
        bitrate_layout = QHBoxLayout()
        bitrate_layout.addWidget(QLabel("视频码率:"))

        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems([
            "自动", "1000 kbps", "2000 kbps", "4000 kbps",
            "6000 kbps", "8000 kbps", "自定义"
        ])
        bitrate_layout.addWidget(self.bitrate_combo)

        self.custom_bitrate = QSpinBox()
        self.custom_bitrate.setRange(100, 50000)
        self.custom_bitrate.setValue(4000)
        self.custom_bitrate.setSuffix(" kbps")
        self.custom_bitrate.setEnabled(False)
        bitrate_layout.addWidget(self.custom_bitrate)

        bitrate_layout.addStretch()
        layout.addLayout(bitrate_layout)

        # 分辨率
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("分辨率:"))

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "保持原始", "1080p", "720p", "480p", "自定义"
        ])
        resolution_layout.addWidget(self.resolution_combo)

        self.custom_width = QSpinBox()
        self.custom_width.setRange(100, 7680)
        self.custom_width.setValue(1920)
        self.custom_width.setEnabled(False)
        resolution_layout.addWidget(QLabel("宽:"))
        resolution_layout.addWidget(self.custom_width)

        self.custom_height = QSpinBox()
        self.custom_height.setRange(100, 4320)
        self.custom_height.setValue(1080)
        self.custom_height.setEnabled(False)
        resolution_layout.addWidget(QLabel("高:"))
        resolution_layout.addWidget(self.custom_height)

        resolution_layout.addStretch()
        layout.addLayout(resolution_layout)

        # 编码器和帧率
        codec_fps_layout = QHBoxLayout()
        codec_fps_layout.addWidget(QLabel("编码器:"))

        self.codec_combo = QComboBox()
        self.codec_combo.addItems(["H.264", "H.265"])
        codec_fps_layout.addWidget(self.codec_combo)

        codec_fps_layout.addStretch()

        codec_fps_layout.addWidget(QLabel("帧率:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems([
            "保持原始", "24 fps", "30 fps", "60 fps", "自定义"
        ])
        codec_fps_layout.addWidget(self.fps_combo)

        self.custom_fps = QSpinBox()
        self.custom_fps.setRange(1, 120)
        self.custom_fps.setValue(30)
        self.custom_fps.setEnabled(False)
        codec_fps_layout.addWidget(self.custom_fps)

        codec_fps_layout.addStretch()
        layout.addLayout(codec_fps_layout)

        # 音频设置
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(QLabel("音频码率:"))

        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItems([
            "64 kbps", "128 kbps", "192 kbps", "256 kbps", "320 kbps"
        ])
        self.audio_bitrate_combo.setCurrentIndex(2)  # 默认 192 kbps
        audio_layout.addWidget(self.audio_bitrate_combo)

        self.keep_audio_check = QCheckBox("保留音频")
        self.keep_audio_check.setChecked(True)
        audio_layout.addWidget(self.keep_audio_check)

        audio_layout.addStretch()
        layout.addLayout(audio_layout)

        panel.setLayout(layout)
        return panel

    def _create_output_settings(self) -> QGroupBox:
        """创建输出设置组"""
        group = QGroupBox("输出设置")
        layout = QVBoxLayout()

        # 输出目录
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("输出目录:"))

        self.output_dir_edit = QLineEdit()
        # 设置默认输出目录
        default_dir = os.path.expanduser("~/Videos/Compressed")
        self.output_dir_edit.setText(default_dir)
        dir_layout.addWidget(self.output_dir_edit)

        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._browse_output_dir)
        dir_layout.addWidget(self.browse_btn)

        layout.addLayout(dir_layout)

        # 文件后缀
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("文件后缀:"))

        self.suffix_edit = QLineEdit()
        self.suffix_edit.setText("_compressed")
        self.suffix_edit.setMaximumWidth(150)
        suffix_layout.addWidget(self.suffix_edit)

        suffix_layout.addStretch()
        layout.addLayout(suffix_layout)

        group.setLayout(layout)
        return group

    def _create_completion_settings(self) -> QGroupBox:
        """创建完成后操作组"""
        group = QGroupBox("完成后操作")
        layout = QHBoxLayout()

        self.open_folder_check = QCheckBox("打开输出目录")
        self.open_folder_check.setChecked(True)
        layout.addWidget(self.open_folder_check)

        self.play_sound_check = QCheckBox("播放提示音")
        layout.addWidget(self.play_sound_check)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _connect_signals(self):
        """连接信号"""
        # 压缩模式变化
        self.mode_group.buttonClicked.connect(self._on_mode_changed)

        # 高级选项变化
        self.bitrate_combo.currentIndexChanged.connect(self._on_bitrate_changed)
        self.resolution_combo.currentIndexChanged.connect(self._on_resolution_changed)
        self.fps_combo.currentIndexChanged.connect(self._on_fps_changed)

    def _toggle_advanced(self):
        """切换高级选项显示"""
        visible = self.advanced_btn.isChecked()
        self.advanced_panel.setVisible(visible)

        if visible:
            self.advanced_btn.setText("▼ 高级选项")
        else:
            self.advanced_btn.setText("▶ 高级选项")

    def _on_mode_changed(self):
        """压缩模式变化处理"""
        mode_id = self.mode_group.checkedId()

        # 启用/禁用对应输入框
        self.ratio_spin.setEnabled(mode_id == 1)
        self.size_spin.setEnabled(mode_id == 2)

        self.settings_changed.emit()

    def _on_bitrate_changed(self, index: int):
        """码率选项变化"""
        # 最后一项是"自定义"
        is_custom = (index == self.bitrate_combo.count() - 1)
        self.custom_bitrate.setEnabled(is_custom)
        self.settings_changed.emit()

    def _on_resolution_changed(self, index: int):
        """分辨率选项变化"""
        # 最后一项是"自定义"
        is_custom = (index == self.resolution_combo.count() - 1)
        self.custom_width.setEnabled(is_custom)
        self.custom_height.setEnabled(is_custom)
        self.settings_changed.emit()

    def _on_fps_changed(self, index: int):
        """帧率选项变化"""
        # 最后一项是"自定义"
        is_custom = (index == self.fps_combo.count() - 1)
        self.custom_fps.setEnabled(is_custom)
        self.settings_changed.emit()

    def _browse_output_dir(self):
        """浏览选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.output_dir_edit.text()
        )

        if dir_path:
            self.output_dir_edit.setText(dir_path)

    def get_settings(self) -> CompressionSettings:
        """
        收集并返回压缩设置

        Returns:
            CompressionSettings 对象
        """
        settings = CompressionSettings()

        # 质量等级
        quality_id = self.quality_group.checkedId()
        quality_map = {
            0: QualityLevel.HIGH,
            1: QualityLevel.MEDIUM,
            2: QualityLevel.LOW
        }
        settings.quality_level = quality_map[quality_id]

        # 压缩模式
        mode_id = self.mode_group.checkedId()
        mode_map = {
            0: CompressionMode.QUALITY,
            1: CompressionMode.RATIO,
            2: CompressionMode.TARGET_SIZE
        }
        settings.compression_mode = mode_map[mode_id]
        settings.target_ratio = self.ratio_spin.value()
        settings.target_size_mb = self.size_spin.value()

        # 高级模式
        settings.use_advanced = self.advanced_btn.isChecked()

        if settings.use_advanced:
            # 视频码率
            bitrate_index = self.bitrate_combo.currentIndex()
            if bitrate_index == 0:  # 自动
                settings.video_bitrate = None
            elif bitrate_index == self.bitrate_combo.count() - 1:  # 自定义
                settings.video_bitrate = self.custom_bitrate.value()
            else:  # 预设值
                bitrate_text = self.bitrate_combo.currentText()
                settings.video_bitrate = int(bitrate_text.split()[0])

            # 分辨率
            res_index = self.resolution_combo.currentIndex()
            res_map = {
                0: Resolution.ORIGINAL,
                1: Resolution.P1080,
                2: Resolution.P720,
                3: Resolution.P480,
                4: Resolution.CUSTOM
            }
            settings.resolution = res_map[res_index]

            if settings.resolution == Resolution.CUSTOM:
                settings.custom_width = self.custom_width.value()
                settings.custom_height = self.custom_height.value()

            # 编码器
            codec_index = self.codec_combo.currentIndex()
            codec_map = {0: VideoCodec.H264, 1: VideoCodec.H265}
            settings.video_codec = codec_map[codec_index]

            # 帧率
            fps_index = self.fps_combo.currentIndex()
            fps_map = {
                0: FrameRate.ORIGINAL,
                1: FrameRate.FPS_24,
                2: FrameRate.FPS_30,
                3: FrameRate.FPS_60,
                4: FrameRate.CUSTOM
            }
            settings.frame_rate = fps_map[fps_index]

            if settings.frame_rate == FrameRate.CUSTOM:
                settings.custom_fps = self.custom_fps.value()

            # 音频
            settings.audio_bitrate = AUDIO_BITRATE_OPTIONS[
                self.audio_bitrate_combo.currentIndex()
            ]
            settings.keep_audio = self.keep_audio_check.isChecked()

        return settings

    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self.output_dir_edit.text()

    def get_suffix(self) -> str:
        """获取文件后缀"""
        return self.suffix_edit.text()

    def should_open_folder(self) -> bool:
        """是否打开输出目录"""
        return self.open_folder_check.isChecked()

    def should_play_sound(self) -> bool:
        """是否播放提示音"""
        return self.play_sound_check.isChecked()

    def set_enabled(self, enabled: bool):
        """设置可用状态"""
        self.setEnabled(enabled)
