# 视频压缩工具

一款基于 PyQt5 图形界面的桌面视频压缩工具,使用 FFmpeg 作为底层编码引擎,支持批量视频压缩、多种压缩模式和丰富的编码参数配置。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 功能特性

### 文件管理
- 支持拖拽添加视频文件
- 支持对话框多选文件
- 支持格式: MP4, MOV, AVI, MKV, WMV, FLV, WEBM, M4V
- 显示文件大小、时长和压缩状态
- 批量文件处理

### 压缩设置

#### 简单模式
- 三档质量等级: 高质量、中等质量、低质量
- 三种压缩模式:
  - **按质量**: 使用 CRF 恒定质量因子
  - **按比例**: 压缩到原始大小的指定百分比
  - **按大小**: 压缩到指定的目标文件大小

#### 高级模式
- 视频编码器: H.264 (libx264)、H.265 (libx265)
- 视频码率: 自动或自定义 (100-50000 kbps)
- 分辨率: 保持原始、1080p、720p、480p、自定义
- 帧率: 保持原始、24fps、30fps、60fps、自定义
- 音频设置: 码率选择 (64-320 kbps)、可选择移除音频

### 其他功能
- 实时进度显示
- 批量压缩
- 取消压缩
- 压缩完成后自动打开输出目录
- 压缩结果统计 (压缩率、节省空间)

## 系统要求

- **操作系统**: Windows 10/11 (主要)、macOS、Linux
- **Python 版本**: Python 3.8+
- **依赖组件**: FFmpeg

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/video-compressor.git
cd video-compressor
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 FFmpeg

#### 方式一: 内置 FFmpeg (推荐)

将 FFmpeg 可执行文件放置在项目的 `ffmpeg/bin/` 目录下:

**Windows**:
- 下载 FFmpeg: https://www.gyan.dev/ffmpeg/builds/
- 解压后,将 `ffmpeg.exe` 和 `ffprobe.exe` 复制到 `ffmpeg/bin/` 目录

**macOS**:
```bash
brew install ffmpeg
```
然后将 `/usr/local/bin/ffmpeg` 和 `/usr/local/bin/ffprobe` 复制到 `ffmpeg/bin/`

**Linux**:
```bash
sudo apt install ffmpeg
```
然后将 `/usr/bin/ffmpeg` 和 `/usr/bin/ffprobe` 复制到 `ffmpeg/bin/`

#### 方式二: 使用系统 FFmpeg

确保 FFmpeg 已添加到系统 PATH 环境变量。

**验证安装**:
```bash
ffmpeg -version
ffprobe -version
```

## 使用方法

### 启动程序

```bash
python main.py
```

### 基本操作流程

1. **添加视频文件**
   - 拖拽视频文件到拖拽区域
   - 或点击"选择文件"按钮

2. **设置压缩参数**
   - 选择质量等级 (高/中/低)
   - 选择压缩模式 (按质量/按比例/按大小)
   - (可选) 展开高级选项进行详细设置

3. **配置输出**
   - 设置输出目录
   - 设置文件后缀 (默认 `_compressed`)

4. **开始压缩**
   - 点击"开始压缩"按钮
   - 观察实时进度
   - 等待压缩完成

5. **查看结果**
   - 自动打开输出目录
   - 查看压缩结果统计

## 项目结构

```
video_compressor/
├── main.py                 # 程序入口
├── requirements.txt        # Python 依赖
├── core/                   # 核心业务逻辑
│   ├── __init__.py
│   ├── compressor.py       # 压缩器
│   ├── presets.py          # 预设配置
│   └── utils.py            # 工具函数
├── ui/                     # 用户界面
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   ├── file_list.py        # 文件列表组件
│   └── settings.py         # 设置面板组件
├── tests/                  # 测试代码
│   ├── __init__.py
│   ├── test_presets.py
│   ├── test_utils.py
│   └── test_compressor.py
├── ffmpeg/                 # FFmpeg 存放目录
│   └── bin/
│       ├── ffmpeg.exe
│       └── ffprobe.exe
└── README.md
```

## 运行测试

```bash
pytest tests/
```

## 技术栈

- **GUI 框架**: PyQt5
- **编程语言**: Python 3.8+
- **视频处理**: FFmpeg / FFprobe
- **测试框架**: pytest

## 常见问题

### Q: 提示 "FFmpeg 未找到" 怎么办?

A: 请确保:
1. FFmpeg 已正确安装
2. 如果使用内置 FFmpeg,检查 `ffmpeg/bin/` 目录是否包含可执行文件
3. 如果使用系统 FFmpeg,确保已添加到 PATH 环境变量

### Q: 支持哪些视频格式?

A: 支持 MP4, MOV, AVI, MKV, WMV, FLV, WEBM, M4V 等常见格式。

### Q: H.265 和 H.264 有什么区别?

A: H.265 (HEVC) 在相同质量下文件更小,但编码速度较慢。一般情况下推荐使用 H.264。

### Q: 压缩率能达到多少?

A: 根据质量等级和原始视频不同:
- 高质量: 节省 30-50% 空间
- 中等质量: 节省 50-70% 空间
- 低质量: 节省 70-90% 空间

### Q: 可以同时压缩多个文件吗?

A: 可以批量添加多个文件,程序会串行处理 (一个接一个压缩)。

## 贡献

欢迎提交 Issue 和 Pull Request!

## 许可证

MIT License

## 致谢

- [FFmpeg](https://ffmpeg.org/) - 强大的音视频处理工具
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - 优秀的 Python GUI 框架

## 联系方式

- 项目主页: https://github.com/yourusername/video-compressor
- 问题反馈: https://github.com/yourusername/video-compressor/issues
