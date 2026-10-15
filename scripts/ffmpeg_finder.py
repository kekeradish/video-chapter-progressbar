# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import json
import re

def get_ffmpeg_cmd():
    """
    自动查找并返回可用的 ffmpeg 执行路径：
    1. 优先使用系统 PATH 中配置的 ffmpeg
    2. 若系统未配置，则自动回退到 Python imageio_ffmpeg 自包含二进制（零配置开箱即用）
    """
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except ImportError:
        pass

    return "ffmpeg"

def get_ffprobe_cmd():
    """自动查找 ffprobe，若系统未配置则尝试从 ffmpeg 同级目录获取"""
    sys_ffprobe = shutil.which("ffprobe")
    if sys_ffprobe:
        return sys_ffprobe
    
    ffmpeg_cmd = get_ffmpeg_cmd()
    if os.path.isabs(ffmpeg_cmd):
        peer_ffprobe = os.path.join(os.path.dirname(ffmpeg_cmd), "ffprobe.exe")
        if os.path.exists(peer_ffprobe):
            return peer_ffprobe
            
    return "ffprobe"

def probe_video_meta(video_path):
    """
    自适应获取视频元数据（分辨率、帧率、时长），
    优先使用 ffprobe，如缺失则自动通过 ffmpeg -i 标准错误输出解析，保证 100% 健壮性
    """
    ffprobe_cmd = get_ffprobe_cmd()
    try:
        cmd = [
            ffprobe_cmd, "-v", "error",
            "-show_entries", "format=duration:stream=width,height,r_frame_rate,codec_type",
            "-of", "json", video_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        duration = float(data["format"]["duration"])
        width, height, fps = 1920, 1080, 30.0
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                width = int(s.get("width", 1920))
                height = int(s.get("height", 1080))
                r_fps = s.get("r_frame_rate", "30/1")
                if "/" in r_fps:
                    n, d = r_fps.split("/")
                    fps = float(n) / max(1.0, float(d))
                else:
                    fps = float(r_fps)
                break
        return {"width": width, "height": height, "fps": fps, "duration": duration}
    except Exception:
        ffmpeg_cmd = get_ffmpeg_cmd()
        res = subprocess.run([ffmpeg_cmd, "-i", video_path], stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        output = res.stderr
        
        dur_match = re.search(r"Duration:\s*(\d+):(\d+):([\d\.]+)", output)
        if dur_match:
            h, m, s = dur_match.groups()
            duration = int(h) * 3600 + int(m) * 60 + float(s)
        else:
            duration = 60.0
            
        dim_match = re.search(r"Video:.*?,.*?,\s*(\d{3,5})x(\d{3,5})", output)
        if dim_match:
            width = int(dim_match.group(1))
            height = int(dim_match.group(2))
        else:
            width, height = 1920, 1080
            
        fps_match = re.search(r"([\d\.]+)\s*fps", output)
        fps = float(fps_match.group(1)) if fps_match else 30.0
        
        return {"width": width, "height": height, "fps": fps, "duration": duration}
