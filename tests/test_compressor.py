"""
测试 compressor 模块
"""

import pytest
from core.compressor import CompressionResult, VideoCompressor
from core.presets import CompressionSettings, QualityLevel, VideoCodec


class TestCompressionResult:
    """测试 CompressionResult 数据类"""

    def test_success_result(self):
        """测试成功结果"""
        result = CompressionResult(
            success=True,
            input_path="/path/to/input.mp4",
            output_path="/path/to/output.mp4",
            original_size=1000000,
            compressed_size=500000
        )

        assert result.success is True
        assert result.original_size == 1000000
        assert result.compressed_size == 500000
        assert result.error_message == ""

    def test_failure_result(self):
        """测试失败结果"""
        result = CompressionResult(
            success=False,
            input_path="/path/to/input.mp4",
            output_path="/path/to/output.mp4",
            error_message="FFmpeg error"
        )

        assert result.success is False
        assert result.error_message == "FFmpeg error"


class TestVideoCompressor:
    """测试 VideoCompressor 类"""

    def test_initialization(self):
        """测试初始化"""
        compressor = VideoCompressor()

        assert compressor._process is None
        assert compressor._is_cancelled is False
        assert compressor._is_paused is False

    def test_cancel_flag(self):
        """测试取消标志"""
        compressor = VideoCompressor()

        assert compressor.is_cancelled is False
        compressor.cancel()
        assert compressor.is_cancelled is True

    def test_pause_resume(self):
        """测试暂停和恢复"""
        compressor = VideoCompressor()

        assert compressor.is_paused is False

        compressor.pause()
        assert compressor.is_paused is True

        compressor.resume()
        assert compressor.is_paused is False

    def test_build_ffmpeg_command(self):
        """测试 FFmpeg 命令构建"""
        compressor = VideoCompressor()
        settings = CompressionSettings(
            quality_level=QualityLevel.MEDIUM,
            video_codec=VideoCodec.H264,
            keep_audio=True,
            audio_bitrate=192
        )

        video_info = {
            'width': 1920,
            'height': 1080,
            'duration': 120.0,
            'video_bit_rate': 5000000
        }

        cmd = compressor._build_ffmpeg_command(
            "/input.mp4",
            "/output.mp4",
            settings,
            video_info
        )

        # 检查命令基本结构
        assert cmd[0] == 'ffmpeg'
        assert '-y' in cmd
        assert '-i' in cmd
        assert '/input.mp4' in cmd
        assert '/output.mp4' in cmd[-1]

        # 检查编码器
        assert '-c:v' in cmd
        codec_index = cmd.index('-c:v')
        assert cmd[codec_index + 1] == 'libx264'

        # 检查 CRF
        assert '-crf' in cmd

        # 检查音频
        assert '-c:a' in cmd
        assert 'aac' in cmd
        assert '-b:a' in cmd
        assert '192k' in cmd
