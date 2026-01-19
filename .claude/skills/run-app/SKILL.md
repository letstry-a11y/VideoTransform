---
name: run-app
description: 运行视频压缩工具程序。当需要启动程序、运行 Python 脚本、测试应用时使用此 skill。
allowed-tools: Bash, Read
---

# 运行视频压缩工具

## 环境配置

- **Python 环境**: `D:\Anaconda\envs\script_dev`
- **Python 可执行文件**: `D:\Anaconda\envs\script_dev\python.exe`
- **FFmpeg 路径**: `D:\ffmpeg-master\bin`

## 运行命令

启动主程序：

```bash
"D:/Anaconda/envs/script_dev/python.exe" "D:/ai demo/VTransform/VideoTransform/main.py"
```

## 常用操作

| 操作 | 命令 |
|------|------|
| 运行主程序 | `"D:/Anaconda/envs/script_dev/python.exe" main.py` |
| 检查 Python 版本 | `"D:/Anaconda/envs/script_dev/python.exe" --version` |
| 安装依赖 | `"D:/Anaconda/envs/script_dev/python.exe" -m pip install -r requirements.txt` |
| 检查 PyQt5 | `"D:/Anaconda/envs/script_dev/python.exe" -c "import PyQt5; print('OK')"` |
