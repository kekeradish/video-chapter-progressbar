# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import argparse

cur_dir = os.path.dirname(os.path.abspath(__file__))
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from transcribe import get_video_info, extract_audio_from_video, transcribe_audio_whisper, parse_srt_file, parse_manual_timestamps
from chapter_segmenter import segment_by_keywords
from geometry import build_track_geometry
from renderer import StripRenderer
from encoder import start_transparent_mov_encoder, composite_to_final_video

def run_progressbar_pipeline(
    video_path,
    srt_path=None,
    manual_chapters=None,
    preset_name="minimal_bottom",
    position="auto",
    mascot_path=None,
    output_mov=None,
    output_mp4=None,
    composite=False,
    target_chapters=None,
    font_path=r"C:\Windows\Fonts\msyhbd.ttc",
    progress_callback=None
):
    print("=" * 60, flush=True)
    print("【Video Chapter Progress Bar 自动化流水线启动】", flush=True)
    print(f"输入视频: {video_path}", flush=True)

    info = get_video_info(video_path)
    width, height = info["width"], info["height"]
    fps = info["fps"]
    duration = info["duration"]
    print(f"视频信息: 分辨率 {width}x{height} | 帧率 {fps:.1f} fps | 时长 {duration:.2f}s", flush=True)

    video_dir = os.path.dirname(os.path.abspath(video_path))
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # 智能推断 1: 自动判断横竖屏与布局位置 (Top/Bottom)
    if not position or position == "auto":
        if height > width:
            position = "top"
            print("💡 智能感知: 检测到竖屏视频 (9:16)，自动推荐并启用【顶部防遮挡布局】！", flush=True)
        else:
            position = "bottom"
            print("💡 智能感知: 检测到横屏视频 (16:9)，自动启用【底部经典沉浸布局】！", flush=True)

    # 智能推断 2: 自动寻找同级目录同名字幕文件
    if not manual_chapters and not srt_path:
        auto_srt = os.path.join(video_dir, f"{video_name}.srt")
        if os.path.exists(auto_srt):
            srt_path = auto_srt
            print(f"💡 智能感知: 自动挂载同级同名字幕文件 -> {srt_path}", flush=True)

    # 智能推断 3: 自动寻找同级目录 IP 角色图片
    if not mascot_path:
        for possible_mascot in ["mascot.png", "avatar.png", "ip.png", f"{video_name}_mascot.png"]:
            cand = os.path.join(video_dir, possible_mascot)
            if os.path.exists(cand):
                mascot_path = cand
                print(f"💡 智能感知: 自动识别到 IP 随动角色素材 -> {mascot_path}", flush=True)
                break

    pos_tag = f"_{position}" if position == "top" else ""
    if not output_mov:
        output_mov = os.path.join(video_dir, f"{video_name}_{preset_name}{pos_tag}_透明素材.mov")
    if not output_mp4:
        output_mp4 = os.path.join(video_dir, f"{video_name}_{preset_name}{pos_tag}_带进度条.mp4")

    # 章节数据获取
    chapters = []
    if manual_chapters:
        print("模式: 显式手工/Agent 语义章节解析...", flush=True)
        chapters = parse_manual_timestamps(manual_chapters, duration)
    elif srt_path and os.path.exists(srt_path):
        print(f"模式: 读取外挂字幕文件 ({srt_path})...", flush=True)
        segs = parse_srt_file(srt_path)
        chapters = segment_by_keywords(segs, duration, target_chapters)
    else:
        print("模式: AI 语音转录与自动语义切分...", flush=True)
        temp_audio = os.path.join(video_dir, f"__temp_audio_{video_name}.mp3")
        try:
            print(" -> 正在提取轻量音频流...", flush=True)
            extract_audio_from_video(video_path, temp_audio)
            print(" -> 正在执行 Whisper 毫秒级语音转录...", flush=True)
            segs = transcribe_audio_whisper(temp_audio, model_name="tiny", language="zh")
            print(f" -> 语音识别完成，共识别 {len(segs)} 条语句，正在进行语义章节聚类...", flush=True)
            chapters = segment_by_keywords(segs, duration, target_chapters)
        finally:
            if os.path.exists(temp_audio):
                try: os.remove(temp_audio)
                except: pass

    print(f"\n【已提取章节目录】(共 {len(chapters)} 个章节):", flush=True)
    print("-" * 60, flush=True)
    for c in chapters:
        print(f"  [{c['start']:06.2f}s -> {c['end']:06.2f}s] 【{c.get('tag','00')}】{c['title']}  {c.get('desc','')}", flush=True)
    print("-" * 60, flush=True)

    preset_dir = os.path.join(os.path.dirname(cur_dir), "presets")
    preset_file = os.path.join(preset_dir, f"{preset_name}.json")
    if not os.path.exists(preset_file):
        preset_file = os.path.join(preset_dir, "minimal_bottom.json")
    with open(preset_file, "r", encoding="utf-8") as pf:
        preset = json.load(pf)
    print(f"应用样式预设: {preset.get('name', preset_name)} | 位置: 【{'顶部 (TOP)' if position == 'top' else '底部 (BOTTOM)'}】", flush=True)
    if mascot_path:
        print(f"加载自定义吉祥物/IP角色: {mascot_path}", flush=True)

    # 4. 空间几何参数建模 (传递 position)
    geo = build_track_geometry(chapters, width, height, duration, preset, font_path, position=position)

    # 5. 启动透明 MOV 流式渲染引擎
    total_frames = int(duration * fps)
    print(f"\n开始渲染透明通道视频 (总帧数: {total_frames} 帧)...", flush=True)
    
    renderer = StripRenderer(geo, preset, font_path, mascot_path=mascot_path)
    proc = start_transparent_mov_encoder(width, height, fps, output_mov)

    start_t = time.time()
    for f_idx in range(total_frames):
        cur_t = f_idx / fps
        frame_bytes = renderer.render_frame_bytes(cur_t, duration)
        proc.stdin.write(frame_bytes)

        if f_idx % 500 == 0 or f_idx == total_frames - 1:
            elapsed = time.time() - start_t
            speed = (f_idx + 1) / max(0.001, elapsed)
            pct = (f_idx + 1) / total_frames * 100
            print(f"渲染进度: {f_idx+1}/{total_frames} ({pct:.1f}%) | 速度: {speed:.1f} fps", flush=True)

    proc.stdin.close()
    proc.wait()
    print(f"\n[OK] 透明通道素材已生成: {output_mov}", flush=True)

    if composite:
        print("\n正在自动合成原画成品视频...", flush=True)
        composite_to_final_video(video_path, output_mov, output_mp4)
        print(f"[OK] 原画成品视频已输出: {output_mp4}", flush=True)

    print("=" * 60, flush=True)
    print("【处理完成！素材已就绪】\n", flush=True)
    return {
        "chapters": chapters,
        "mov_path": output_mov,
        "mp4_path": output_mp4 if composite else None
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动视频分段动态进度条生成工具")
    parser.add_argument("-i", "--input", required=True, help="输入视频路径")
    parser.add_argument("-s", "--srt", default=None, help="外挂字幕文件路径 (.srt)")
    parser.add_argument("-c", "--chapters", default=None, help="手工章节文本")
    parser.add_argument("-p", "--preset", default="minimal_bottom", help="预设主题")
    parser.add_argument("-pos", "--position", default="auto", choices=["auto", "bottom", "top"], help="显示位置: auto(智能推断横竖屏), bottom(底部), top(顶部)")
    parser.add_argument("-m", "--mascot", default=None, help="自定义吉祥物/IP透明PNG图片路径")
    parser.add_argument("-n", "--num_chapters", type=int, default=None, help="期望目标章节数")
    parser.add_argument("-o", "--output_mov", default=None, help="输出透明MOV路径")
    parser.add_argument("--composite", action="store_true", help="是否直接合成出原画MP4")
    args = parser.parse_args()

    run_progressbar_pipeline(
        video_path=args.input,
        srt_path=args.srt,
        manual_chapters=args.chapters,
        preset_name=args.preset,
        position=args.position,
        mascot_path=args.mascot,
        output_mov=args.output_mov,
        composite=args.composite,
        target_chapters=args.num_chapters
    )
