"""
环境测试脚本
"""

import sys
print("=" * 50)
print("视频压缩工具 - 环境检查")
print("=" * 50)
print()

# 1. Python版本
print("1. Python版本:")
print(f"   {sys.version}")
print()

# 2. PyQt5检查
print("2. PyQt5检查:")
try:
    import PyQt5
    from PyQt5.QtCore import QT_VERSION_STR
    from PyQt5.Qt import PYQT_VERSION_STR
    print(f"   ✓ PyQt5已安装")
    print(f"   Qt版本: {QT_VERSION_STR}")
    print(f"   PyQt版本: {PYQT_VERSION_STR}")
except ImportError as e:
    print(f"   ✗ PyQt5未安装: {e}")
    print("   请运行: python -m pip install PyQt5")
print()

# 3. FFmpeg检查
print("3. FFmpeg检查:")
try:
    from core.utils import check_ffmpeg_installed
    if check_ffmpeg_installed():
        print("   ✓ FFmpeg可用")
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True, text=True, timeout=5)
        first_line = result.stdout.split('\n')[0]
        print(f"   {first_line}")
    else:
        print("   ✗ FFmpeg未找到")
        print("   请配置FFmpeg:")
        print("   - 方式1: 将ffmpeg.exe和ffprobe.exe放到 ffmpeg/bin/ 目录")
        print("   - 方式2: 安装FFmpeg到系统并添加到PATH")
except Exception as e:
    print(f"   ✗ 检查失败: {e}")
print()

# 4. 模块导入测试
print("4. 核心模块测试:")
modules = [
    'core.presets',
    'core.utils',
    'core.compressor',
    'ui.file_list',
    'ui.settings',
    'ui.main_window'
]

all_ok = True
for module_name in modules:
    try:
        __import__(module_name)
        print(f"   ✓ {module_name}")
    except Exception as e:
        print(f"   ✗ {module_name}: {e}")
        all_ok = False
print()

# 总结
print("=" * 50)
if all_ok:
    print("✓ 环境检查完成，所有模块正常")
    print()
    print("可以运行程序:")
    print("  python main.py")
else:
    print("✗ 发现问题，请根据上述提示解决")
print("=" * 50)
