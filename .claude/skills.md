# VideoTransform 项目 Skills

本项目使用 Python 环境: `D:/Anaconda/envs/script_dev`
FFmpeg 路径: `D:/ffmpeg-master/bin`

## /run

启动视频压缩工具应用程序

```bash
"D:/Anaconda/envs/script_dev/python.exe" main.py
```

## /test

运行所有测试用例

```bash
"D:/Anaconda/envs/script_dev/python.exe" -m pytest tests/ -v
```

## /test-unit

运行单个测试文件（需要指定文件名）

```bash
"D:/Anaconda/envs/script_dev/python.exe" -m pytest tests/$ARGUMENTS -v
```

## /install

安装项目依赖

```bash
"D:/Anaconda/envs/script_dev/python.exe" -m pip install -r requirements.txt
```

## /check-env

检查开发环境和依赖状态

```bash
"D:/Anaconda/envs/script_dev/python.exe" test_env.py
```

## /lint

检查代码风格（需要安装 flake8）

```bash
"D:/Anaconda/envs/script_dev/python.exe" -m flake8 core/ ui/ main.py --max-line-length=120
```

## /format

格式化代码（需要安装 black）

```bash
"D:/Anaconda/envs/script_dev/python.exe" -m black core/ ui/ main.py
```

## /build

使用 PyInstaller 打包应用程序（需要安装 pyinstaller）

```bash
"D:/Anaconda/envs/script_dev/python.exe" -m PyInstaller --onefile --windowed --name VideoCompressor main.py
```

## /ffmpeg-check

检查 FFmpeg 是否可用

```bash
"D:/ffmpeg-master/bin/ffmpeg.exe" -version
```

## /clean

清理 Python 缓存文件

```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; find . -name "*.pyc" -delete 2>/dev/null; find . -name "*.pyo" -delete 2>/dev/null; echo "Cache cleaned"
```
