# -*- coding: utf-8 -*-
import os
import re
import json
import subprocess

from ffmpeg_finder import get_ffmpeg_cmd, probe_video_meta

def parse_time_str(time_str):
    """将 00:01:23.45 或 01:23 或 123 转化为浮点秒数"""
    parts = time_str.strip().replace(',', '.').split(':')
    if len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 1:
        return float(parts[0])
    return 0.0

def get_video_info(video_path):
    """获取视频的分辨率、帧率与总时长（自动适配系统与自包含 FFmpeg/FFprobe）"""
    return probe_video_meta(video_path)

def extract_audio_from_video(video_path, temp_audio_path):
    """使用 ffmpeg 从视频中抽取 16kHz 单声道音频"""
    ffmpeg_exe = get_ffmpeg_cmd()
    cmd = [
        ffmpeg_exe, "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-ar", "16000",
        "-ac", "1",
        "-q:a", "4",
        temp_audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return temp_audio_path

def transcribe_audio_whisper(audio_path, model_name="tiny", language="zh"):
    """使用本地 Whisper 快速转录音频，返回带有 start, end, text 的片段列表（可选脱机插件）"""
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path, language=language)
        result = []
        for s in segments:
            result.append({"start": s.start, "end": s.end, "text": s.text.strip()})
        return result
    except ImportError:
        pass

    try:
        import whisper
        model = whisper.load_model(model_name)
        res = model.transcribe(audio_path, language=language)
        result = []
        for s in res.get("segments", []):
            result.append({"start": float(s["start"]), "end": float(s["end"]), "text": s["text"].strip()})
        return result
    except ImportError:
        raise RuntimeError(
            "【提示】未检测到本地 Whisper 模型。\n"
            "💡 最优方案：推荐直接由 AI Agent 多模态理解视频提取章节，并通过 -c '00:00 标题1 01:20 标题2' 参数传入（秒级渲染、零依赖！）；\n"
            "💡 或在视频同目录下放置同名 .srt 字幕文件；\n"
            "💡 若确需本地离线语音听写，可单独运行：pip install faster-whisper"
        )

def parse_srt_file(srt_path):
    """解析 .srt 字幕文件提取时间戳与文本"""
    with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    pattern = re.compile(r'(\d+)\s*\n(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n(.*?)(?=\n\s*\n|\Z)', re.DOTALL)
    matches = pattern.findall(content)
    segments = []
    for m in matches:
        start = parse_time_str(m[1])
        end = parse_time_str(m[2])
        text = re.sub(r'<[^>]+>', '', m[3]).strip().replace('\n', ' ')
        if text:
            segments.append({"start": start, "end": end, "text": text})
    return segments

def parse_manual_timestamps(text_content, total_duration):
    """解析手工时间戳文本，例如: 00:00 开篇 \n 00:20 火箭筒"""
    lines = text_content.strip().splitlines()
    entries = []
    time_regex = re.compile(r'(?:(\d{1,2}:)?\d{1,2}:\d{2}(?:[\.,]\d+)?)')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = time_regex.search(line)
        if m:
            t_str = m.group(0)
            sec = parse_time_str(t_str)
            title = line.replace(t_str, '').strip(' -–—:：|[],\t')
            entries.append({"start": sec, "title": title or "未命名章节"})
    entries.sort(key=lambda x: x["start"])
    chapters = []
    for i, e in enumerate(entries):
        start = e["start"]
        end = entries[i+1]["start"] if i + 1 < len(entries) else total_duration
        chapters.append({
            "tag": f"{i+1:02d}",
            "title": e["title"],
            "start": start,
            "end": end,
            "desc": ""
        })
    return chapters
