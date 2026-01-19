"""
测试 presets 模块
"""

import pytest
from core.presets import (
    QualityLevel, VideoCodec, Resolution, CompressionMode,
    get_crf_for_codec, calculate_target_resolution,
    calculate_target_bitrate, get_ffmpeg_params,
    CompressionSettings
)


class TestGetCrfForCodec:
    """测试 get_crf_for_codec 函数"""

    def test_h264_high_quality(self):
        """测试 H.264 高质量"""
        crf = get_crf_for_codec(QualityLevel.HIGH, VideoCodec.H264)
        assert crf == 18

    def test_h264_medium_quality(self):
        """测试 H.264 中等质量"""
        crf = get_crf_for_codec(QualityLevel.MEDIUM, VideoCodec.H264)
        assert crf == 23

    def test_h265_quality_difference(self):
        """测试 H.265 与 H.264 的 CRF 差异"""
        h264_crf = get_crf_for_codec(QualityLevel.MEDIUM, VideoCodec.H264)
        h265_crf = get_crf_for_codec(QualityLevel.MEDIUM, VideoCodec.H265)
        assert h265_crf == h264_crf - 4


class TestCalculateTargetResolution:
    """测试 calculate_target_resolution 函数"""

    def test_original_resolution(self):
        """测试保持原始分辨率"""
        width, height = calculate_target_resolution(
            1920, 1080, Resolution.ORIGINAL
        )
        assert width == 1920
        assert height == 1080

    def test_downscale_to_720p(self):
        """测试缩小到 720p"""
        width, height = calculate_target_resolution(
            1920, 1080, Resolution.P720
        )
        assert width == 1280
        assert height == 720

    def test_no_upscale(self):
        """测试不放大"""
        width, height = calculate_target_resolution(
            640, 480, Resolution.P1080
        )
        assert width == 640
        assert height == 480

    def test_even_dimensions(self):
        """测试宽高为偶数"""
        width, height = calculate_target_resolution(
            1921, 1081, Resolution.P720
        )
        assert width % 2 == 0
        assert height % 2 == 0

    def test_custom_resolution(self):
        """测试自定义分辨率"""
        width, height = calculate_target_resolution(
            1920, 1080, Resolution.CUSTOM,
            custom_width=1000, custom_height=562
        )
        assert width == 1000
        assert height == 562


class TestCalculateTargetBitrate:
    """测试 calculate_target_bitrate 函数"""

    def test_basic_calculation(self):
        """测试基本码率计算"""
        # 目标大小: 50MB, 时长: 120秒, 音频: 192kbps
        bitrate = calculate_target_bitrate(
            50 * 1024 * 1024,  # 50MB
            120,  # 120秒
            192,  # 192kbps
            True
        )
        # 预期视频码率约 3128 kbps（含 5% 安全余量）
        assert 3000 <= bitrate <= 3200

    def test_without_audio(self):
        """测试不保留音频时的计算"""
        bitrate_with_audio = calculate_target_bitrate(
            50 * 1024 * 1024, 120, 192, True
        )
        bitrate_without_audio = calculate_target_bitrate(
            50 * 1024 * 1024, 120, 192, False
        )
        # 不保留音频时视频码率应该更高
        assert bitrate_without_audio > bitrate_with_audio

    def test_minimum_bitrate(self):
        """测试最小码率限制"""
        bitrate = calculate_target_bitrate(
            1 * 1024,  # 1KB (极小目标)
            120,
            192,
            True
        )
        assert bitrate >= 100  # 最小码率 100kbps


class TestGetFfmpegParams:
    """测试 get_ffmpeg_params 函数"""

    def test_quality_mode(self):
        """测试按质量模式"""
        settings = CompressionSettings(
            compression_mode=CompressionMode.QUALITY,
            quality_level=QualityLevel.HIGH,
            video_codec=VideoCodec.H264
        )
        params = get_ffmpeg_params(settings)

        assert params['video_codec'] == 'libx264'
        assert params['crf'] == 18
        assert params['preset'] == 'slow'

    def test_audio_settings(self):
        """测试音频设置"""
        settings = CompressionSettings(keep_audio=True, audio_bitrate=192)
        params = get_ffmpeg_params(settings)

        assert params['audio_codec'] == 'aac'
        assert params['audio_bitrate'] == '192k'

    def test_no_audio(self):
        """测试移除音频"""
        settings = CompressionSettings(keep_audio=False)
        params = get_ffmpeg_params(settings)

        assert params.get('no_audio') is True
        assert 'audio_codec' not in params
