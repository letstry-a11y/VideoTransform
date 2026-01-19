# 更新日志

## [2026-01-19] 环境配置与编码修复

### 新增
- **Claude Code Skill 配置**: 添加 `.claude/skills/run-app/SKILL.md`，配置项目运行环境
- **运行配置文档**: 添加 `skills.md` 记录项目运行配置信息

### 修改

#### main.py
- **FFmpeg 路径配置优化**: 支持内置路径和外部路径双重检测
  - 优先使用项目内置 `ffmpeg/bin` 目录
  - 备选使用外部路径 `D:\ffmpeg-master\bin`

```python
# 修改前
ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")

# 修改后
ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
if not os.path.exists(ffmpeg_path):
    ffmpeg_path = r"D:\ffmpeg-master\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")
```

#### core/utils.py
- **修复 GBK 编码错误**: 为 subprocess 调用添加 UTF-8 编码支持

`check_ffmpeg_installed()` 函数 (第92-97行):
```python
# 修改前
result = subprocess.run(
    ['ffmpeg', '-version'],
    capture_output=True,
    text=True,
    timeout=5
)

# 修改后
result = subprocess.run(
    ['ffmpeg', '-version'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='ignore',
    timeout=5
)
```

`get_video_info()` 函数 (第150-155行):
```python
# 修改前
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=30
)

# 修改后
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='ignore',
    timeout=30
)
```

#### run.bat
- **指定 Python 环境**: 使用 Anaconda 环境 `D:\Anaconda\envs\script_dev`
- **简化启动流程**: 移除冗余检查，直接使用指定环境运行

### 修复
- 修复 Windows 下 subprocess 输出的 GBK 编码解码错误 (`UnicodeDecodeError: 'gbk' codec can't decode byte`)

### 环境配置
- **Python 环境**: `D:\Anaconda\envs\script_dev`
- **FFmpeg 路径**: `D:\ffmpeg-master\bin`
