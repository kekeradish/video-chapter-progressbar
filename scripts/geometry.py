# -*- coding: utf-8 -*-
from PIL import ImageFont

def build_track_geometry(chapters, width, height, total_duration, preset, font_path, position=None):
    """
    根据视频分辨率、总时长、章节列表与样式配置，计算所有轨道的像素坐标与文字排版
    支持 position="top" (顶部防遮挡，适合短视频/抖音) 与 position="bottom" (底部经典长视频)
    """
    is_vertical = height > width
    
    # 优先使用传入的 position，未指定则读取 preset，默认 bottom
    pos = position or preset.get("layout", {}).get("position", "bottom")
    pos = pos.lower()
    if pos not in ["top", "bottom"]:
        pos = "bottom"

    margin_x = preset.get("margin_x", 48 if not is_vertical else 32)
    gap = preset.get("gap", 8 if not is_vertical else 6)
    bar_height = preset.get("bar_height", 14 if not is_vertical else 10)
    
    # 根据上下位置计算条带坐标
    if pos == "top":
        margin_top = 46 if not is_vertical else 58 # 避开手机顶部状态栏/前摄
        strip_height = 140
        strip_y_start = 0
        y1_local = margin_top
        y2_local = margin_top + bar_height
        text_y_offset = y2_local + (14 if not is_vertical else 10)
    else:
        margin_bottom = preset.get("margin_bottom", 22 if not is_vertical else 36)
        strip_height = preset.get("strip_height", 120 if not preset.get("show_capsule") else 180)
        strip_y_start = height - strip_height
        bar_y_bottom_local = strip_height - margin_bottom
        y1_local = bar_y_bottom_local - bar_height
        y2_local = bar_y_bottom_local
        text_y_offset = y1_local - (26 if not is_vertical else 20)

    radius = preset.get("radius", bar_height // 2)

    total_chapters = len(chapters)
    bar_total_w = width - margin_x * 2
    total_gaps = (total_chapters - 1) * gap
    available_w = max(100, bar_total_w - total_gaps)

    font_normal_size = preset.get("font_sizes", {}).get("title_normal", 20 if not is_vertical else 16)
    font_active_size = preset.get("font_sizes", {}).get("title_active", 22 if not is_vertical else 18)
    font_normal = ImageFont.truetype(font_path, font_normal_size)
    font_active = ImageFont.truetype(font_path, font_active_size)

    tracks = []
    x_off = margin_x
    for idx, ch in enumerate(chapters):
        st = ch["start"]
        et = ch["end"]
        dur = max(0.01, et - st)
        ch_w = (dur / total_duration) * available_w
        x1 = x_off
        x2 = x_off + ch_w

        title = ch["title"]
        tw_normal = font_normal.getlength(title) if hasattr(font_normal, 'getlength') else font_normal.getsize(title)[0]
        can_fit_full = (ch_w >= tw_normal + 10)
        display_title = title if can_fit_full else ch.get("tag", f"{idx+1}")
        tw_display = font_normal.getlength(display_title) if hasattr(font_normal, 'getlength') else font_normal.getsize(display_title)[0]
        
        tx = x1 + (ch_w - tw_display) / 2
        ty = text_y_offset

        tracks.append({
            "index": idx,
            "chapter": ch,
            "x1": x1, "x2": x2,
            "y1": y1_local, "y2": y2_local,
            "w": ch_w,
            "dur": dur,
            "display_title": display_title,
            "full_title": title,
            "can_fit_full": can_fit_full,
            "tx": tx,
            "ty": ty
        })
        x_off = x2 + gap

    return {
        "width": width,
        "height": height,
        "position": pos,
        "is_vertical": is_vertical,
        "strip_height": strip_height,
        "strip_y_start": strip_y_start,
        "bar_height": bar_height,
        "radius": radius,
        "margin_x": margin_x,
        "tracks": tracks
    }
