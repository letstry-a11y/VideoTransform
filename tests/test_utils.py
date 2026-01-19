"""
测试 utils 模块
"""

import pytest
from core.utils import (
    format_size, format_duration, parse_duration,
    get_supported_formats, is_supported_format,
    calculate_compression_ratio
)


class TestFormatSize:
    """测试 format_size 函数"""

    def test_bytes(self):
        """测试字节格式化"""
        assert format_size(512) == "512 B"

    def test_kilobytes(self):
        """测试 KB 格式化"""
        assert format_size(1024) == "1.00 KB"
        assert format_size(2048) == "2.00 KB"

    def test_megabytes(self):
        """测试 MB 格式化"""
        assert format_size(1024 * 1024) == "1.00 MB"
        assert format_size(1536 * 1024) == "1.50 MB"

    def test_gigabytes(self):
        """测试 GB 格式化"""
        assert format_size(1024 * 1024 * 1024) == "1.00 GB"
        assert format_size(2 * 1024 * 1024 * 1024) == "2.00 GB"


class TestFormatDuration:
    """测试 format_duration 函数"""

    def test_seconds_only(self):
        """测试仅秒数"""
        assert format_duration(45) == "00:00:45"

    def test_minutes(self):
        """测试分钟"""
        assert format_duration(125) == "00:02:05"

    def test_hours(self):
        """测试小时"""
        assert format_duration(3665) == "01:01:05"

    def test_long_duration(self):
        """测试长时长"""
        assert format_duration(7384) == "02:03:04"


class TestParseDuration:
    """测试 parse_duration 函数"""

    def test_float_string(self):
        """测试浮点数字符串"""
        assert parse_duration("83.5") == 83.5

    def test_hms_format(self):
        """测试 HH:MM:SS 格式"""
        assert parse_duration("01:23:45") == 5025.0

    def test_hms_with_milliseconds(self):
        """测试 HH:MM:SS.mmm 格式"""
        result = parse_duration("01:23:45.67")
        assert 5025.6 <= result <= 5025.7

    def test_ms_format(self):
        """测试 MM:SS 格式"""
        assert parse_duration("12:34") == 754.0


class TestSupportedFormats:
    """测试支持的格式"""

    def test_get_supported_formats(self):
        """测试获取支持格式列表"""
        formats = get_supported_formats()
        assert '.mp4' in formats
        assert '.mov' in formats
        assert '.avi' in formats
        assert '.mkv' in formats

    def test_is_supported_format_mp4(self):
        """测试 MP4 格式支持"""
        assert is_supported_format("video.mp4") is True
        assert is_supported_format("VIDEO.MP4") is True

    def test_is_supported_format_unsupported(self):
        """测试不支持的格式"""
        assert is_supported_format("video.txt") is False
        assert is_supported_format("video.doc") is False


class TestCalculateCompressionRatio:
    """测试 calculate_compression_ratio 函数"""

    def test_70_percent_compression(self):
        """测试 70% 压缩率"""
        ratio = calculate_compression_ratio(100, 30)
        assert ratio == 70.0

    def test_50_percent_compression(self):
        """测试 50% 压缩率"""
        ratio = calculate_compression_ratio(1000, 500)
        assert ratio == 50.0

    def test_no_compression(self):
        """测试无压缩"""
        ratio = calculate_compression_ratio(100, 100)
        assert ratio == 0.0

    def test_zero_original_size(self):
        """测试原始大小为零"""
        ratio = calculate_compression_ratio(0, 50)
        assert ratio == 0.0
