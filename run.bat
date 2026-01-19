@echo off
chcp 65001 >nul
echo ========================================
echo 视频压缩工具启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] 检测到Python版本:
python --version
echo.

REM 检查PyQt5是否安装
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [警告] 未安装PyQt5，正在安装依赖...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo [成功] 依赖安装完成
    echo.
)

REM 检查FFmpeg
if exist "ffmpeg\bin\ffmpeg.exe" (
    echo [信息] 检测到内置FFmpeg
) else (
    echo [警告] 未找到内置FFmpeg
    echo 请将 ffmpeg.exe 和 ffprobe.exe 放置到 ffmpeg\bin\ 目录
    echo 或确保系统已安装FFmpeg并添加到PATH
    echo.
    echo 下载地址: https://www.gyan.dev/ffmpeg/builds/
    echo.
)

REM 启动程序
echo [信息] 正在启动视频压缩工具...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    pause
)
