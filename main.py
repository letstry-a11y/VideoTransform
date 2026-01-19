"""
视频压缩工具 - 程序入口
"""

import os
import sys

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 检查并添加内置 FFmpeg 路径到 PATH
ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")

# 设置 Windows DPI 感知模式 (高 DPI 支持)
if sys.platform == 'win32':
    try:
        import ctypes
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

# Qt 高 DPI 设置
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from ui.main_window import MainWindow


def main():
    """主函数"""
    # 设置 Qt 高 DPI 属性
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建应用程序
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("视频压缩工具")
    app.setOrganizationName("VideoCompressor")

    # 设置应用样式
    app.setStyle("Fusion")

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 进入事件循环
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
