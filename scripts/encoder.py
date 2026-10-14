# -*- coding: utf-8 -*-
import subprocess

def start_transparent_mov_encoder(width, height, fps, output_mov_path):
    """
    启动 FFmpeg 管道，编码生成原生带 32-bit RGBA Alpha 透明通道的 QuickTime MOV
    使用 qtrle 编码器（无损且兼容剪映、PR、FCP、达芬奇）
    """
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgba",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "qtrle",
        "-r", str(fps),
        output_mov_path
    ]
    # 必须使用 stderr=subprocess.DEVNULL 避免 Windows 管道填满导致死锁
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return proc

def composite_to_final_video(video_src, mov_src, output_mp4_path):
    """
    将透明 MOV 图层无损叠加回原视频，音频 direct copy，利用硬件加速极速输出成片
    """
    cmd_nvenc = [
        "ffmpeg", "-y",
        "-i", video_src,
        "-i", mov_src,
        "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
        "-map", "[v]",
        "-map", "0:a",
        "-c:v", "h264_nvenc",
        "-preset", "p6",
        "-b:v", "22M",
        "-c:a", "copy",
        output_mp4_path
    ]
    res = subprocess.run(cmd_nvenc, capture_output=True, text=True)
    if res.returncode == 0:
        return True
    
    # 失败降级为 CPU 编码
    cmd_cpu = [
        "ffmpeg", "-y",
        "-i", video_src,
        "-i", mov_src,
        "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
        "-map", "[v]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-c:a", "copy",
        output_mp4_path
    ]
    subprocess.run(cmd_cpu, check=True)
    return True
