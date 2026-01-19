@echo off
chcp 65001 >nul

REM 设置 Anaconda 环境路径
set PYTHON_EXE=D:\Anaconda\envs\script_dev\python.exe

echo ========================================
echo 视频压缩工具启动脚本
echo ========================================
echo.

REM 检查Python是否存在
if not exist "%PYTHON_EXE%" (
    echo [错误] 未找到Python环境: %PYTHON_EXE%
    pause
    exit /b 1
)

echo [信息] 使用Python环境: %PYTHON_EXE%
"%PYTHON_EXE%" --version
echo.

REM 检查FFmpeg
if exist "ffmpeg\bin\ffmpeg.exe" (
    echo [信息] 检测到内置FFmpeg
) else (
    echo [信息] 使用外部FFmpeg: D:\ffmpeg-master\bin
    echo.
)

REM 启动程序
echo [信息] 正在启动视频压缩工具...
echo.
"%PYTHON_EXE%" main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    pause
)
