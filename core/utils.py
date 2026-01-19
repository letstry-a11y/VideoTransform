"""
工具函数模块
提供文件大小格式化、时长解析、视频信息获取等工具函数
"""

import os
import json
import subprocess
import shutil
from typing import Optional, Dict, Any, List


def format_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 文件大小 (字节)

    Returns:
        格式化后的字符串,如 "1.50 MB"
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"


def format_duration(seconds: float) -> str:
    """
    格式化时长

    Args:
        seconds: 时长 (秒)

    Returns:
        格式化后的字符串,如 "01:23:45"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_duration(duration_str: str) -> float:
    """
    解析时长字符串为秒数

    Args:
        duration_str: 时长字符串,如 "01:23:45.67" 或 "83.5"

    Returns:
        秒数
    """
    try:
        # 尝试直接解析为浮点数
        return float(duration_str)
    except ValueError:
        pass

    # 解析 HH:MM:SS.mmm 格式
    parts = duration_str.split(':')
    if len(parts) == 3:
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes = float(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        return 0.0


def check_ffmpeg_installed() -> bool:
    """
    检查 FFmpeg 是否已安装

    Returns:
        True 如果 FFmpeg 可用,否则 False
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_supported_formats() -> List[str]:
    """
    获取支持的视频格式列表

    Returns:
        支持的视频格式扩展名列表
    """
    return ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v']


def is_supported_format(file_path: str) -> bool:
    """
    检查文件格式是否支持

    Args:
        file_path: 文件路径

    Returns:
        True 如果格式支持,否则 False
    """
    ext = os.path.splitext(file_path)[1].lower()
    return ext in get_supported_formats()


def get_video_info(file_path: str) -> Optional[Dict[str, Any]]:
    """
    调用 ffprobe 获取视频信息

    Args:
        file_path: 视频文件路径

    Returns:
        视频信息字典,失败返回 None
    """
    if not os.path.exists(file_path):
        return None

    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )

        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)

        # 解析格式信息
        format_info = data.get('format', {})
        streams = data.get('streams', [])

        # 查找视频流和音频流
        video_stream = None
        audio_stream = None

        for stream in streams:
            if stream.get('codec_type') == 'video' and not video_stream:
                video_stream = stream
            elif stream.get('codec_type') == 'audio' and not audio_stream:
                audio_stream = stream

        # 构建信息字典
        info = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': int(format_info.get('size', 0)),
            'duration': float(format_info.get('duration', 0)),
            'bit_rate': int(format_info.get('bit_rate', 0)),
            'format_name': format_info.get('format_name', ''),
        }

        # 视频流信息
        if video_stream:
            info['width'] = int(video_stream.get('width', 0))
            info['height'] = int(video_stream.get('height', 0))
            info['video_codec'] = video_stream.get('codec_name', '')
            info['video_bit_rate'] = int(video_stream.get('bit_rate', 0))

            # 解析帧率
            fps_str = video_stream.get('r_frame_rate', '0/1')
            if '/' in fps_str:
                num, den = fps_str.split('/')
                if int(den) != 0:
                    info['fps'] = float(num) / float(den)
                else:
                    info['fps'] = 0.0
            else:
                info['fps'] = float(fps_str)

        # 音频流信息
        if audio_stream:
            info['audio_codec'] = audio_stream.get('codec_name', '')
            info['audio_bit_rate'] = int(audio_stream.get('bit_rate', 0))
            info['sample_rate'] = int(audio_stream.get('sample_rate', 0))
            info['channels'] = int(audio_stream.get('channels', 0))

        return info

    except (subprocess.SubprocessError, json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"获取视频信息失败: {e}")
        return None


def get_output_path(
    input_path: str,
    output_dir: str,
    suffix: str
) -> str:
    """
    生成输出文件路径

    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        suffix: 文件后缀 (如 "_compressed")

    Returns:
        输出文件路径
    """
    # 获取文件名和扩展名
    file_name = os.path.basename(input_path)
    name_without_ext, ext = os.path.splitext(file_name)

    # 生成新文件名
    output_name = f"{name_without_ext}{suffix}{ext}"

    # 生成完整路径
    output_path = os.path.join(output_dir, output_name)

    return output_path


def ensure_unique_path(file_path: str) -> str:
    """
    确保路径唯一,避免覆盖现有文件

    Args:
        file_path: 文件路径

    Returns:
        唯一的文件路径
    """
    if not os.path.exists(file_path):
        return file_path

    # 分离路径和扩展名
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    name_without_ext, ext = os.path.splitext(file_name)

    # 添加序号
    counter = 1
    while True:
        new_name = f"{name_without_ext}_{counter}{ext}"
        new_path = os.path.join(dir_name, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def calculate_compression_ratio(
    original_size: int,
    compressed_size: int
) -> float:
    """
    计算压缩率 (节省百分比)

    Args:
        original_size: 原始文件大小 (字节)
        compressed_size: 压缩后文件大小 (字节)

    Returns:
        压缩率百分比 (0-100)
    """
    if original_size <= 0:
        return 0.0

    ratio = (1 - compressed_size / original_size) * 100
    return max(0.0, min(100.0, ratio))
