"""
预设配置模块
定义压缩质量等级、编码器、分辨率等预设参数
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple


class QualityLevel(Enum):
    """质量等级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VideoCodec(Enum):
    """视频编码器枚举"""
    H264 = "libx264"
    H265 = "libx265"


class Resolution(Enum):
    """分辨率预设枚举"""
    ORIGINAL = "original"
    P1080 = "1080p"
    P720 = "720p"
    P480 = "480p"
    CUSTOM = "custom"


class FrameRate(Enum):
    """帧率预设枚举"""
    ORIGINAL = "original"
    FPS_24 = 24
    FPS_30 = 30
    FPS_60 = 60
    CUSTOM = "custom"


class CompressionMode(Enum):
    """压缩模式枚举"""
    QUALITY = "quality"        # 按质量压缩 (CRF)
    RATIO = "ratio"            # 按比例压缩
    TARGET_SIZE = "target_size"  # 按目标大小压缩


@dataclass
class CompressionSettings:
    """压缩设置数据类"""
    # 质量等级
    quality_level: QualityLevel = QualityLevel.MEDIUM

    # 视频参数
    video_codec: VideoCodec = VideoCodec.H264
    video_bitrate: Optional[int] = None  # kbps, None 表示自动

    # 分辨率
    resolution: Resolution = Resolution.ORIGINAL
    custom_width: Optional[int] = None
    custom_height: Optional[int] = None

    # 帧率
    frame_rate: FrameRate = FrameRate.ORIGINAL
    custom_fps: Optional[int] = None

    # 音频参数
    audio_bitrate: int = 192  # kbps
    keep_audio: bool = True

    # 高级模式
    use_advanced: bool = False

    # 压缩模式
    compression_mode: CompressionMode = CompressionMode.QUALITY
    target_ratio: int = 50  # 百分比 (5-95%)
    target_size_mb: float = 0  # MB


# 质量预设常量
QUALITY_PRESETS = {
    QualityLevel.HIGH: {
        'crf': 18,
        'preset': 'slow',
        'description': '高质量 - 视觉无损,适合存档',
        'estimated_ratio': '30-50%',
    },
    QualityLevel.MEDIUM: {
        'crf': 23,
        'preset': 'medium',
        'description': '中等质量 - 平衡质量与大小',
        'estimated_ratio': '50-70%',
    },
    QualityLevel.LOW: {
        'crf': 28,
        'preset': 'fast',
        'description': '低质量 - 最小体积,适合分享',
        'estimated_ratio': '70-90%',
    },
}

# 分辨率映射 (宽, 高)
RESOLUTION_MAP = {
    Resolution.P1080: (1920, 1080),
    Resolution.P720: (1280, 720),
    Resolution.P480: (854, 480),
}

# 音频码率选项 (kbps)
AUDIO_BITRATE_OPTIONS = [64, 128, 192, 256, 320]


def get_crf_for_codec(quality: QualityLevel, codec: VideoCodec) -> int:
    """
    根据编码器调整 CRF 值
    H.265 的 CRF 比 H.264 低 4 可获得相似质量

    Args:
        quality: 质量等级
        codec: 视频编码器

    Returns:
        CRF 值
    """
    base_crf = QUALITY_PRESETS[quality]['crf']

    if codec == VideoCodec.H265:
        # H.265 在相同质量下可以使用更低的 CRF
        return base_crf - 4

    return base_crf


def calculate_target_resolution(
    original_width: int,
    original_height: int,
    target: Resolution,
    custom_width: Optional[int] = None,
    custom_height: Optional[int] = None
) -> Tuple[int, int]:
    """
    计算目标分辨率,保持宽高比,不放大

    Args:
        original_width: 原始宽度
        original_height: 原始高度
        target: 目标分辨率预设
        custom_width: 自定义宽度
        custom_height: 自定义高度

    Returns:
        (宽度, 高度) 元组,保证为偶数
    """
    # 保持原始分辨率
    if target == Resolution.ORIGINAL:
        return (original_width, original_height)

    # 自定义分辨率
    if target == Resolution.CUSTOM and custom_width and custom_height:
        # 确保宽高为偶数
        width = custom_width - (custom_width % 2)
        height = custom_height - (custom_height % 2)
        return (width, height)

    # 预设分辨率
    target_width, target_height = RESOLUTION_MAP[target]

    # 不放大 - 如果原始尺寸小于目标,保持原始
    if original_width <= target_width and original_height <= target_height:
        return (original_width, original_height)

    # 计算缩放比例,取较小值以保持宽高比
    scale_w = target_width / original_width
    scale_h = target_height / original_height
    scale = min(scale_w, scale_h)

    # 计算新尺寸并确保为偶数
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    # 确保宽高为偶数 (编码器要求)
    new_width = new_width - (new_width % 2)
    new_height = new_height - (new_height % 2)

    return (new_width, new_height)


def calculate_target_bitrate(
    target_size_bytes: int,
    duration_seconds: float,
    audio_bitrate_kbps: int,
    keep_audio: bool
) -> int:
    """
    根据目标文件大小计算视频码率

    公式:
        total_bits = target_size * 8 * safety_factor
        audio_bits = audio_bitrate * 1000 * duration
        video_bits = total_bits - audio_bits
        video_bitrate = video_bits / duration / 1000

    Args:
        target_size_bytes: 目标文件大小 (字节)
        duration_seconds: 视频时长 (秒)
        audio_bitrate_kbps: 音频码率 (kbps)
        keep_audio: 是否保留音频

    Returns:
        视频码率 (kbps)
    """
    if duration_seconds <= 0:
        return 2000  # 默认码率

    # 安全系数：预留 5% 余量用于容器开销和编码误差
    safety_factor = 0.95

    # 总比特数（考虑安全系数）
    total_bits = target_size_bytes * 8 * safety_factor

    # 音频比特数
    audio_bits = 0
    if keep_audio:
        audio_bits = audio_bitrate_kbps * 1000 * duration_seconds

    # 视频比特数
    video_bits = total_bits - audio_bits

    # 如果视频比特数为负，说明目标大小太小，无法容纳音频
    if video_bits <= 0:
        video_bits = target_size_bytes * 8 * safety_factor * 0.8  # 分配 80% 给视频

    # 视频码率 (kbps)
    video_bitrate = video_bits / duration_seconds / 1000

    # 限制码率范围
    video_bitrate = max(100, min(50000, video_bitrate))

    return int(video_bitrate)


def get_ffmpeg_params(
    settings: CompressionSettings,
    video_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    根据设置生成 FFmpeg 参数字典

    Args:
        settings: 压缩设置
        video_info: 视频信息字典 (可选)

    Returns:
        FFmpeg 参数字典
    """
    params = {}

    # 视频编码器
    params['video_codec'] = settings.video_codec.value

    # 根据压缩模式设置参数
    if settings.compression_mode == CompressionMode.QUALITY:
        # 按质量压缩 - 使用 CRF
        crf = get_crf_for_codec(settings.quality_level, settings.video_codec)
        params['crf'] = crf
        params['preset'] = QUALITY_PRESETS[settings.quality_level]['preset']

    elif settings.compression_mode == CompressionMode.TARGET_SIZE and video_info:
        # 按目标大小压缩 - 计算码率
        target_size_bytes = int(settings.target_size_mb * 1024 * 1024)
        duration = video_info.get('duration', 0)
        video_bitrate = calculate_target_bitrate(
            target_size_bytes,
            duration,
            settings.audio_bitrate,
            settings.keep_audio
        )
        params['video_bitrate'] = f"{video_bitrate}k"
        params['preset'] = 'medium'

    elif settings.compression_mode == CompressionMode.RATIO and video_info:
        # 按比例压缩 - 根据原始文件大小计算目标大小，再计算码率
        original_size = video_info.get('file_size', 0)
        duration = video_info.get('duration', 0)

        if original_size > 0 and duration > 0:
            # 计算目标文件大小
            target_size_bytes = int(original_size * settings.target_ratio / 100)
            # 使用统一的码率计算函数
            video_bitrate = calculate_target_bitrate(
                target_size_bytes,
                duration,
                settings.audio_bitrate,
                settings.keep_audio
            )
            params['video_bitrate'] = f"{video_bitrate}k"
        else:
            # 没有文件大小或时长信息，使用 CRF
            crf = get_crf_for_codec(settings.quality_level, settings.video_codec)
            params['crf'] = crf
        params['preset'] = 'medium'

    # 高级选项
    if settings.use_advanced:
        # 视频码率 (覆盖前面的设置)
        if settings.video_bitrate:
            params['video_bitrate'] = f"{settings.video_bitrate}k"

        # 分辨率
        if settings.resolution != Resolution.ORIGINAL and video_info:
            original_w = video_info.get('width', 1920)
            original_h = video_info.get('height', 1080)
            new_w, new_h = calculate_target_resolution(
                original_w,
                original_h,
                settings.resolution,
                settings.custom_width,
                settings.custom_height
            )
            if (new_w, new_h) != (original_w, original_h):
                params['scale'] = f"{new_w}:{new_h}"

        # 帧率
        if settings.frame_rate == FrameRate.CUSTOM and settings.custom_fps:
            params['fps'] = settings.custom_fps
        elif settings.frame_rate != FrameRate.ORIGINAL:
            params['fps'] = settings.frame_rate.value

    # 音频
    if settings.keep_audio:
        params['audio_codec'] = 'aac'
        params['audio_bitrate'] = f"{settings.audio_bitrate}k"
    else:
        params['no_audio'] = True

    return params
